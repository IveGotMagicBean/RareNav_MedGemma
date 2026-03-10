"""Diagnosis API - Integrated diagnosis reasoning"""
from flask import Blueprint, request, jsonify, current_app

diagnosis_bp = Blueprint("diagnosis", __name__)

# Rare disease knowledge base (curated subset for demo)
RARE_DISEASE_DB = [
    {
        "id": "ORPHA:586", "name": "Cystic Fibrosis", "omim": "219700",
        "gene": "CFTR", "inheritance": "Autosomal recessive",
        "prevalence": "1/2,500 (European)",
        "key_symptoms": ["recurrent lung infections", "chronic cough", "failure to thrive",
                         "malnutrition", "infertility", "salty sweat", "pancreatic insufficiency"],
        "diagnosis": "Sweat chloride test, CFTR genetic panel",
        "treatments": ["CFTR modulators (ivacaftor, elexacaftor/tezacaftor)", "Chest physiotherapy", "Enzyme replacement"],
        "specialists": ["Pulmonology", "Gastroenterology", "Genetics"],
        "urgency": "high"
    },
    {
        "id": "ORPHA:435", "name": "Marfan Syndrome", "omim": "154700",
        "gene": "FBN1", "inheritance": "Autosomal dominant",
        "prevalence": "1/5,000",
        "key_symptoms": ["tall stature", "long limbs", "arachnodactyly", "lens dislocation",
                         "aortic aneurysm", "joint hypermobility", "scoliosis", "pectus deformity"],
        "diagnosis": "Clinical criteria (Ghent nosology), FBN1 genetic testing, Echocardiography",
        "treatments": ["Beta-blockers (aortic protection)", "Losartan", "Surgical aortic repair"],
        "specialists": ["Cardiology", "Ophthalmology", "Orthopedics", "Genetics"],
        "urgency": "high"
    },
    {
        "id": "ORPHA:548", "name": "Gaucher Disease Type 1", "omim": "230800",
        "gene": "GBA", "inheritance": "Autosomal recessive",
        "prevalence": "1/40,000 (1/850 Ashkenazi Jewish)",
        "key_symptoms": ["splenomegaly", "hepatomegaly", "anemia", "thrombocytopenia",
                         "bone pain", "fatigue", "easy bruising"],
        "diagnosis": "Beta-glucocerebrosidase enzyme activity, GBA sequencing",
        "treatments": ["Enzyme replacement therapy (imiglucerase)", "Substrate reduction therapy (miglustat)"],
        "specialists": ["Hematology", "Genetics", "Hepatology"],
        "urgency": "medium"
    },
    {
        "id": "ORPHA:727", "name": "Fabry Disease", "omim": "301500",
        "gene": "GLA", "inheritance": "X-linked",
        "prevalence": "1/40,000–1/117,000",
        "key_symptoms": ["neuropathic pain", "angiokeratoma", "hypohidrosis", "corneal opacity",
                         "cardiomyopathy", "renal failure", "stroke"],
        "diagnosis": "Alpha-galactosidase A enzyme activity, GLA sequencing",
        "treatments": ["Enzyme replacement therapy (agalsidase)", "Migalastat (amenable mutations)"],
        "specialists": ["Nephrology", "Cardiology", "Neurology", "Genetics"],
        "urgency": "high"
    },
    {
        "id": "ORPHA:648", "name": "Phenylketonuria (PKU)", "omim": "261600",
        "gene": "PAH", "inheritance": "Autosomal recessive",
        "prevalence": "1/10,000–1/15,000",
        "key_symptoms": ["intellectual disability", "behavioral problems", "seizures",
                         "fair skin", "musty odor", "microcephaly"],
        "diagnosis": "Newborn screening (Phe levels), PAH sequencing",
        "treatments": ["Low-phenylalanine diet", "Sapropterin (BH4)", "Pegvaliase"],
        "specialists": ["Metabolic medicine", "Neurology", "Dietetics", "Genetics"],
        "urgency": "critical"
    },
    {
        "id": "ORPHA:79233", "name": "Ehlers-Danlos Syndrome (Classical)", "omim": "130000",
        "gene": "COL5A1/COL5A2", "inheritance": "Autosomal dominant",
        "prevalence": "1/20,000–1/40,000",
        "key_symptoms": ["joint hypermobility", "skin hyperextensibility", "fragile skin",
                         "easy bruising", "poor wound healing", "chronic pain"],
        "diagnosis": "Clinical criteria, collagen gene panel, skin biopsy",
        "treatments": ["Physical therapy", "Pain management", "Wound care", "Joint protection"],
        "specialists": ["Rheumatology", "Genetics", "Orthopedics", "Dermatology"],
        "urgency": "medium"
    },
    {
        "id": "ORPHA:280", "name": "Hereditary Hemochromatosis", "omim": "235200",
        "gene": "HFE", "inheritance": "Autosomal recessive",
        "prevalence": "1/200–1/400 (Northern European)",
        "key_symptoms": ["fatigue", "joint pain", "abdominal pain", "liver disease",
                         "diabetes", "skin bronzing", "cardiac arrhythmia", "hypogonadism"],
        "diagnosis": "Transferrin saturation, serum ferritin, HFE C282Y/H63D testing, liver biopsy",
        "treatments": ["Therapeutic phlebotomy", "Chelation therapy"],
        "specialists": ["Hepatology", "Hematology", "Genetics", "Endocrinology"],
        "urgency": "medium"
    },
    {
        "id": "ORPHA:791", "name": "Retinitis Pigmentosa", "omim": "268000",
        "gene": "Multiple (RP1, RPGR, USH2A, etc.)", "inheritance": "Multiple patterns",
        "prevalence": "1/3,500–1/4,000",
        "key_symptoms": ["night blindness", "visual field loss", "reduced visual acuity",
                         "photophobia", "color vision defects"],
        "diagnosis": "Ophthalmologic exam, ERG, genetic panel for RP genes",
        "treatments": ["Vitamin A supplementation", "Gene therapy (RPE65)", "Low vision aids"],
        "specialists": ["Ophthalmology", "Genetics"],
        "urgency": "medium"
    },
    {
        "id": "ORPHA:908", "name": "Tuberous Sclerosis Complex", "omim": "191100",
        "gene": "TSC1/TSC2", "inheritance": "Autosomal dominant",
        "prevalence": "1/6,000–1/10,000",
        "key_symptoms": ["seizures", "intellectual disability", "skin lesions", "cardiac rhabdomyoma",
                         "renal angiomyolipoma", "pulmonary LAM", "brain tubers"],
        "diagnosis": "Clinical criteria, brain/renal/cardiac imaging, TSC1/TSC2 sequencing",
        "treatments": ["mTOR inhibitors (everolimus)", "Antiepileptics", "Organ-specific management"],
        "specialists": ["Neurology", "Nephrology", "Dermatology", "Pulmonology", "Genetics"],
        "urgency": "high"
    },
    {
        "id": "ORPHA:ADPKD", "name": "Autosomal Dominant PKD", "omim": "173900",
        "gene": "PKD1/PKD2", "inheritance": "Autosomal dominant",
        "prevalence": "1/400–1/1,000",
        "key_symptoms": ["flank pain", "hematuria", "hypertension", "renal cysts",
                         "intracranial aneurysm", "liver cysts", "proteinuria"],
        "diagnosis": "Renal ultrasound, CT/MRI, PKD1/PKD2 genetic testing",
        "treatments": ["Tolvaptan (aquaretic)", "Blood pressure control", "Pain management", "Dialysis/Transplant"],
        "specialists": ["Nephrology", "Genetics", "Urology"],
        "urgency": "medium"
    },
]


