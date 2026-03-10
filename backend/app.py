"""
RareNav - Rare Disease Navigation System
Main Flask Application
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from pathlib import Path

from api.variants import variants_bp
from api.symptoms import symptoms_bp
from api.diagnosis import diagnosis_bp
from api.chat import chat_bp
from api.diseases import diseases_bp
from api.agent_chat import agent_chat_bp
from services.clinvar_service import ClinVarService
from services.medgemma_service import MedGemmaService
from services.hpo_service import HPOService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
MODEL_PATH = os.environ.get("MODEL_PATH", "./medgemma-4b-it")
CLINVAR_PATH = os.environ.get("CLINVAR_PATH", "./data/variant_summary.txt")
HPO_PATH = os.environ.get("HPO_PATH", "./data/hp.obo")

app = Flask(__name__, static_folder="../frontend/dist")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Services (initialized on startup)
clinvar_service = None
medgemma_service = None
hpo_service = None


def init_services():
    global clinvar_service, medgemma_service, hpo_service
    logger.info("Initializing services...")

    clinvar_service = ClinVarService(CLINVAR_PATH)
    clinvar_service.load()

    hpo_service = HPOService(HPO_PATH)
    hpo_service.load()

    medgemma_service = MedGemmaService(MODEL_PATH)
    medgemma_service.load()

    # Inject into blueprints
    app.config["CLINVAR"] = clinvar_service
    app.config["MEDGEMMA"] = medgemma_service
    app.config["HPO"] = hpo_service

    logger.info("All services ready!")


# Register blueprints
app.register_blueprint(variants_bp, url_prefix="/api/variants")
app.register_blueprint(symptoms_bp, url_prefix="/api/symptoms")
app.register_blueprint(diagnosis_bp, url_prefix="/api/diagnosis")
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(diseases_bp, url_prefix="/api/diseases")
app.register_blueprint(agent_chat_bp, url_prefix="/api/agent")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "clinvar": clinvar_service is not None and clinvar_service.loaded,
            "medgemma": medgemma_service is not None and medgemma_service.loaded,
            "hpo": hpo_service is not None and hpo_service.loaded
        }
    })


@app.route("/api/status")
def status():
    stats = {}
    if clinvar_service and clinvar_service.loaded:
        stats["variant_count"] = clinvar_service.get_count()
    if hpo_service and hpo_service.loaded:
        stats["hpo_term_count"] = hpo_service.get_count()
    return jsonify(stats)


# Serve React frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    dist_dir = Path("../frontend/dist")
    if dist_dir.exists():
        if path and (dist_dir / path).exists():
            return send_from_directory(str(dist_dir), path)
        return send_from_directory(str(dist_dir), "index.html")
    return jsonify({"message": "Frontend not built. Run: cd frontend && npm run build"}), 404


if __name__ == "__main__":
    init_services()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"RareNav starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
