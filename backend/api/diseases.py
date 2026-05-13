"""
Diseases API
============

Disease library exposed to the frontend. Builds an aggregated catalog from
two sources:

  1. RARE_DISEASE_DB   — 10 hand-curated entries with full clinical detail
                         (key symptoms, treatments, specialists, urgency).
  2. Phenomizer.disease_meta — every OMIM/ORPHANET/DECIPHER disease that
                         HPO's phenotype.hpoa annotates (≈8,500 entries).

The hand-curated entries take precedence when there is an ID overlap; for
all other diseases we return a slim record (id/name/omim/gene/HPO terms)
that is still rich enough to drive the library UI and serves as the
endpoint for an "8,500+ diseases" claim.
"""

from flask import Blueprint, request, jsonify, current_app
from .diagnosis import RARE_DISEASE_DB

diseases_bp = Blueprint("diseases", __name__)


def _slim_record_from_phenomizer(disease_id: str, phen) -> dict:
    """
    Build a slim disease record from Phenomizer's curated annotations.
    No clinical narrative — just the structured facts pulled from HPO.
    """
    meta = phen.disease_meta.get(disease_id, {}) if phen else {}
    hpo_terms = phen.disease_to_hpo.get(disease_id, set()) if phen else set()
    genes = sorted(phen.disease_to_genes.get(disease_id, set())) if phen else []

    # Pick the most informative HPO terms as "key symptoms"
    if phen and phen.ic:
        sorted_hpo = sorted(hpo_terms, key=lambda t: -phen.ic.get(t, 0))[:8]
    else:
        sorted_hpo = list(hpo_terms)[:8]
    key_symptoms = []
    seen_names = set()
    for hp_id in sorted_hpo:
        t = phen.hpo_service.terms.get(hp_id, {}) if phen else {}
        name = (t.get("name") or "").lower()
        if name and name not in seen_names:
            key_symptoms.append(name)
            seen_names.add(name)

    return {
        "id": disease_id,
        "name": meta.get("name", disease_id),
        "omim": meta.get("omim", ""),
        "source": meta.get("source", ""),
        "gene": ", ".join(genes[:3]),
        "genes": genes,
        "inheritance": "",
        "prevalence": "",
        "key_symptoms": key_symptoms,
        "hpo_terms": [
            {"id": hp_id,
             "name": (phen.hpo_service.terms.get(hp_id, {}).get("name", hp_id)
                      if phen else hp_id)}
            for hp_id in sorted_hpo
        ],
        "diagnosis": "See HPO/OMIM",
        "treatments": [],
        "specialists": [],
        "urgency": "",
        "curated": False,
        "url": (f"https://omim.org/entry/{meta.get('omim')}"
                if meta.get("omim")
                else f"https://hpo.jax.org/app/browse/disease/{disease_id}"),
    }


def _build_catalog():
    """
    Merge RARE_DISEASE_DB (curated) with Phenomizer disease_meta (derived).
    """
    phen = current_app.config.get("PHENOMIZER")
    catalog = []
    seen_ids = set()
    seen_omim = set()

    # 1. Curated entries first (always shown)
    for d in RARE_DISEASE_DB:
        entry = dict(d)
        entry["curated"] = True
        catalog.append(entry)
        seen_ids.add(entry["id"])
        if entry.get("omim"):
            seen_omim.add(entry["omim"])

    # 2. Phenomizer-derived entries
    if phen and phen.loaded and not phen.use_demo:
        for disease_id in phen.disease_meta.keys():
            if disease_id in seen_ids:
                continue
            meta = phen.disease_meta[disease_id]
            if meta.get("omim") and meta["omim"] in seen_omim:
                continue
            # Skip diseases with zero gene annotations and < 3 phenotype terms
            # — these are stubs that aren't useful in the library view.
            if len(phen.disease_to_hpo.get(disease_id, set())) < 3:
                continue
            catalog.append(_slim_record_from_phenomizer(disease_id, phen))

    return catalog


@diseases_bp.route("/", methods=["GET"])
def list_diseases():
    search = request.args.get("q", "").lower()
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 1000))

    catalog = _build_catalog()

    if search:
        filtered = []
        for d in catalog:
            if (search in d["name"].lower()
                or search in (d.get("gene") or "").lower()
                or any(search in s.lower() for s in d.get("key_symptoms", []))
                or any(search in g.lower() for g in d.get("genes", []))):
                filtered.append(d)
    else:
        filtered = catalog

    # Curated entries first, then derived
    filtered.sort(key=lambda d: (not d.get("curated"), d["name"].lower()))

    return jsonify({
        "diseases": filtered[:limit],
        "count": len(filtered),
        "total_in_catalog": len(catalog),
        "curated_count": sum(1 for d in catalog if d.get("curated")),
    })


@diseases_bp.route("/<path:disease_id>", methods=["GET"])
def get_disease(disease_id):
    # 1. Look in curated DB by id
    disease = next((d for d in RARE_DISEASE_DB if d["id"] == disease_id), None)

    # 2. Try by slug
    if not disease:
        disease = next((d for d in RARE_DISEASE_DB
                        if d["name"].lower().replace(" ", "-") == disease_id.lower()),
                       None)
    if disease:
        out = dict(disease)
        out["curated"] = True
        # Enrich with HPO terms if Phenomizer knows about this disease
        phen = current_app.config.get("PHENOMIZER")
        if phen and phen.loaded and not phen.use_demo:
            hpo_terms = phen.disease_to_hpo.get(out["id"], set())
            if hpo_terms and phen.ic:
                sorted_hpo = sorted(hpo_terms, key=lambda t: -phen.ic.get(t, 0))[:15]
                out["hpo_terms"] = [
                    {"id": hp,
                     "name": phen.hpo_service.terms.get(hp, {}).get("name", hp),
                     "ic": round(phen.ic.get(hp, 0), 2)}
                    for hp in sorted_hpo
                ]
        return jsonify(out)

    # 3. Phenomizer-derived (no curated entry)
    phen = current_app.config.get("PHENOMIZER")
    if phen and phen.loaded and not phen.use_demo and disease_id in phen.disease_meta:
        return jsonify(_slim_record_from_phenomizer(disease_id, phen))

    return jsonify({"error": "Disease not found"}), 404


@diseases_bp.route("/by-gene/<gene>", methods=["GET"])
def by_gene(gene):
    gene_u = gene.upper()
    diseases = [d for d in RARE_DISEASE_DB if gene_u in (d.get("gene") or "").upper()]

    # Add Phenomizer-derived diseases linked to this gene
    phen = current_app.config.get("PHENOMIZER")
    if phen and phen.loaded and not phen.use_demo:
        seen = {d["id"] for d in diseases}
        for disease_id in sorted(phen.gene_to_diseases.get(gene_u, set())):
            if disease_id in seen:
                continue
            diseases.append(_slim_record_from_phenomizer(disease_id, phen))

    clinvar = current_app.config["CLINVAR"]
    clinvar_summary = clinvar.get_gene_summary(gene)
    clinvar_variants = clinvar.search_by_gene(gene, 10)

    return jsonify({
        "gene": gene_u,
        "diseases": diseases,
        "clinvar_summary": clinvar_summary,
        "top_variants": clinvar_variants,
    })
