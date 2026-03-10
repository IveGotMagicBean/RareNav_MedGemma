"""Chat API — with SSE streaming + Agent tool display"""
from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
import time
import re
import json

chat_bp = Blueprint("chat", __name__)
sessions = {}

SYMPTOM_KEYWORDS = [
    'symptom','pain','fatigue','weakness','fever','cough','breath','swelling',
    'vision','hearing','seizure','tremor','rash','bleeding','vomiting','nausea',
    'muscle','joint','liver','kidney','heart','lung','brain','nerve','bone',
    'presents with','complains of','history of','suffering from','diagnosed'
]
GENE_PATTERN = re.compile(r'\b([A-Z][A-Z0-9]{1,9})\b')
VARIANT_PATTERN = re.compile(r'c\.\d+|p\.[A-Z]|rs\d{5,}', re.IGNORECASE)
SKIP_WORDS = {'I','A','OR','AND','THE','FOR','DNA','RNA','PCR','MRI','CT','AI','US','NO','MY','IS'}

def detect_intent(message):
    msg_lower = message.lower()
    has_symptoms = any(k in msg_lower for k in SYMPTOM_KEYWORDS)
    genes = [g for g in GENE_PATTERN.findall(message) if g not in SKIP_WORDS and len(g) >= 2]
    has_variant = bool(VARIANT_PATTERN.search(message))
    is_diagnostic = any(w in msg_lower for w in [
        'diagnos','what disease','what condition','could this be',
        'differential','rare disease','genetic','hereditary','syndrome','mutation','variant'
    ])
    return {
        'has_symptoms': has_symptoms,
        'genes': list(set(genes[:3])),
        'has_variant': has_variant,
        'is_diagnostic': is_diagnostic,
        'needs_agent': has_symptoms or has_variant or is_diagnostic or len(genes) > 0
    }

def run_agent_enrichment(message, intent, clinvar, hpo):
    trace = []
    enrichment = []
    if clinvar and intent['genes']:
        for gene in intent['genes'][:2]:
            try:
                records = clinvar.search_by_gene(gene, limit=3)
                if records:
                    top = records[0]
                    sig = top.get('significance', '')
                    condition = (top.get('phenotype') or '').split('|')[0].strip()
                    enrichment.append(
                        f"[ClinVar] {gene}: top variant significance = {sig}"
                        + (f", associated with {condition}" if condition else "")
                    )
                    trace.append({'step':'clinvar','label':f'ClinVar → {gene}','detail':f'{len(records)} record(s) · {sig}','status':'ok'})
                else:
                    trace.append({'step':'clinvar','label':f'ClinVar → {gene}','detail':'No records found','status':'empty'})
            except Exception as e:
                trace.append({'step':'clinvar','label':f'ClinVar → {gene}','detail':str(e)[:60],'status':'error'})
    if hpo and intent['has_symptoms']:
        symptom_words = [w for w in SYMPTOM_KEYWORDS if w in message.lower()]
        if symptom_words:
            try:
                mapped = hpo.map_symptoms(symptom_words)
                terms = mapped.get('mapped', [])
                if terms:
                    term_str = ', '.join(t.get('term','') for t in terms[:5])
                    enrichment.append(f"[HPO] Relevant phenotype terms: {term_str}")
                    trace.append({'step':'hpo','label':'HPO Mapping','detail':term_str,'status':'ok'})
            except Exception:
                pass
    return {'trace': trace, 'context_str': '\n'.join(enrichment)}

def check_needs_followup(message, session):
    history = session.get('messages', [])
    all_text = ' '.join(m.get('content','') for m in history).lower()
    if not any(k in message.lower() for k in SYMPTOM_KEYWORDS):
        return None
    if 'age' not in all_text and 'year' not in all_text and 'old' not in all_text:
        if len(history) <= 3:
            return "age_sex"
    if 'family' not in all_text and 'hereditary' not in all_text:
        if 3 < len(history) <= 6:
            return "family_history"
    return None

def sse(event_type, data):
    return f"data: {json.dumps({'type': event_type, **data})}\n\n"

