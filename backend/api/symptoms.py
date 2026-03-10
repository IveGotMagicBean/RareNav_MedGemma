"""Symptoms API - HPO search and symptom analysis"""
from flask import Blueprint, request, jsonify, current_app

symptoms_bp = Blueprint("symptoms", __name__)


@symptoms_bp.route("/search", methods=["GET"])
def search_symptoms():
    query = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 10))

    if not query:
        return jsonify({"error": "q parameter required"}), 400

    hpo = current_app.config["HPO"]
    results = hpo.search_symptoms(query, limit)
    return jsonify({"results": results, "count": len(results)})


@symptoms_bp.route("/all-terms", methods=["GET"])
def all_terms():
    hpo = current_app.config["HPO"]
    terms = hpo.get_all_terms_list()
    return jsonify({"terms": terms, "count": len(terms)})


@symptoms_bp.route("/analyze", methods=["POST"])
def analyze_symptoms():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    age = data.get("age")
    sex = data.get("sex")
    family_history = data.get("family_history")
    onset = data.get("onset")

    if not symptoms:
        return jsonify({"error": "symptoms array required"}), 400

    medgemma = current_app.config["MEDGEMMA"]
    result = medgemma.analyze_symptoms(symptoms, age, sex, family_history)

    # Also map to HPO terms
    hpo = current_app.config["HPO"]
    hpo_terms = []
    for symptom in symptoms:
        matches = hpo.search_symptoms(symptom, 3)
        if matches:
            hpo_terms.append({
                "symptom": symptom,
                "hpo_term": matches[0]["name"],
                "hpo_id": matches[0]["id"]
            })

    result["hpo_mapping"] = hpo_terms
    result["symptom_count"] = len(symptoms)

    return jsonify(result)


@symptoms_bp.route("/map-text", methods=["POST"])
def map_text_to_hpo():
    """Map free text description to HPO terms"""
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400

    hpo = current_app.config["HPO"]
    terms = hpo.map_text_to_hpo(text)
    return jsonify({"terms": terms, "text": text})
