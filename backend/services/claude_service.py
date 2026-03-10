"""
Claude Service (Anthropic API)
Used as:
1. Fallback when MedGemma model is not available
2. The Agent orchestration engine for multi-step reasoning
"""
import os
import json
import re
import logging
import time
import base64
import io
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def _call_claude(messages: List[Dict], system: str = "", max_tokens: int = 1500,
                 temperature: float = 0.7, image_b64: str = None,
                 image_type: str = "image/jpeg") -> str:
    """Raw call to Anthropic /v1/messages"""
    import urllib.request, urllib.error

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    # If image provided, inject into first user message
    if image_b64 and messages:
        first = messages[0]
        img_content = [
            {"type": "image", "source": {"type": "base64", "media_type": image_type, "data": image_b64}},
            {"type": "text", "text": first.get("content", "")}
        ]
        messages = [{"role": "user", "content": img_content}] + messages[1:]

    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        body["system"] = system

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        logger.error(f"Claude API error {e.code}: {err_body}")
        raise RuntimeError(f"Claude API HTTP {e.code}: {err_body[:200]}")


class ClaudeService:
    """Anthropic Claude as AI backbone — variant explanation, report parsing, agent reasoning"""

    def __init__(self):
        self.available = bool(ANTHROPIC_API_KEY)
        if not self.available:
            logger.warning("ANTHROPIC_API_KEY not set — Claude service unavailable")
        else:
            logger.info("Claude service ready (Anthropic API)")

    # ───────────────────────────────────────────────────────────
    # 1. Report image/PDF extraction (multimodal)
    # ───────────────────────────────────────────────────────────
    def extract_from_report(self, file_data: str, file_type: str) -> dict:
        """Extract genetic variants from uploaded PDF or image using Claude vision"""
        t0 = time.time()

        if not self.available:
            return {"error": "Claude API key not configured", "demo": True}

        # Convert PDF to image if needed
        img_b64 = file_data
        img_type = file_type

        if file_type == "application/pdf" or file_data[:8].startswith("JVBERi0"):
            try:
                raw = base64.b64decode(file_data)
                from pdf2image import convert_from_bytes
                pages = convert_from_bytes(raw, dpi=200, first_page=1, last_page=1)
                if pages:
                    buf = io.BytesIO()
                    pages[0].convert("RGB").save(buf, format="JPEG", quality=90)
                    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    img_type = "image/jpeg"
                    logger.info("PDF converted to JPEG for Claude vision")
            except Exception as e:
                logger.warning(f"PDF conversion failed ({e}), sending raw data")

        prompt = """You are a medical genetics expert. Analyze this genetic test report image and extract all genetic variants.

Return ONLY valid JSON, nothing else:
{
  "variants": [
    {
      "gene": "GENE_NAME",
      "variant": "HGVS notation or descriptive name",
      "significance": "Pathogenic | Likely Pathogenic | VUS | Likely Benign | Benign",
      "condition": "associated condition name",
      "zygosity": "heterozygous | homozygous | hemizygous | unknown",
      "raw_text": "exact text from report"
    }
  ],
  "report_type": "type of genetic test",
  "lab": "laboratory name if visible",
  "patient_id": "patient ID or anonymized identifier if visible",
  "date": "report date if visible",
  "summary": "one sentence summary of key findings",
  "negative_genes": ["list of tested genes with no findings, if mentioned"]
}

If no genetic variants found: {"variants": [], "summary": "No pathogenic variants detected"}
Be thorough — extract every variant mentioned including carrier status and VUS."""

        try:
            text = _call_claude(
                messages=[{"role": "user", "content": prompt}],
                image_b64=img_b64,
                image_type=img_type,
                max_tokens=1200,
                temperature=0.1,
            )
            # Parse JSON from response
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                extracted = json.loads(match.group())
            else:
                extracted = {"variants": [], "summary": text}

            return {
                "extracted": extracted,
                "raw_text": text,
                "demo": False,
                "latency": round(time.time() - t0, 2),
                "engine": "claude"
            }
        except Exception as e:
            logger.error(f"Claude extract_from_report failed: {e}")
            return {"error": str(e), "demo": True, "latency": round(time.time() - t0, 2)}

    # ───────────────────────────────────────────────────────────
    # 2. Variant explanation
    # ───────────────────────────────────────────────────────────
    def explain_variant(self, gene: str, variant: str, significance: str, disease: str) -> dict:
        t0 = time.time()
        if not self.available:
            return {"explanation": "Claude API not configured.", "demo": True}

        system = """You are a compassionate genetic counselor explaining results to patients and families.
Use clear language, be empathetic, and always recommend consulting a healthcare professional."""

        prompt = f"""Explain this genetic variant to a patient:
- Gene: {gene}
- Variant: {variant}  
- Clinical Significance: {significance}
- Associated Condition: {disease}

Cover: (1) what the gene does, (2) what this variant means, (3) implications for health, 
(4) inheritance and family risk, (5) next steps. Use clear, accessible language."""

        try:
            text = _call_claude(
                messages=[{"role": "user", "content": prompt}],
                system=system, max_tokens=700, temperature=0.7
            )
            return {"explanation": text, "latency": round(time.time() - t0, 2), "demo": False, "engine": "claude"}
        except Exception as e:
            return {"explanation": f"Error: {e}", "demo": True, "latency": round(time.time() - t0, 2)}

    # ───────────────────────────────────────────────────────────
    # 3. Agent: orchestrate full diagnostic pipeline
    # ───────────────────────────────────────────────────────────
    def run_diagnostic_agent(self, inputs: dict, clinvar_service=None, hpo_service=None) -> dict:
        """
        Autonomous multi-step diagnostic agent.
        
        Steps:
          1. Parse inputs (variants from report / symptoms / both)
          2. Query ClinVar for each variant
          3. Map symptoms to HPO terms
          4. Reason over genotype + phenotype
          5. Produce ranked differential, management plan, specialist list
        
        Returns structured agent trace + final report.
        """
        t0 = time.time()
        trace = []  # agent reasoning steps, visible in UI

        variants = inputs.get("variants", [])       # from report upload
        symptoms = inputs.get("symptoms", [])        # free text symptoms
        patient_info = inputs.get("patient", {})     # age, sex etc.
        report_summary = inputs.get("report_summary", "")

        def step(name: str, detail: str, data=None):
            entry = {"step": name, "detail": detail, "ts": round(time.time() - t0, 2)}
            if data: entry["data"] = data
            trace.append(entry)
            logger.info(f"[Agent] {name}: {detail}")

        # ── Step 1: Acknowledge inputs ──────────────────────────
        step("input_parsing",
             f"Received {len(variants)} variant(s) and {len(symptoms)} symptom(s)",
             {"variant_count": len(variants), "symptom_count": len(symptoms)})

        # ── Step 2: ClinVar lookup for each variant ─────────────
        clinvar_results = []
        if clinvar_service and variants:
            for v in variants[:5]:   # cap at 5
                gene = v.get("gene", "")
                var_name = v.get("variant", "")
                if not gene:
                    continue
                try:
                    records = []
                    if var_name:
                        records = clinvar_service.search_by_variant(gene, var_name)
                    if not records:
                        records = clinvar_service.search_by_gene(gene, 3)
                    clinvar_results.append({
                        "query": f"{gene} {var_name}",
                        "records": records[:3],
                        "found": len(records) > 0
                    })
                    step("clinvar_query",
                         f"ClinVar: {gene} {var_name} → {len(records)} record(s)",
                         {"gene": gene, "hits": len(records)})
                except Exception as e:
                    step("clinvar_query", f"ClinVar lookup failed for {gene}: {e}")

        # ── Step 3: HPO symptom mapping ─────────────────────────
        hpo_terms = []
        if hpo_service and symptoms:
            try:
                mapped = hpo_service.map_symptoms(symptoms)
                hpo_terms = mapped.get("mapped", [])
                step("hpo_mapping",
                     f"Mapped {len(symptoms)} symptom(s) to {len(hpo_terms)} HPO term(s)",
                     {"terms": [t.get("term", "") for t in hpo_terms[:5]]})
            except Exception as e:
                step("hpo_mapping", f"HPO mapping failed: {e}")
        elif symptoms:
            # HPO not available — pass raw symptoms
            step("hpo_mapping", "HPO service not available — using raw symptom text")

        # ── Step 4: AI reasoning ────────────────────────────────
        step("ai_reasoning", "Initiating multi-step clinical reasoning…")

        if not self.available:
            step("ai_reasoning", "Claude API not available — returning partial results")
            return {
                "trace": trace,
                "report": {"error": "AI reasoning requires ANTHROPIC_API_KEY"},
                "latency": round(time.time() - t0, 2),
                "demo": True
            }

        # Build context for Claude
        context_parts = []

        if variants:
            var_text = "\n".join(
                f"- {v.get('gene','?')} {v.get('variant','?')} "
                f"[{v.get('significance','unknown')}] → {v.get('condition','unknown condition')}"
                for v in variants
            )
            context_parts.append(f"**Genetic Findings:**\n{var_text}")

        if clinvar_results:
            cv_text = []
            for cr in clinvar_results:
                if cr["found"] and cr["records"]:
                    r = cr["records"][0]
                    cv_text.append(
                        f"- ClinVar: {r.get('gene','')} {r.get('name','')[:60]} "
                        f"[{r.get('significance','')}] — {r.get('phenotype','')[:60]}"
                    )
            if cv_text:
                context_parts.append("**ClinVar Confirmation:**\n" + "\n".join(cv_text))

        if symptoms:
            context_parts.append(f"**Reported Symptoms:** {', '.join(symptoms)}")

        if hpo_terms:
            hpo_text = ", ".join(t.get("term", "") for t in hpo_terms[:8])
            context_parts.append(f"**HPO Terms:** {hpo_text}")

        if patient_info:
            info = []
            if patient_info.get("age"): info.append(f"Age: {patient_info['age']}")
            if patient_info.get("sex"): info.append(f"Sex: {patient_info['sex']}")
            if patient_info.get("family_history"): info.append(f"Family history: {patient_info['family_history']}")
            if info: context_parts.append("**Patient Info:** " + " | ".join(info))

        if report_summary:
            context_parts.append(f"**Report Summary:** {report_summary}")

        clinical_context = "\n\n".join(context_parts) if context_parts else "No specific genetic or clinical data provided."

        agent_prompt = f"""You are RareNav Diagnostic Agent, a clinical genetics AI conducting a systematic analysis.

{clinical_context}

Perform a structured diagnostic analysis and return ONLY valid JSON:
{{
  "differential_diagnosis": [
    {{
      "rank": 1,
      "disease": "disease name",
      "omim": "OMIM ID if known",
      "confidence": "high | medium | low",
      "supporting_evidence": ["evidence point 1", "evidence point 2"],
      "against_evidence": ["counter-evidence if any"],
      "inheritance": "autosomal recessive | dominant | X-linked | etc"
    }}
  ],
  "genetic_interpretation": {{
    "overall_classification": "summary of variant pathogenicity",
    "key_findings": ["finding 1", "finding 2"],
    "variants_of_note": ["gene:variant pairs that are most clinically significant"]
  }},
  "recommended_workup": {{
    "immediate": ["urgent tests or actions"],
    "short_term": ["tests within 1-3 months"],
    "genetic_tests": ["specific genetic panels or sequencing recommended"]
  }},
  "specialist_referrals": [
    {{"specialty": "specialty name", "urgency": "urgent | soon | elective", "reason": "brief reason"}}
  ],
  "management_plan": {{
    "monitoring": ["surveillance recommendations"],
    "treatment_options": ["available therapies"],
    "patient_education": ["key points to discuss with patient"]
  }},
  "family_implications": {{
    "inheritance_risk": "risk assessment for family members",
    "cascade_testing": "recommendation for family testing",
    "genetic_counseling": "yes | recommended | not indicated"
  }},
  "clinical_summary": "2-3 sentence overall clinical summary for the physician",
  "patient_summary": "2-3 sentence plain-language summary for the patient",
  "urgency": "critical | high | medium | low",
  "confidence_level": "high | medium | low",
  "reasoning_notes": "brief notes on the agent's reasoning process"
}}

Be specific and evidence-based. If data is limited, indicate uncertainty clearly."""

        try:
            step("ai_reasoning", "Calling Claude for multi-step clinical synthesis…")
            raw_response = _call_claude(
                messages=[{"role": "user", "content": agent_prompt}],
                system="You are a medical genetics AI. Return only valid JSON.",
                max_tokens=2000,
                temperature=0.3
            )

            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if match:
                report = json.loads(match.group())
            else:
                report = {"clinical_summary": raw_response, "error": "Could not parse structured output"}

            step("report_generated",
                 f"Diagnostic report complete. Top dx: {report.get('differential_diagnosis', [{}])[0].get('disease', 'N/A') if report.get('differential_diagnosis') else 'N/A'}",
                 {"urgency": report.get("urgency", "unknown")})

            return {
                "trace": trace,
                "report": report,
                "clinvar_results": clinvar_results,
                "hpo_terms": hpo_terms,
                "latency": round(time.time() - t0, 2),
                "demo": False,
                "engine": "claude-agent"
            }

        except Exception as e:
            step("error", f"Agent reasoning failed: {e}")
            return {
                "trace": trace,
                "report": {"error": str(e), "clinical_summary": "Agent encountered an error during reasoning."},
                "latency": round(time.time() - t0, 2),
                "demo": True
            }

    # ───────────────────────────────────────────────────────────
    # 4. Symptom analysis
    # ───────────────────────────────────────────────────────────
    def analyze_symptoms(self, symptoms: List[str], age: str = None, sex: str = None) -> dict:
        t0 = time.time()
        if not self.available:
            return {"analysis": "Claude API not configured.", "demo": True}

        patient_ctx = ""
        if age or sex:
            patient_ctx = f"\nPatient: {age or 'unknown age'}, {sex or 'unknown sex'}"

        prompt = f"""As a rare disease specialist, analyze these symptoms and provide differential diagnosis:{patient_ctx}

Symptoms: {', '.join(symptoms)}

Provide: top 3-5 rare disease differentials with reasoning, recommended workup, and specialist referrals.
Use clear clinical language."""

        try:
            text = _call_claude(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800, temperature=0.5
            )
            return {"analysis": text, "latency": round(time.time() - t0, 2), "demo": False, "engine": "claude"}
        except Exception as e:
            return {"analysis": f"Error: {e}", "demo": True, "latency": round(time.time() - t0, 2)}

    # ───────────────────────────────────────────────────────────
    # 5. Chat
    # ───────────────────────────────────────────────────────────
    def chat_response(self, messages: List[Dict], context: dict = None, mode: str = "patient") -> dict:
        t0 = time.time()
        if not self.available:
            return {"reply": "Claude API not configured. Please set ANTHROPIC_API_KEY.", "demo": True}

        if mode == "clinician":
            system = """You are RareNav, a clinical genetics AI assistant.
Use clinical terminology (ACMG criteria, HGVS notation, evidence grades).
Be concise and evidence-based. Always note evidence quality."""
        else:
            system = """You are RareNav, a compassionate guide for patients navigating rare genetic diseases.
Use simple, clear language. Be warm and reassuring. Always recommend speaking with their doctor."""

        if context:
            parts = []
            for k in ["gene", "variant", "significance", "condition"]:
                if context.get(k): parts.append(f"{k.title()}: {context[k]}")
            if parts: system += "\n\nCurrent context: " + " | ".join(parts)

        formatted = [{"role": m["role"], "content": m["content"]} for m in messages[-10:]]

        try:
            text = _call_claude(formatted, system=system, max_tokens=500, temperature=0.7)
            return {"reply": text, "latency": round(time.time() - t0, 2), "demo": False, "engine": "claude"}
        except Exception as e:
            return {"reply": f"Error: {e}", "demo": True, "latency": round(time.time() - t0, 2)}
