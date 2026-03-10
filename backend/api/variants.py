"""Variants API - ClinVar queries and variant explanation"""
from flask import Blueprint, request, jsonify, current_app

variants_bp = Blueprint("variants", __name__)


@variants_bp.route("/search", methods=["GET"])
def search_variants():
    gene = request.args.get("gene", "").strip()
    variant = request.args.get("variant", "").strip()
    disease = request.args.get("disease", "").strip()
    limit = int(request.args.get("limit", 20))

    clinvar = current_app.config["CLINVAR"]

    if disease:
        results = clinvar.search_by_disease(disease, limit)
    elif gene and variant:
        results = clinvar.search_by_variant(gene, variant)
    elif gene:
        results = clinvar.search_by_gene(gene, limit)
    else:
        return jsonify({"error": "Provide gene, variant, or disease parameter"}), 400

    return jsonify({"results": results, "count": len(results)})


@variants_bp.route("/explain", methods=["POST"])
def explain_variant():
    data = request.get_json()
    gene = data.get("gene", "").strip()
    variant = data.get("variant", "").strip()
    significance = data.get("significance", "")
    disease = data.get("disease", "")

    if not gene or not variant:
        return jsonify({"error": "gene and variant required"}), 400

    clinvar = current_app.config["CLINVAR"]
    medgemma = current_app.config["MEDGEMMA"]

    # Fetch from ClinVar if not provided
    if not significance or not disease:
        records = clinvar.search_by_variant(gene, variant)
        if records:
            significance = significance or records[0]["significance"]
            disease = disease or records[0]["phenotype"]

    result = medgemma.explain_variant(gene, variant, significance, disease)
    return jsonify(result)


@variants_bp.route("/gene-summary/<gene>", methods=["GET"])
def gene_summary(gene):
    clinvar = current_app.config["CLINVAR"]
    summary = clinvar.get_gene_summary(gene)
    return jsonify(summary)


@variants_bp.route("/statistics", methods=["GET"])
def statistics():
    clinvar = current_app.config["CLINVAR"]
    return jsonify(clinvar.get_statistics())


@variants_bp.route("/parse", methods=["POST"])
def parse_variant():
    """Parse variant string into components"""
    data = request.get_json()
    variant_str = data.get("input", "").strip()

    import re
    result = {"original": variant_str, "parsed": False}

    # GENE VARIANT (space)
    m = re.match(r'^([A-Z][A-Z0-9]+)\s+(.+)$', variant_str, re.IGNORECASE)
    if m:
        result.update({"gene": m.group(1).upper(), "variant": m.group(2), "parsed": True})
        return jsonify(result)

    # GENE:VARIANT
    m = re.match(r'^([A-Z][A-Z0-9]+):(.+)$', variant_str, re.IGNORECASE)
    if m:
        result.update({"gene": m.group(1).upper(), "variant": m.group(2), "parsed": True})
        return jsonify(result)

    return jsonify(result)
