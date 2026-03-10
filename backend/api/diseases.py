"""Diseases API - Disease information and knowledge base"""
from flask import Blueprint, request, jsonify, current_app
from .diagnosis import RARE_DISEASE_DB

diseases_bp = Blueprint("diseases", __name__)


@diseases_bp.route("/", methods=["GET"])
def list_diseases():
    search = request.args.get("q", "").lower()
    if search:
        filtered = [d for d in RARE_DISEASE_DB
                    if search in d["name"].lower() or search in d.get("gene", "").lower()
                    or any(search in s.lower() for s in d.get("key_symptoms", []))]
    else:
        filtered = RARE_DISEASE_DB
    return jsonify({"diseases": filtered, "count": len(filtered)})


@diseases_bp.route("/<disease_id>", methods=["GET"])
def get_disease(disease_id):
    disease = next((d for d in RARE_DISEASE_DB if d["id"] == disease_id), None)
    if not disease:
        # Try by name
        disease = next((d for d in RARE_DISEASE_DB
                        if d["name"].lower().replace(" ", "-") == disease_id.lower()), None)
    if not disease:
        return jsonify({"error": "Disease not found"}), 404
    return jsonify(disease)


@diseases_bp.route("/by-gene/<gene>", methods=["GET"])
def by_gene(gene):
    diseases = [d for d in RARE_DISEASE_DB if gene.upper() in d.get("gene", "").upper()]

    clinvar = current_app.config["CLINVAR"]
    clinvar_summary = clinvar.get_gene_summary(gene)
    clinvar_variants = clinvar.search_by_gene(gene, 10)

    return jsonify({
        "gene": gene.upper(),
        "diseases": diseases,
        "clinvar_summary": clinvar_summary,
        "top_variants": clinvar_variants
    })
