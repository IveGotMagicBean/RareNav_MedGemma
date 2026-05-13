"""
HPO (Human Phenotype Ontology) Service
======================================

Loads the HPO ontology and exposes two retrieval surfaces:

  - Lexical lookup (substring / exact match) — fast, deterministic, used for
    exact term-name matches and as a fallback when the dense index is missing.
  - Semantic retrieval (`HPORagIndex`) — sentence-transformer embeddings over
    every term's name + synonyms + first-sentence definition, with cosine
    similarity ranking. This is what `map_symptoms()` calls.

The dense index is built lazily on first `load()` and persisted to disk so
subsequent starts are sub-second.
"""
import logging
import os
import re
from typing import List, Dict, Optional
from pathlib import Path

from services.hpo_rag import HPORagIndex

logger = logging.getLogger(__name__)


class HPOService:
    def __init__(self, obo_path: str, rag_cache_dir: Optional[str] = None,
                 rag_model: Optional[str] = None):
        self.obo_path = Path(obo_path)
        self.terms: Dict[str, Dict] = {}
        self.name_to_id: Dict[str, str] = {}
        self.synonym_to_id: Dict[str, str] = {}
        self.loaded = False

        # Where to put the embedding cache. Default: alongside the .obo file.
        cache_root = Path(rag_cache_dir) if rag_cache_dir else self.obo_path.parent
        self._rag_cache_path = cache_root / "hpo_embeddings.npz"
        self._rag_model_name = (
            rag_model
            or os.environ.get("HPO_RAG_MODEL")
            or "sentence-transformers/all-MiniLM-L6-v2"
        )
        # Sentence-transformers model cache (HF hub layout)
        self._st_cache = os.environ.get(
            "SENTENCE_TRANSFORMERS_HOME",
            "/data/home/fanglab/linshiyi/.cache/huggingface/sentence_transformers",
        )
        self.rag: Optional[HPORagIndex] = None

    def load(self):
        if not self.obo_path.exists():
            logger.warning(f"HPO OBO file not found: {self.obo_path}. Using built-in phenotype data.")
            self._load_builtin_terms()
            self.loaded = True
            self._build_rag()
            return

        logger.info(f"Loading HPO from {self.obo_path}...")
        self._parse_obo(self.obo_path)
        self.loaded = True
        logger.info(f"Loaded {len(self.terms)} HPO terms")
        self._build_rag()

    def _build_rag(self):
        try:
            self.rag = HPORagIndex(
                terms=self.terms,
                model_name=self._rag_model_name,
                cache_dir=self._st_cache,
                embedding_cache=str(self._rag_cache_path),
            )
            self.rag.build()
        except Exception as e:
            logger.warning(f"HPO RAG init failed ({e}); semantic search disabled, "
                           f"falling back to substring matching.")
            self.rag = None

    def _parse_obo(self, path: Path):
        current_term = {}
        in_term = False

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "[Term]":
                    if current_term and current_term.get("id", "").startswith("HP:"):
                        self._add_term(current_term)
                    current_term = {}
                    in_term = True
                elif line == "" and in_term:
                    in_term = False
                elif in_term:
                    if line.startswith("id: "):
                        current_term["id"] = line[4:]
                    elif line.startswith("name: "):
                        current_term["name"] = line[6:]
                    elif line.startswith("def: "):
                        current_term["def"] = line[5:]
                    elif line.startswith("synonym: "):
                        if "synonyms" not in current_term:
                            current_term["synonyms"] = []
                        m = re.match(r'synonym: "([^"]+)"', line)
                        if m:
                            current_term["synonyms"].append(m.group(1))
                    elif line.startswith("is_a: "):
                        if "parents" not in current_term:
                            current_term["parents"] = []
                        m = re.match(r'is_a: (HP:\d+)', line)
                        if m:
                            current_term["parents"].append(m.group(1))

        if current_term and current_term.get("id", "").startswith("HP:"):
            self._add_term(current_term)

    def _add_term(self, term: Dict):
        hp_id = term["id"]
        name = term.get("name", "")
        self.terms[hp_id] = term
        if name:
            self.name_to_id[name.lower()] = hp_id
        for syn in term.get("synonyms", []):
            self.synonym_to_id[syn.lower()] = hp_id

    def _load_builtin_terms(self):
        """Comprehensive built-in HPO terms for demo mode"""
        builtin = [
            # Neurological
            {"id": "HP:0001250", "name": "Seizures", "category": "Neurological",
             "def": "Paroxysmal events due to abnormal electrical activity in the brain"},
            {"id": "HP:0001251", "name": "Ataxia", "category": "Neurological",
             "def": "Impairment of the ability to perform smoothly coordinated voluntary movements"},
            {"id": "HP:0000726", "name": "Dementia", "category": "Neurological",
             "def": "A loss of global cognitive ability"},
            {"id": "HP:0002322", "name": "Resting tremor", "category": "Neurological",
             "def": "Tremor present at rest"},
            {"id": "HP:0001257", "name": "Spasticity", "category": "Neurological",
             "def": "Velocity-dependent increase in muscle tone"},
            {"id": "HP:0002376", "name": "Developmental regression", "category": "Neurological",
             "def": "Loss of developmental milestones"},
            {"id": "HP:0001263", "name": "Global developmental delay", "category": "Neurological",
             "def": "Significant delay in multiple developmental domains"},
            # Musculoskeletal
            {"id": "HP:0001382", "name": "Joint hypermobility", "category": "Musculoskeletal",
             "def": "The ability to move joints beyond the normal range of motion"},
            {"id": "HP:0000924", "name": "Abnormality of the skeletal system", "category": "Musculoskeletal",
             "def": "Abnormality of the skeletal system"},
            {"id": "HP:0003236", "name": "Elevated serum creatine kinase", "category": "Musculoskeletal",
             "def": "Elevated level of creatine kinase in blood"},
            {"id": "HP:0001324", "name": "Muscle weakness", "category": "Musculoskeletal",
             "def": "Reduced strength of one or more muscles"},
            {"id": "HP:0009830", "name": "Peripheral neuropathy", "category": "Musculoskeletal",
             "def": "Dysfunction of peripheral nerves"},
            # Cardiovascular
            {"id": "HP:0001638", "name": "Cardiomyopathy", "category": "Cardiovascular",
             "def": "A myocardial disorder in which the heart muscle is structurally and functionally abnormal"},
            {"id": "HP:0001659", "name": "Aortic regurgitation", "category": "Cardiovascular",
             "def": "Insufficiency of the aortic valve resulting in flow of blood from the aorta back into the left ventricle"},
            {"id": "HP:0001977", "name": "Abnormal thrombosis", "category": "Cardiovascular",
             "def": "Abnormal formation of thrombi"},
            {"id": "HP:0004942", "name": "Aortic aneurysm", "category": "Cardiovascular",
             "def": "Aneurysm of the aorta"},
            # Metabolic
            {"id": "HP:0001508", "name": "Failure to thrive", "category": "Metabolic",
             "def": "Failure to thrive (FTT) refers to failure to gain weight appropriately in infancy"},
            {"id": "HP:0001988", "name": "Hypoglycemia", "category": "Metabolic",
             "def": "A blood glucose level below the normal range"},
            {"id": "HP:0001943", "name": "Hyperlipidemia", "category": "Metabolic",
             "def": "An excess of lipids or fats in the blood"},
            {"id": "HP:0003119", "name": "Abnormality of lipid metabolism", "category": "Metabolic",
             "def": "Deviation from the normal metabolism of lipids"},
            # Renal
            {"id": "HP:0000077", "name": "Abnormality of the kidney", "category": "Renal",
             "def": "An abnormality of the kidney"},
            {"id": "HP:0000093", "name": "Proteinuria", "category": "Renal",
             "def": "Excess protein in the urine"},
            {"id": "HP:0003774", "name": "End-stage renal disease", "category": "Renal",
             "def": "Kidney failure requiring dialysis or transplantation"},
            # Ophthalmological
            {"id": "HP:0001087", "name": "Lens subluxation", "category": "Ophthalmological",
             "def": "Partial displacement of the lens"},
            {"id": "HP:0000518", "name": "Cataract", "category": "Ophthalmological",
             "def": "Opacity of the lens of the eye"},
            {"id": "HP:0000505", "name": "Visual impairment", "category": "Ophthalmological",
             "def": "Visual impairment (or vision impairment) is vision loss"},
            # Immunological
            {"id": "HP:0002721", "name": "Immunodeficiency", "category": "Immunological",
             "def": "A reduction in the ability to mount an immune response"},
            {"id": "HP:0001973", "name": "Autoimmune thrombocytopenia", "category": "Immunological",
             "def": "Thrombocytopenia due to autoimmune destruction"},
            # Dermatological
            {"id": "HP:0000992", "name": "Cutaneous photosensitivity", "category": "Dermatological",
             "def": "An increased sensitivity of the skin to light"},
            {"id": "HP:0001030", "name": "Fragile skin", "category": "Dermatological",
             "def": "Skin that tears, blisters, or scars unusually easily"},
            # Hematological
            {"id": "HP:0001871", "name": "Abnormality of blood and blood-forming tissues", "category": "Hematological",
             "def": "Abnormality of blood and blood-forming tissues"},
            {"id": "HP:0001903", "name": "Anemia", "category": "Hematological",
             "def": "A reduction in erythrocytes or hemoglobin"},
            {"id": "HP:0001744", "name": "Splenomegaly", "category": "Hematological",
             "def": "Abnormal increased size of the spleen"},
            {"id": "HP:0002240", "name": "Hepatomegaly", "category": "Hematological",
             "def": "Enlargement of the liver"},
            # Craniofacial
            {"id": "HP:0000272", "name": "Malar flattening", "category": "Craniofacial",
             "def": "Underdevelopment of the malar bones"},
            {"id": "HP:0000347", "name": "Micrognathia", "category": "Craniofacial",
             "def": "Abnormally small lower jaw"},
        ]
        for t in builtin:
            self.terms[t["id"]] = t
            self.name_to_id[t["name"].lower()] = t["id"]

    def get_count(self) -> int:
        return len(self.terms)

    def search_symptoms(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search HPO terms by text query. Combines exact lexical match (for
        precision on canonical names) with dense semantic retrieval (for
        recall on free-text descriptions).
        """
        query_lower = (query or "").strip().lower()
        if not query_lower:
            return []

        results: List[Dict] = []
        seen: set = set()

        # 1. Exact name match (high precision)
        hp_id = self.name_to_id.get(query_lower)
        if hp_id and hp_id not in seen:
            results.append(self.terms[hp_id])
            seen.add(hp_id)

        # 2. Exact synonym match
        sy_id = self.synonym_to_id.get(query_lower)
        if sy_id and sy_id not in seen:
            results.append(self.terms[sy_id])
            seen.add(sy_id)

        # 3. Dense semantic retrieval (covers paraphrase / multi-word queries)
        if self.rag and self.rag.loaded and not self.rag.use_demo:
            for hit in self.rag.search(query, top_k=limit, min_score=0.30):
                hp_id = hit["id"]
                if hp_id in seen:
                    continue
                term = self.terms.get(hp_id)
                if not term:
                    continue
                annotated = dict(term)
                annotated["_score"] = hit["score"]
                annotated["_matched_surface"] = hit["matched_surface"]
                annotated["_matched_kind"] = hit["matched_kind"]
                results.append(annotated)
                seen.add(hp_id)
                if len(results) >= limit:
                    break

        # 4. Substring fallback if both above came up empty
        if len(results) < limit:
            for name, hp_id in self.name_to_id.items():
                if hp_id in seen:
                    continue
                if query_lower in name:
                    results.append(self.terms[hp_id])
                    seen.add(hp_id)
                    if len(results) >= limit:
                        break

        return results[:limit]

    def map_symptoms(self, symptoms: List[str], top_k: int = 3) -> Dict:
        """
        Map a list of free-text symptoms to standardised HPO terms using the
        dense semantic index. Returns a structured payload the Agent can use
        and trace back to the user.

        Output schema:
            {
              "mapped": [
                { "input": "走路无力",
                  "term": "Difficulty walking",
                  "hp_id": "HP:0002355",
                  "score": 0.81,
                  "matched_surface": "Difficulty walking",
                  "matched_kind": "name",
                  "definition": "...",
                  "synonyms": [...] },
                ...
              ],
              "unmapped": ["..."],
              "engine": "rag" | "substring",
            }
        """
        out_mapped: List[Dict] = []
        unmapped: List[str] = []
        clean = [s.strip() for s in (symptoms or []) if s and s.strip()]
        if not clean:
            return {"mapped": [], "unmapped": [], "engine": "none"}

        engine = "substring"
        if self.rag and self.rag.loaded and not self.rag.use_demo:
            engine = "rag"
            multi = self.rag.search_multi(clean, top_k_per_symptom=top_k)
            for sym in clean:
                hits = multi.get(sym, [])
                if not hits:
                    unmapped.append(sym)
                    continue
                # Keep the best hit per input symptom plus the next 1–2 as
                # alternative candidates the LLM may consider.
                primary = hits[0]
                out_mapped.append({
                    "input": sym,
                    "term": primary["name"],
                    "hp_id": primary["id"],
                    "score": primary["score"],
                    "matched_surface": primary["matched_surface"],
                    "matched_kind": primary["matched_kind"],
                    "definition": primary["definition"],
                    "synonyms": primary["synonyms"],
                    "alternatives": [
                        {"term": h["name"], "hp_id": h["id"], "score": h["score"]}
                        for h in hits[1:]
                    ],
                })
            return {"mapped": out_mapped, "unmapped": unmapped, "engine": engine}

        # Substring fallback
        for sym in clean:
            matches = self.search_symptoms(sym, limit=1)
            if matches:
                t = matches[0]
                out_mapped.append({
                    "input": sym,
                    "term": t.get("name", ""),
                    "hp_id": t.get("id", ""),
                    "score": 1.0 if t.get("name", "").lower() == sym.lower() else 0.5,
                    "matched_surface": t.get("name", ""),
                    "matched_kind": "substring",
                    "definition": t.get("def", ""),
                    "synonyms": t.get("synonyms", [])[:3],
                    "alternatives": [],
                })
            else:
                unmapped.append(sym)
        return {"mapped": out_mapped, "unmapped": unmapped, "engine": engine}

    def get_term(self, hp_id: str) -> Optional[Dict]:
        return self.terms.get(hp_id)

    def get_all_terms_list(self) -> List[Dict]:
        """Return all terms as list for frontend autocomplete"""
        return [
            {"id": t["id"], "name": t["name"],
             "category": t.get("category", "General"),
             "definition": t.get("def", "")}
            for t in self.terms.values()
        ]

    def map_text_to_hpo(self, text: str) -> List[Dict]:
        """Map free text to HPO terms using keyword matching"""
        words = text.lower().split()
        found = set()
        results = []

        for i in range(len(words)):
            for j in range(i + 1, min(i + 5, len(words) + 1)):
                phrase = " ".join(words[i:j])
                if phrase in self.name_to_id and self.name_to_id[phrase] not in found:
                    hp_id = self.name_to_id[phrase]
                    found.add(hp_id)
                    results.append(self.terms[hp_id])

        return results
