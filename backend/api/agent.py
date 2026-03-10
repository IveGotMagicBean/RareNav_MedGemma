"""
Agent API — Autonomous multi-step diagnostic pipeline
POST /api/agent/run  → run full pipeline (report + symptoms → diagnosis)
GET  /api/agent/status → check agent capabilities
"""
from flask import Blueprint, request, jsonify, current_app
import logging
import time

log = logging.getLogger(__name__)
agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/run", methods=["POST"])
def run_agent():
    """
    Full autonomous diagnostic agent.
    
    Input (JSON):
      - variants: list of {gene, variant, significance, condition} (from report upload)
      - symptoms: list of symptom strings
      - patient: {age, sex, family_history}
      - report_summary: string (from report extraction)
      - file_data: base64 string (optional — will auto-extract if provided)
      - file_type: mime type
    
    Output:
      - trace: step-by-step agent reasoning
      - report: structured diagnostic output
      - clinvar_results: ClinVar lookups performed
      - hpo_terms: HPO mappings
      - latency
    """
    data = request.get_json(force=True, silent=True) or {}
    t0 = time.time()

    variants = data.get("variants", [])
    symptoms = data.get("symptoms", [])
    patient = data.get("patient", {})
    report_summary = data.get("report_summary", "")
    file_data = data.get("file_data")
    file_type = data.get("file_type", "image/jpeg")

    if not variants and not symptoms and not file_data:
        return jsonify({"error": "Provide at least one of: variants, symptoms, or file_data"}), 400

    claude = current_app.config.get("CLAUDE")
    medgemma = current_app.config.get("MEDGEMMA")
    clinvar = current_app.config.get("CLINVAR")
    hpo = current_app.config.get("HPO")

    trace = []

    def step(name, detail, data_=None):
        entry = {"step": name, "detail": detail, "ts": round(time.time() - t0, 2)}
        if data_: entry["data"] = data_
        trace.append(entry)

    # ── Auto-extract from file if provided ─────────────────────
    if file_data and not variants:
        step("report_extraction", "Extracting genetic variants from uploaded report…")
        try:
            # Try Claude vision first, fall back to MedGemma
            if claude and claude.available:
                extract_result = claude.extract_from_report(file_data, file_type)
                engine = "claude"
            else:
                extract_result = medgemma.extract_from_image(
                    file_data, file_type,
                    "Extract all genetic variants. Return JSON with variants array."
                )
                engine = "medgemma"

            extracted = extract_result.get("extracted", {})
            variants = extracted.get("variants", [])
            if not report_summary:
                report_summary = extracted.get("summary", "")

            step("report_extraction",
                 f"Extracted {len(variants)} variant(s) via {engine}",
                 {"variants": [f"{v.get('gene')} {v.get('variant')}" for v in variants],
                  "engine": engine})
        except Exception as e:
            step("report_extraction", f"Extraction failed: {e}")

    # ── Run the Agent ──────────────────────────────────────────
    agent_inputs = {
        "variants": variants,
        "symptoms": symptoms,
        "patient": patient,
        "report_summary": report_summary,
    }

    if claude and claude.available:
        result = claude.run_diagnostic_agent(agent_inputs, clinvar_service=clinvar, hpo_service=hpo)
    else:
        # Fallback: MedGemma-based pipeline (limited)
        step("ai_reasoning", "Claude unavailable — using MedGemma fallback")
        report_text = medgemma.generate_diagnostic_report(patient, variants[0] if variants else None,
                                                          {"symptoms": symptoms} if symptoms else None)
        result = {
            "trace": [],
            "report": {"clinical_summary": report_text.get("report", ""), "engine": "medgemma"},
            "demo": report_text.get("demo", True),
            "latency": time.time() - t0,
        }

    # Merge extraction trace into agent trace
    result["trace"] = trace + result.get("trace", [])
    result["total_latency"] = round(time.time() - t0, 2)

    return jsonify(result)


@agent_bp.route("/status", methods=["GET"])
def agent_status():
    claude = current_app.config.get("CLAUDE")
    medgemma = current_app.config.get("MEDGEMMA")

    return jsonify({
        "claude_available": claude.available if claude else False,
        "medgemma_available": medgemma.loaded and not medgemma.use_demo if medgemma else False,
        "agent_capabilities": {
            "report_extraction": (claude and claude.available) or (medgemma and not medgemma.use_demo),
            "variant_search": True,  # ClinVar always available
            "symptom_mapping": True,
            "diagnostic_reasoning": (claude and claude.available) or (medgemma and not medgemma.use_demo),
            "multi_step_pipeline": claude.available if claude else False,
        }
    })
