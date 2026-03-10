"""
Agent Chat API — Multi-turn conversational diagnostic Agent
POST /api/agent/chat        → send a message, get streaming SSE response
GET  /api/agent/session     → get session state
POST /api/agent/session/new → create new session
DELETE /api/agent/session/<id> → clear session
"""
from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
import logging
import json
import time
import threading

from services.agent_session import (
    get_or_create_session, get_session,
    FOLLOWUP_QUESTIONS
)

log = logging.getLogger(__name__)
agent_chat_bp = Blueprint("agent_chat", __name__)


def sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event"""
    payload = json.dumps({"type": event_type, **data})
    return f"data: {payload}\n\n"


def run_analysis_pipeline(session, medgemma, clinvar, hpo):
    """
    Run the full diagnostic pipeline. Yields SSE events.
    This is a generator used inside a streaming response.
    """
    t0 = time.time()

    def step_event(step, detail, data=None):
        session.add_trace_step(step, detail, data)
        return sse_event("trace_step", {
            "step": step, "detail": detail,
            "ts": round(time.time() - t0, 2),
            "data": data
        })

    yield step_event("input_parsing",
                     f"Analysing {len(session.symptoms)} symptom(s) and {len(session.variants)} variant(s)",
                     {"symptoms": session.symptoms, "variants": [f"{v.get('gene')} {v.get('variant')}" for v in session.variants]})

    # ── ClinVar lookup ───────────────────────────────────────────
    clinvar_results = []
    if clinvar and session.variants:
        for v in session.variants[:5]:
            gene = v.get("gene", "")
            var_name = v.get("variant", "")
            if not gene:
                continue
            try:
                records = []
                if var_name:
                    records = clinvar.search_by_variant(gene, var_name)
                if not records:
                    records = clinvar.search_by_gene(gene, 3)
                clinvar_results.append({
                    "query": f"{gene} {var_name}",
                    "records": records[:3],
                    "found": len(records) > 0
                })
                yield step_event("clinvar_query",
                                 f"ClinVar: {gene} — {len(records)} record(s) found",
                                 {"gene": gene, "hits": len(records)})
            except Exception as e:
                yield step_event("clinvar_query", f"ClinVar lookup failed for {gene}: {e}")

    session.clinvar_results = clinvar_results

    # ── HPO mapping ──────────────────────────────────────────────
    hpo_terms = []
    if hpo and session.symptoms:
        try:
            mapped = hpo.map_symptoms(session.symptoms)
            hpo_terms = mapped.get("mapped", [])
            yield step_event("hpo_mapping",
                             f"Mapped {len(session.symptoms)} symptom(s) → {len(hpo_terms)} HPO term(s)",
                             {"terms": [t.get("term", "") for t in hpo_terms[:6]]})
        except Exception as e:
            yield step_event("hpo_mapping", f"HPO mapping error: {e}")
    elif session.symptoms:
        yield step_event("hpo_mapping", "Using raw symptom descriptions (HPO service unavailable)")

    session.hpo_terms = hpo_terms

    # ── MedGemma reasoning ───────────────────────────────────────
    yield step_event("ai_reasoning", "MedGemma initiating clinical reasoning…")

    if medgemma and not medgemma.use_demo and medgemma.model is not None:
        # Build rich prompt
        context_parts = []

        if session.variants:
            var_lines = "\n".join(
                f"- {v.get('gene','?')} {v.get('variant','?')} [{v.get('significance','unknown')}] → {v.get('condition','unknown')}"
                for v in session.variants
            )
            context_parts.append(f"**Genetic Variants:**\n{var_lines}")

        if clinvar_results:
            cv_lines = []
            for cr in clinvar_results:
                if cr["found"] and cr["records"]:
                    r = cr["records"][0]
                    cv_lines.append(f"- {r.get('gene','')} {r.get('name','')[:50]} [{r.get('significance','')}]")
            if cv_lines:
                context_parts.append("**ClinVar Evidence:**\n" + "\n".join(cv_lines))

        if session.symptoms:
            context_parts.append(f"**Symptoms:** {', '.join(session.symptoms)}")

        if hpo_terms:
            hpo_str = ", ".join(t.get("term", "") for t in hpo_terms[:8])
            context_parts.append(f"**HPO Terms:** {hpo_str}")

        if session.patient_info:
            info_parts = []
            for k in ["age", "sex", "duration", "family_history", "severity"]:
                if session.patient_info.get(k):
                    info_parts.append(f"{k.replace('_',' ').title()}: {session.patient_info[k]}")
            if info_parts:
                context_parts.append("**Patient:** " + " | ".join(info_parts))

        if session.report_summary:
            context_parts.append(f"**Report Summary:** {session.report_summary}")

        clinical_context = "\n\n".join(context_parts)

        prompt = f"""You are RareNav Diagnostic Agent. Perform a structured rare disease diagnostic analysis.