def calculate_symptom_match(symptoms: list, disease: dict) -> float:
    """Calculate symptom overlap score"""
    if not symptoms:
        return 0.0
    key_syms = [s.lower() for s in disease["key_symptoms"]]
    user_syms = [s.lower() for s in symptoms]
    
    matches = 0
    for us in user_syms:
        for ks in key_syms:
            if us in ks or ks in us or any(word in ks for word in us.split() if len(word) > 3):
                matches += 1
                break
    
    return min(1.0, matches / max(len(key_syms) * 0.5, 1))


@diagnosis_bp.route("/symptom-based", methods=["POST"])
def symptom_based_diagnosis():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    age = data.get("age")
    sex = data.get("sex")

    if not symptoms:
        return jsonify({"error": "symptoms required"}), 400

    # Score diseases
    scored = []
    for disease in RARE_DISEASE_DB:
        score = calculate_symptom_match(symptoms, disease)
        if score > 0:
            scored.append({**disease, "match_score": score})

    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # Get AI analysis
    medgemma = current_app.config["MEDGEMMA"]
    ai_result = medgemma.analyze_symptoms(symptoms, age, sex)

    return jsonify({
        "ranked_diseases": scored[:5],
        "ai_analysis": ai_result.get("analysis"),
        "hpo_mapping": ai_result.get("hpo_mapping", []),
        "symptom_count": len(symptoms),
        "ai_latency": ai_result.get("latency"),
        "demo_mode": ai_result.get("demo", True)
    })


@diagnosis_bp.route("/variant-based", methods=["POST"])
def variant_based_diagnosis():
    data = request.get_json()
    gene = data.get("gene", "").strip()
    variant = data.get("variant", "").strip()

    if not gene:
        return jsonify({"error": "gene required"}), 400

    clinvar = current_app.config["CLINVAR"]
    medgemma = current_app.config["MEDGEMMA"]

    # Find variant info
    records = []
    if variant:
        records = clinvar.search_by_variant(gene, variant)
    if not records:
        records = clinvar.search_by_gene(gene, 5)

    gene_summary = clinvar.get_gene_summary(gene)

    # Generate explanation
    if records:
        r = records[0]
        explanation = medgemma.explain_variant(
            r["gene"], r["name"], r["significance"], r["phenotype"]
        )
    else:
        explanation = {"explanation": f"No ClinVar records found for {gene} {variant}.", "demo": True}

    # Find matching disease in knowledge base
    related_diseases = [d for d in RARE_DISEASE_DB if d["gene"].upper().startswith(gene.upper())]

    return jsonify({
        "variant_records": records,
        "gene_summary": gene_summary,
        "ai_explanation": explanation.get("explanation"),
        "related_diseases": related_diseases,
        "ai_latency": explanation.get("latency"),
        "demo_mode": explanation.get("demo", True)
    })


@diagnosis_bp.route("/report", methods=["POST"])
def generate_report():
    data = request.get_json()
    patient_data = data.get("patient", {})
    variant_data = data.get("variant")
    symptom_data = data.get("symptoms")

    medgemma = current_app.config["MEDGEMMA"]
    result = medgemma.generate_diagnostic_report(patient_data, variant_data, symptom_data)
    return jsonify(result)


@diagnosis_bp.route("/disease-list", methods=["GET"])
def disease_list():
    return jsonify({
        "diseases": RARE_DISEASE_DB,
        "count": len(RARE_DISEASE_DB)
    })
