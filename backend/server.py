"""backend/server.py — Flask app factory"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import logging, os

log = logging.getLogger("rarenav.server")

def create_app(model_path="./models/medgemma-4b-it",
               clinvar_path="./data/variant_summary.txt",
               hpo_path="./data/hp.obo",
               frontend_dist=None) -> Flask:

    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from services.clinvar_service import ClinVarService
    from services.medgemma_service import MedGemmaService
    from services.hpo_service import HPOService
    from services.claude_service import ClaudeService

    log.info("Loading ClinVar ...")
    clinvar = ClinVarService(clinvar_path)
    clinvar.load()

    log.info("Loading HPO ...")
    hpo = HPOService(hpo_path)
    hpo.load()

    log.info("Loading MedGemma ...")
    medgemma = MedGemmaService(model_path)
    medgemma.load()

    log.info("Initializing Claude service ...")
    claude = ClaudeService()

    app.config.update(CLINVAR=clinvar, MEDGEMMA=medgemma, HPO=hpo, CLAUDE=claude)

    from api.variants  import variants_bp
    from api.symptoms  import symptoms_bp
    from api.diagnosis import diagnosis_bp
    from api.chat      import chat_bp
    from api.diseases  import diseases_bp
    from api.upload    import upload_bp
    from api.agent     import agent_bp

    app.register_blueprint(variants_bp,  url_prefix="/api/variants")
    app.register_blueprint(symptoms_bp,  url_prefix="/api/symptoms")
    app.register_blueprint(diagnosis_bp, url_prefix="/api/diagnosis")
    app.register_blueprint(chat_bp,      url_prefix="/api/chat")
    app.register_blueprint(diseases_bp,  url_prefix="/api/diseases")
    app.register_blueprint(upload_bp,    url_prefix="/api/upload")
    app.register_blueprint(agent_bp,     url_prefix="/api/agent")

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "healthy",
            "services": {
                "clinvar": clinvar.loaded,
                "medgemma": medgemma.loaded,
                "hpo": hpo.loaded,
                "claude": claude.available
            },
            "demo_mode": not claude.available and (clinvar.use_demo or medgemma.use_demo),
            "ai_engine": "claude" if claude.available else ("medgemma" if not medgemma.use_demo else "demo")
        })

    @app.route("/api/status")
    def status():
        return jsonify({
            "variant_count": clinvar.get_count(),
            "hpo_term_count": hpo.get_count(),
            "model_loaded": medgemma.loaded and not medgemma.use_demo,
        })

    # Serve files from the rarenav/file/ directory (demo.md, demo.mp4, etc.)
    # Path is resolved relative to the project root (one level up from backend/)
    project_root = Path(__file__).parent.parent
    file_dir = project_root / "file"

    @app.route("/file/<path:filename>")
    def serve_file(filename):
        if not file_dir.exists():
            return jsonify({"error": "file directory not found"}), 404
        return send_from_directory(str(file_dir), filename)

    from frontend import HTML as EMBEDDED_HTML
    dist_dir = Path(frontend_dist) if frontend_dist else None

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("file/"):
            return serve_file(path[5:])
        if dist_dir and path:
            target = dist_dir / path
            if target.exists() and target.is_file():
                return send_from_directory(str(dist_dir), path)
        return EMBEDDED_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

    log.info("Flask app ready.")
    return app

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
    _app = create_app(
        model_path=os.environ.get("MODEL_PATH", "../models/medgemma-4b-it"),
        clinvar_path=os.environ.get("CLINVAR_PATH", "../data/variant_summary.txt"),
        hpo_path=os.environ.get("HPO_PATH", "../data/hp.obo"),
    )
    _app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)