# ── Streaming endpoint ────────────────────────────────────────────────
@chat_bp.route("/stream", methods=["POST"])
def stream():
    data = request.get_json()
    session_id = data.get("session_id", str(int(time.time())))
    user_message = data.get("message", "").strip()
    selected_option = data.get("selected_option")
    context = data.get("context")
    mode = data.get("mode", "patient")

    if not user_message and not selected_option:
        return jsonify({"error": "message required"}), 400
    if selected_option:
        user_message = selected_option

    if session_id not in sessions:
        sessions[session_id] = {"messages": [], "context": None, "mode": mode, "collected": {}}

    session = sessions[session_id]
    if context: session["context"] = context
    if mode: session["mode"] = mode

    if data.get("selected_option"):
        pending = session.get("pending_question")
        if pending == "age_sex": session["collected"]["age_sex"] = selected_option
        elif pending == "family_history": session["collected"]["family_history"] = selected_option
        session["pending_question"] = None

    session["messages"].append({"role": "user", "content": user_message})

    medgemma = current_app.config.get("MEDGEMMA")
    clinvar = current_app.config.get("CLINVAR")
    hpo = current_app.config.get("HPO")

    intent = detect_intent(user_message)

    def generate():
        # ── Step 1: Tool calls ──────────────────────────────────────
        agent_trace = []
        enriched_context = ""

        if intent['needs_agent']:
            if intent['genes']:
                for gene in intent['genes'][:2]:
                    yield sse('tool_start', {'label': f'Querying ClinVar → {gene}…', 'step': 'clinvar'})
            if intent['has_symptoms']:
                yield sse('tool_start', {'label': 'Mapping symptoms → HPO…', 'step': 'hpo'})

            enrichment = run_agent_enrichment(user_message, intent, clinvar, hpo)
            agent_trace = enrichment['trace']
            enriched_context = enrichment['context_str']

            for tr in agent_trace:
                yield sse('tool_done', tr)

        # ── Step 2: Build augmented messages ────────────────────────
        augmented = list(session["messages"])
        if enriched_context:
            last = augmented[-1]
            augmented[-1] = {"role": "user", "content":
                f"{last['content']}\n\n[Database context:\n{enriched_context}]"}

        collected = session.get("collected", {})
        if collected:
            parts = []
            if collected.get("age_sex"): parts.append(f"Patient: {collected['age_sex']}")
            if collected.get("family_history"): parts.append(f"Family history: {collected['family_history']}")
            if parts:
                augmented[-1]["content"] += f"\n[Patient info: {', '.join(parts)}]"

        # ── Step 3: Stream tokens ────────────────────────────────────
        yield sse('reply_start', {})
        t0 = time.time()
        full_reply = ""

        if medgemma and not medgemma.use_demo and medgemma.model:
            # Build formatted messages for medgemma
            sys_prompt = (
                "You are RareNav, an AI assistant for clinical genetics. "
                "Provide concise, evidence-based responses using clinical terminology."
                if mode == "clinician" else
                "You are RareNav, a compassionate AI guide for patients navigating rare genetic diseases. "
                "Use simple, clear language and be warm and reassuring."
            )
            formatted = [
                {"role": "user", "content": [{"type": "text", "text": sys_prompt}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Understood. How can I help?"}]}
            ]
            for m in augmented[-8:]:
                formatted.append({"role": m["role"], "content": [{"type": "text", "text": m["content"]}]})

            try:
                for token in medgemma._generate_stream(formatted, max_new_tokens=400, temperature=0.4):
                    full_reply += token
                    yield sse('token', {'text': token})
            except Exception as e:
                full_reply = f"Generation error: {e}"
                yield sse('token', {'text': full_reply})
        else:
            # Demo mode — simulate streaming
            result = medgemma.chat_with_context(augmented, session.get("context"), mode)
            full_reply = result.get("reply", "")
            words = full_reply.split(' ')
            for i, word in enumerate(words):
                chunk = word + (' ' if i < len(words)-1 else '')
                yield sse('token', {'text': chunk})
                time.sleep(0.02)

        latency = round(time.time() - t0, 1)
        session["messages"].append({"role": "assistant", "content": full_reply})
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]

        # ── Step 4: Followup question ────────────────────────────────
        followup_question = None
        followup_options = None
        if intent['needs_agent'] and not data.get("selected_option"):
            fq = check_needs_followup(user_message, session)
            if fq == "age_sex":
                session["pending_question"] = "age_sex"
                followup_question = "To give a more accurate assessment — what is the patient's age?"
                followup_options = ["Child (0-12)", "Teen (13-17)", "Young Adult (18-35)", "Adult (36-60)", "Senior (60+)"]
            elif fq == "family_history":
                session["pending_question"] = "family_history"
                followup_question = "Any relevant family history of genetic or rare diseases?"
                followup_options = ["Yes, known family history", "Possibly / unsure", "No known family history", "Unknown / adopted"]

        yield sse('done', {
            'latency': latency,
            'demo': medgemma.use_demo if medgemma else True,
            'followup_question': followup_question,
            'followup_options': followup_options,
        })

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )

