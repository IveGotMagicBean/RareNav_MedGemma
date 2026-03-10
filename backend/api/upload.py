"""Upload API - handles report image/PDF upload and multimodal extraction"""
from flask import Blueprint, request, jsonify, current_app
import time, logging

log = logging.getLogger(__name__)
upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/report", methods=["POST"])
def upload_report():
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception as e:
        return jsonify({"error": f"JSON parse failed: {e}"}), 400

    file_data = data.get("file_data")
    file_type = data.get("file_type", "image/jpeg")
    t0 = time.time()

    if not file_data:
        return jsonify({"error": "file_data is required"}), 400

    # Sanity check: base64 string should be non-empty
    if len(file_data) < 100:
        return jsonify({"error": "file_data too short — upload may have failed"}), 400

    log.info(f"Upload received: type={file_type}, base64_len={len(file_data)}")

    medgemma = current_app.config["MEDGEMMA"]
    claude = current_app.config.get("CLAUDE")

    # Prefer Claude (API-based, no GPU needed) → fall back to MedGemma → demo
    if claude and claude.available:
        log.info("Using Claude vision for report extraction")
        result = claude.extract_from_report(file_data, file_type)
        return jsonify({
            "extracted": result.get("extracted", {}),
            "raw_text": result.get("raw_text", ""),
            "latency": round(time.time() - t0, 2),
            "demo": result.get("demo", False),
            "engine": "claude"
        })

    # MedGemma fallback
    prompt = """You are a medical genetics expert. Analyze this genetic test report and extract all genetic variants mentioned.

Return ONLY valid JSON in this exact format, nothing else:
{
  "variants": [
    {
      "gene": "GENE_NAME",
      "variant": "variant_notation (e.g. c.1521_1523del or p.Phe508del)",
      "significance": "Pathogenic or Likely Pathogenic or VUS or Likely Benign or Benign",
      "condition": "associated condition name",
      "zygosity": "heterozygous | homozygous | unknown",
      "raw_text": "exact text from report"
    }
  ],
  "report_type": "type of genetic test (e.g. Comprehensive Carrier Screen)",
  "lab": "laboratory name if visible",
  "summary": "one sentence summary of key findings"
}

If no genetic variants found: {"variants": [], "summary": "No genetic variants detected"}"""

    result = medgemma.extract_from_image(file_data, file_type, prompt)

    return jsonify({
        "extracted": result.get("extracted", {}),
        "raw_text": result.get("raw_text", ""),
        "latency": round(time.time() - t0, 2),
        "demo": result.get("demo", True),
        "engine": "medgemma"
    })