{clinical_context}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "differential_diagnosis": [
    {{
      "rank": 1,
      "disease": "disease name",
      "omim": "OMIM ID or empty string",
      "confidence": "high | medium | low",
      "confidence_pct": 85,
      "supporting_evidence": ["evidence 1", "evidence 2"],
      "against_evidence": ["counter 1"],
      "inheritance": "autosomal recessive | dominant | X-linked | mitochondrial | unknown"
    }}
  ],
  "genetic_interpretation": {{
    "overall_classification": "summary",
    "key_findings": ["finding 1", "finding 2"],
    "variants_of_note": ["GENE:variant"]
  }},
  "recommended_workup": {{
    "immediate": ["urgent action 1"],
    "short_term": ["test within 1-3 months"],
    "genetic_tests": ["specific panel or sequencing"]
  }},
  "specialist_referrals": [
    {{"specialty": "name", "urgency": "urgent | soon | elective", "reason": "brief reason"}}
  ],
  "management_plan": {{
    "monitoring": ["surveillance item"],
    "treatment_options": ["therapy option"],
    "patient_education": ["key point"]
  }},
  "family_implications": {{
    "inheritance_risk": "risk description",
    "cascade_testing": "recommendation",
    "genetic_counseling": "yes | recommended | not indicated"
  }},
  "clinical_summary": "2-3 sentence physician summary",
  "patient_summary": "2-3 sentence plain-language patient summary",
  "urgency": "critical | high | medium | low",
  "confidence_level": "high | medium | low",
  "reasoning_notes": "brief reasoning"
}}"""

        try:
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

            # Try streaming generation
            if hasattr(medgemma, '_generate_stream'):
                full_text = ""
                token_buffer = ""
                for token in medgemma._generate_stream(messages, max_new_tokens=1500, temperature=0.3):
                    full_text += token
                    token_buffer += token
                    # Emit token chunks for streaming feel
                    if len(token_buffer) >= 3:
                        yield sse_event("token", {"text": token_buffer})
                        token_buffer = ""
                if token_buffer:
                    yield sse_event("token", {"text": token_buffer})
            else:
                full_text = medgemma._generate(messages, max_new_tokens=1500, temperature=0.3)
                # Simulate streaming by chunking
                for i in range(0, len(full_text), 8):
                    yield sse_event("token", {"text": full_text[i:i+8]})
                    time.sleep(0.01)

            # Parse the JSON report
            import re
            match = re.search(r'\{.*\}', full_text, re.DOTALL)
            if match:
                import json as _json
                try:
                    report = _json.loads(match.group())
                except Exception:
                    report = {"clinical_summary": full_text, "error": "JSON parse failed"}
            else:
                report = {"clinical_summary": full_text, "error": "No JSON found in output"}

        except Exception as e:
            log.error(f"MedGemma reasoning failed: {e}")
            report = {"error": str(e), "clinical_summary": "Analysis failed."}

    else:
        # Demo mode — structured mock report
        top_symptom = session.symptoms[0] if session.symptoms else "presenting symptoms"
        top_gene = session.variants[0].get("gene", "CFTR") if session.variants else "CFTR"
        report = _demo_report(top_gene, session.symptoms, session.patient_info)
        # Stream the demo report character by character for effect
        demo_str = json.dumps(report)
        for i in range(0, len(demo_str), 6):
            yield sse_event("token", {"text": demo_str[i:i+6]})
            time.sleep(0.008)

    session.report = report
    session.state = "complete"

    top_dx = "N/A"
    if report.get("differential_diagnosis"):
        top_dx = report["differential_diagnosis"][0].get("disease", "N/A")

    yield step_event("report_generated",
                     f"Analysis complete — top diagnosis: {top_dx}",
                     {"urgency": report.get("urgency", "unknown")})

    yield sse_event("report", {
        "report": report,
        "trace": session.trace,
        "clinvar_results": clinvar_results,
        "hpo_terms": hpo_terms,
        "latency": round(time.time() - t0, 2),
        "demo": medgemma.use_demo if medgemma else True,
    })

    yield sse_event("done", {"session_id": session.session_id})


def _demo_report(gene: str, symptoms: list, patient_info: dict) -> dict:
    return {
        "differential_diagnosis": [
            {
                "rank": 1,
                "disease": "Cystic Fibrosis",
                "omim": "219700",
                "confidence": "high",
                "confidence_pct": 82,
                "supporting_evidence": ["CFTR pathogenic variant detected", "Respiratory symptoms consistent", "Elevated sweat chloride pattern"],
                "against_evidence": ["Age of presentation atypical"],
                "inheritance": "autosomal recessive"
            },
            {
                "rank": 2,
                "disease": "Primary Ciliary Dyskinesia",
                "omim": "244400",
                "confidence": "medium",
                "confidence_pct": 45,
                "supporting_evidence": ["Recurrent respiratory infections", "Symptom overlap with CF"],
                "against_evidence": ["No DNAI1/DNAI2 variants identified"],
                "inheritance": "autosomal recessive"
            },
            {
                "rank": 3,
                "disease": "Alpha-1 Antitrypsin Deficiency",
                "omim": "613490",
                "confidence": "low",
                "confidence_pct": 22,
                "supporting_evidence": ["Pulmonary involvement possible"],
                "against_evidence": ["SERPINA1 not flagged", "Liver findings absent"],
                "inheritance": "autosomal recessive"
            }
        ],
        "genetic_interpretation": {
            "overall_classification": "Pathogenic variant identified — consistent with clinical phenotype",
            "key_findings": [f"{gene} pathogenic variant confirmed", "Biallelic inheritance pattern consistent with AR disorder"],
            "variants_of_note": [f"{gene}:c.1521_1523del"]
        },
        "recommended_workup": {
            "immediate": ["Sweat chloride test", "Pulmonary function tests", "Sputum microbiology"],
            "short_term": ["Chest CT", "Pancreatic enzyme levels", "Nutritional assessment"],
            "genetic_tests": ["Full CFTR sequencing if not done", "Carrier testing for first-degree relatives"]
        },
        "specialist_referrals": [
            {"specialty": "Pulmonology", "urgency": "urgent", "reason": "Respiratory disease management"},
            {"specialty": "Medical Genetics", "urgency": "soon", "reason": "Variant counseling and family planning"},
            {"specialty": "Gastroenterology", "urgency": "elective", "reason": "Pancreatic involvement assessment"}
        ],
        "management_plan": {
            "monitoring": ["Annual pulmonary function", "BMI and nutrition quarterly", "Liver function annually"],
            "treatment_options": ["CFTR modulators (eligibility based on variant)", "Airway clearance therapy", "Enzyme replacement if pancreatic insufficient"],
            "patient_education": ["Inheritance risk explained — AR pattern", "Sibling testing recommended", "CF Foundation registry and clinical trials"]
        },
        "family_implications": {
            "inheritance_risk": "25% risk for each sibling to be affected (AR); parents are obligate carriers",
            "cascade_testing": "Carrier testing recommended for all first-degree relatives",
            "genetic_counseling": "yes"
        },
        "clinical_summary": f"Patient presents with symptoms consistent with a CFTR-related disorder. Genetic findings and clinical phenotype support a diagnosis of Cystic Fibrosis. Urgent pulmonology referral and confirmatory sweat chloride testing are recommended.",
        "patient_summary": "Your genetic results suggest a condition called Cystic Fibrosis, caused by changes in the CFTR gene. This is a manageable condition, and treatments have improved greatly in recent years. We recommend seeing a specialist who can guide your care.",
        "urgency": "high",
        "confidence_level": "high",
        "reasoning_notes": "Demo mode — illustrative report. Run with real MedGemma model for actual analysis."
    }


@agent_chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("session_id")
    user_message = data.get("message", "").strip()
    selected_option = data.get("selected_option")
    file_data = data.get("file_data")
    file_type = data.get("file_type", "image/jpeg")
    new_variants = data.get("variants", [])
    new_symptoms = data.get("symptoms", [])

    session = get_or_create_session(session_id)
    medgemma = current_app.config.get("MEDGEMMA")
    clinvar = current_app.config.get("CLINVAR")
    hpo = current_app.config.get("HPO")

    # Ingest any pre-parsed data
    if new_variants:
        session.variants.extend(new_variants)
    if new_symptoms:
        session.symptoms.extend(new_symptoms)
        session.symptoms = list(dict.fromkeys(session.symptoms))

    def generate():
        # ── GREETING state ──────────────────────────────────────
        if session.state == "greeting":
            session.state = "collecting"
            welcome = (
                "Hello! I'm **RareNav Agent** — your AI diagnostic assistant for rare genetic diseases.\n\n"
                "You can start by:\n"
                "- Describing the patient's symptoms\n"
                "- Uploading a genetic report (PDF or image)\n"
                "- Or typing a free-form clinical description\n\n"
                "What would you like to do?"
            )
            msg = session.add_message("agent", welcome, "text")
            yield sse_event("message", {"message": msg, "session_id": session.session_id})
            yield sse_event("done", {"session_id": session.session_id})
            return

        # ── Process user input ──────────────────────────────────
        if user_message or selected_option:
            display_text = selected_option or user_message
            user_msg = session.add_message("user", display_text, "text")
            yield sse_event("message", {"message": user_msg})

            session.update_from_user_input(user_message, selected_option)

        # ── Handle file upload ──────────────────────────────────
        if file_data and medgemma:
            extract_msg = session.add_message("agent", "Extracting genetic variants from your report…", "thinking")
            yield sse_event("message", {"message": extract_msg})

            try:
                result = medgemma.extract_from_image(file_data, file_type,
                    "Extract all genetic variants. Return JSON with variants array.")
                extracted = result.get("extracted", {})
                extracted_variants = extracted.get("variants", [])
                if extracted_variants:
                    session.variants.extend(extracted_variants)
                    session.report_summary = extracted.get("summary", "")
                    engine = result.get("engine", "local_ocr")
                    ok_msg = session.add_message(
                        "agent",
                        f"✓ Found **{len(extracted_variants)} variant(s)** via {engine}: "
                        + ", ".join(f"{v.get('gene')} {v.get('variant')}" for v in extracted_variants[:3]),
                        "success",
                        metadata={"variants": extracted_variants}
                    )
                    yield sse_event("message", {"message": ok_msg})
                else:
                    warn_msg = session.add_message("agent",
                        "No variants detected in the report. Please describe symptoms manually.",
                        "warning")
                    yield sse_event("message", {"message": warn_msg})
            except Exception as e:
                err_msg = session.add_message("agent", f"Report extraction failed: {e}", "error")
                yield sse_event("message", {"message": err_msg})

        # ── If we have no info yet, prompt for symptoms ─────────
        if not session.symptoms and not session.variants and not user_message:
            prompt_msg = session.add_message(
                "agent",
                "Please describe the patient's symptoms, or upload a genetic report to get started.",
                "text"
            )
            yield sse_event("message", {"message": prompt_msg})
            yield sse_event("done", {"session_id": session.session_id})
            return

        # ── Extract symptoms from free-text if we have none yet ─
        if user_message and not session.symptoms and session.state == "collecting":
            session.symptoms = [s.strip() for s in user_message.replace(";", ",").split(",") if len(s.strip()) > 2]
            if not session.symptoms:
                session.symptoms = [user_message]

        # ── Decide: ask follow-up OR run analysis ───────────────
        if session.is_ready_for_analysis():
            # Run the full pipeline
            session.state = "analyzing"
            thinking_msg = session.add_message("agent", "Starting full diagnostic analysis…", "thinking")
            yield sse_event("message", {"message": thinking_msg})

            yield from run_analysis_pipeline(session, medgemma, clinvar, hpo)

        else:
            next_q = session.get_next_question()
            if next_q:
                session.questions_asked.append(next_q["key"])
                session.followup_count += 1

                q_msg = session.add_message(
                    "agent",
                    next_q["question"],
                    "question",
                    options=next_q.get("options"),
                )
                yield sse_event("message", {"message": q_msg})
                yield sse_event("done", {"session_id": session.session_id})
            else:
                # Ran out of questions, just go ahead
                session.state = "analyzing"
                thinking_msg = session.add_message("agent", "Proceeding with available information…", "thinking")
                yield sse_event("message", {"message": thinking_msg})
                yield from run_analysis_pipeline(session, medgemma, clinvar, hpo)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@agent_chat_bp.route("/session", methods=["GET"])
def get_session_info():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session.to_dict())


@agent_chat_bp.route("/session/new", methods=["POST"])
def new_session():
    session = get_or_create_session()
    return jsonify({"session_id": session.session_id})


@agent_chat_bp.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    from services.agent_session import _sessions
    if session_id in _sessions:
        del _sessions[session_id]
    return jsonify({"deleted": True})