# ── Non-streaming fallback ────────────────────────────────────────────
@chat_bp.route("/message", methods=["POST"])
def message():
    data = request.get_json()
    session_id = data.get("session_id", str(int(time.time())))
    user_message = data.get("message", "").strip()
    context = data.get("context")
    mode = data.get("mode", "patient")
    selected_option = data.get("selected_option")

    if not user_message and not selected_option:
        return jsonify({"error": "message required"}), 400
    if selected_option:
        user_message = selected_option

    if session_id not in sessions:
        sessions[session_id] = {"messages": [], "context": None, "mode": mode, "collected": {}}

    session = sessions[session_id]
    if context: session["context"] = context
    if mode: session["mode"] = mode

    if data.get("selected_option"):
        pending = session.get("pending_question")
        if pending == "age_sex": session["collected"]["age_sex"] = selected_option
        elif pending == "family_history": session["collected"]["family_history"] = selected_option
        session["pending_question"] = None

    session["messages"].append({"role": "user", "content": user_message})
    medgemma = current_app.config.get("MEDGEMMA")
    clinvar = current_app.config.get("CLINVAR")
    hpo = current_app.config.get("HPO")
    intent = detect_intent(user_message)
    agent_trace = []
    enriched_context = ""

    if intent['needs_agent']:
        enrichment = run_agent_enrichment(user_message, intent, clinvar, hpo)
        agent_trace = enrichment['trace']
        enriched_context = enrichment['context_str']

    augmented = list(session["messages"])
    if enriched_context:
        last = augmented[-1]
        augmented[-1] = {"role": "user", "content": f"{last['content']}\n\n[Database context:\n{enriched_context}]"}

    result = medgemma.chat_with_context(augmented, session.get("context"), mode)
    reply = result.get("reply", "")

    followup_question = None
    followup_options = None
    if intent['needs_agent'] and not data.get("selected_option"):
        fq = check_needs_followup(user_message, session)
        if fq == "age_sex":
            session["pending_question"] = "age_sex"
            followup_question = "To give a more accurate assessment — what is the patient's age?"
            followup_options = ["Child (0-12)", "Teen (13-17)", "Young Adult (18-35)", "Adult (36-60)", "Senior (60+)"]
        elif fq == "family_history":
            session["pending_question"] = "family_history"
            followup_question = "Any relevant family history of genetic or rare diseases?"
            followup_options = ["Yes, known family history", "Possibly / unsure", "No known family history", "Unknown / adopted"]

    session["messages"].append({"role": "assistant", "content": reply})
    if len(session["messages"]) > 20:
        session["messages"] = session["messages"][-20:]

    return jsonify({
        "reply": reply, "session_id": session_id,
        "latency": result.get("latency"), "demo_mode": result.get("demo", True),
        "agent_trace": agent_trace,
        "followup_question": followup_question, "followup_options": followup_options,
    })

@chat_bp.route("/session/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    sessions.pop(session_id, None)
    return jsonify({"cleared": True})
