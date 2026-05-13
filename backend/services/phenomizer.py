"""
Phenomizer-lite: HPO Phenotype Similarity for Differential Diagnosis
====================================================================

Given a set of patient HPO terms, rank candidate Mendelian diseases by how
well their published phenotypic profile matches the query.

This is a faithful implementation of the symmetric Resnik/Lin similarity used
in the original Phenomizer (Köhler et al., AJHG 2009) and downstream tools
such as Exomiser/LIRICAL. It is not a learned model — it is information-
theoretic over the HPO DAG and the gold-standard disease-phenotype
annotations (phenotype.hpoa).

Pipeline:
    1. Parse phenotype.hpoa            → (disease, hpo_term) pairs + meta
    2. Build ancestor closure          → expand annotations up the is-a DAG
    3. Information content per term    → IC(t) = -log(P(t) | diseases)
    4. Symmetric pairwise similarity   → max IC(LCA(t1, t2))
    5. Disease scoring                 → bidirectional avg-of-max

All structures are cached to disk so subsequent starts read a single .npz.

References:
    Köhler S, et al. "Clinical diagnostics in human genetics with semantic
    similarity searches in ontologies." AJHG 2009;85(4):457-464.
    Smedley D, et al. "Next-generation diagnostics and disease-gene discovery
    with the Exomiser." Nat Protoc 2015;10(12):2004-2015.
"""

from __future__ import annotations

import logging
import math
import os
import pickle
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class PhenomizerService:
    def __init__(
        self,
        hpo_service,
        hpoa_path: str,
        genes_to_phenotype_path: Optional[str] = None,
        cache_path: Optional[str] = None,
    ):
        self.hpo_service = hpo_service
        self.hpoa_path = Path(hpoa_path)
        self.gp_path = Path(genes_to_phenotype_path) if genes_to_phenotype_path else None
        self.cache_path = Path(cache_path) if cache_path else (
            self.hpoa_path.parent / "phenomizer_cache.pkl"
        )

        self.disease_to_hpo: Dict[str, Set[str]] = {}
        self.hpo_to_diseases: Dict[str, Set[str]] = defaultdict(set)
        self.disease_meta: Dict[str, Dict] = {}
        self.gene_to_diseases: Dict[str, Set[str]] = defaultdict(set)
        self.disease_to_genes: Dict[str, Set[str]] = defaultdict(set)
        self.ancestors: Dict[str, Set[str]] = {}
        self.ic: Dict[str, float] = {}

        self.n_diseases: int = 0
        self.loaded: bool = False
        self.use_demo: bool = False

    # ── Build ──────────────────────────────────────────────────────────
    def _build_ancestor_closure(self) -> None:
        """For every HPO term, compute the set of ancestors (incl. itself)."""
        terms = self.hpo_service.terms
        cache: Dict[str, Set[str]] = {}

        def collect(node: str) -> Set[str]:
            if node in cache:
                return cache[node]
            term = terms.get(node)
            if not term:
                cache[node] = {node}
                return cache[node]
            anc = {node}
            for parent in term.get("parents", []) or []:
                anc |= collect(parent)
            cache[node] = anc
            return anc

        for hp_id in terms.keys():
            collect(hp_id)
        self.ancestors = cache
        logger.info(f"Phenomizer: ancestor closure for {len(self.ancestors):,} HPO terms")

    def _parse_hpoa(self) -> None:
        """
        phenotype.hpoa is TSV with header:
            database_id  disease_name  qualifier  hpo_id  reference  evidence  ...

        We only need (database_id, disease_name, hpo_id) for terms with
        no negative qualifier ('NOT' means 'absent', skip).
        """
        if not self.hpoa_path.exists():
            raise FileNotFoundError(f"phenotype.hpoa missing: {self.hpoa_path}")

        n_rows = 0
        with open(self.hpoa_path, "r", encoding="utf-8") as f:
            header = None
            for line in f:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                cols = line.split("\t")
                if header is None:
                    header = [c.strip().lower() for c in cols]
                    continue
                row = dict(zip(header, cols))
                disease_id = (row.get("database_id") or "").strip()
                disease_name = (row.get("disease_name") or "").strip()
                qualifier = (row.get("qualifier") or "").strip().upper()
                hpo_id = (row.get("hpo_id") or "").strip()
                if not disease_id or not hpo_id:
                    continue
                if qualifier == "NOT":
                    continue   # phenotype explicitly absent
                if hpo_id not in self.ancestors:
                    # phenotype.hpoa sometimes references obsolete IDs
                    continue
                self.disease_to_hpo.setdefault(disease_id, set()).add(hpo_id)
                if disease_id not in self.disease_meta:
                    self.disease_meta[disease_id] = {
                        "id": disease_id,
                        "name": disease_name,
                        "source": disease_id.split(":")[0] if ":" in disease_id else "",
                        "omim": disease_id.split(":")[1] if disease_id.startswith("OMIM:") else "",
                    }
                n_rows += 1

        logger.info(
            f"Phenomizer: parsed {n_rows:,} HPOA annotations → "
            f"{len(self.disease_to_hpo):,} diseases"
        )

    def _expand_annotations(self) -> None:
        """
        Propagate disease annotations up the HPO is-a DAG so a query for a
        more specific term still matches a disease annotated with a more
        general parent (and vice versa via ancestors at query time).
        """
        expanded: Dict[str, Set[str]] = {}
        for disease, terms in self.disease_to_hpo.items():
            full = set()
            for t in terms:
                full |= self.ancestors.get(t, {t})
            expanded[disease] = full
        self.disease_to_hpo = expanded
        # Inverted index
        self.hpo_to_diseases = defaultdict(set)
        for disease, terms in self.disease_to_hpo.items():
            for t in terms:
                self.hpo_to_diseases[t].add(disease)

    def _compute_ic(self) -> None:
        """
        IC(t) = -log( frequency(t) ) where frequency is the fraction of
        diseases (after annotation propagation) whose phenotype set contains t.
        """
        n_total = max(len(self.disease_to_hpo), 1)
        self.n_diseases = n_total
        self.ic = {}
        for t, diseases in self.hpo_to_diseases.items():
            p = len(diseases) / n_total
            if p > 0:
                self.ic[t] = -math.log(p)
        logger.info(
            f"Phenomizer: IC computed for {len(self.ic):,} terms "
            f"(n_diseases={n_total:,}, max IC={max(self.ic.values()):.2f})"
        )

    def _parse_genes_to_phenotype(self) -> None:
        """
        Optional: parse genes_to_phenotype.txt to link disease → genes.
        Columns: ncbi_gene_id, gene_symbol, hpo_id, hpo_name, frequency,
                 disease_id (e.g. OMIM:219700)
        """
        if not self.gp_path or not self.gp_path.exists():
            return
        with open(self.gp_path, "r", encoding="utf-8") as f:
            header = None
            for line in f:
                if not line.strip() or line.startswith("#"):
                    continue
                cols = line.rstrip("\n").split("\t")
                if header is None:
                    header = [c.strip().lower() for c in cols]
                    continue
                row = dict(zip(header, cols))
                gene = (row.get("gene_symbol") or row.get("gene-symbol") or "").strip().upper()
                disease = (row.get("disease_id") or row.get("disease-id") or "").strip()
                if gene and disease:
                    self.gene_to_diseases[gene].add(disease)
                    self.disease_to_genes[disease].add(gene)
        logger.info(
            f"Phenomizer: {len(self.gene_to_diseases):,} genes linked to "
            f"{sum(len(v) for v in self.gene_to_diseases.values()):,} disease associations"
        )

    def _try_load_cache(self) -> bool:
        if not self.cache_path.exists():
            return False
        try:
            with open(self.cache_path, "rb") as f:
                data = pickle.load(f)
            self.disease_to_hpo = data["disease_to_hpo"]
            self.hpo_to_diseases = defaultdict(set, data["hpo_to_diseases"])
            self.disease_meta = data["disease_meta"]
            self.gene_to_diseases = defaultdict(set, data.get("gene_to_diseases", {}))
            self.disease_to_genes = defaultdict(set, data.get("disease_to_genes", {}))
            self.ancestors = data["ancestors"]
            self.ic = data["ic"]
            self.n_diseases = data["n_diseases"]
            logger.info(
                f"Phenomizer cache hit: {self.n_diseases:,} diseases, "
                f"{len(self.ic):,} term IC values"
            )
            return True
        except Exception as e:
            logger.warning(f"Phenomizer cache load failed: {e}")
            return False

    def _save_cache(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "wb") as f:
                pickle.dump({
                    "disease_to_hpo": self.disease_to_hpo,
                    "hpo_to_diseases": dict(self.hpo_to_diseases),
                    "disease_meta": self.disease_meta,
                    "gene_to_diseases": dict(self.gene_to_diseases),
                    "disease_to_genes": dict(self.disease_to_genes),
                    "ancestors": self.ancestors,
                    "ic": self.ic,
                    "n_diseases": self.n_diseases,
                }, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"Phenomizer cache saved → {self.cache_path}")
        except Exception as e:
            logger.warning(f"Phenomizer cache save failed: {e}")

    def build(self) -> None:
        if not self.hpo_service or not self.hpo_service.terms:
            logger.warning("Phenomizer: HPO ontology not loaded — disabled")
            self.use_demo = True
            self.loaded = True
            return

        t0 = time.time()
        if self._try_load_cache():
            self.loaded = True
            return

        try:
            self._build_ancestor_closure()
            self._parse_hpoa()
            self._expand_annotations()
            self._compute_ic()
            self._parse_genes_to_phenotype()
        except FileNotFoundError as e:
            logger.warning(f"Phenomizer: {e} — disabled")
            self.use_demo = True
            self.loaded = True
            return
        except Exception as e:
            logger.error(f"Phenomizer build failed: {e}")
            self.use_demo = True
            self.loaded = True
            return

        self.loaded = True
        self._save_cache()
        logger.info(f"Phenomizer ready in {time.time() - t0:.1f}s")

    # ── Similarity & ranking ───────────────────────────────────────────
    def _lca_ic(self, t1: str, t2: str) -> float:
        """Return IC of the lowest (most informative) common ancestor."""
        if t1 == t2:
            return self.ic.get(t1, 0.0)
        a1 = self.ancestors.get(t1)
        a2 = self.ancestors.get(t2)
        if not a1 or not a2:
            return 0.0
        common = a1 & a2
        if not common:
            return 0.0
        best = 0.0
        for c in common:
            v = self.ic.get(c, 0.0)
            if v > best:
                best = v
        return best

    def _term_to_set_sim(self, t: str, term_set: Iterable[str]) -> float:
        best = 0.0
        for s in term_set:
            v = self._lca_ic(t, s)
            if v > best:
                best = v
        return best

    def _avg_max(self, src: Iterable[str], dst: Iterable[str]) -> float:
        src = list(src)
        if not src:
            return 0.0
        total = 0.0
        for t in src:
            total += self._term_to_set_sim(t, dst)
        return total / len(src)

    def _candidate_diseases(self, query_hp_ids: List[str], max_candidates: int = 2000) -> Set[str]:
        """
        Restrict scoring to diseases that share at least one ancestor with any
        query term. Saves us scoring ~8k diseases when most won't overlap.
        """
        candidates: Set[str] = set()
        for q in query_hp_ids:
            # Hit any disease annotated with q (annotation propagation already
            # gave us upward closure)
            candidates |= self.hpo_to_diseases.get(q, set())
        if len(candidates) > max_candidates:
            return candidates
        # Also include diseases whose annotations share an ancestor with q,
        # to catch sibling terms
        for q in query_hp_ids:
            for anc in self.ancestors.get(q, {q}):
                candidates |= self.hpo_to_diseases.get(anc, set())
                if len(candidates) > max_candidates:
                    return candidates
        return candidates

    def rank_diseases(
        self,
        query_hp_ids: List[str],
        top_k: int = 10,
        candidate_gene: Optional[str] = None,
        min_score: float = 0.5,
    ) -> List[Dict]:
        """
        Score and rank candidate diseases against the user's HPO profile.

        Symmetric IC-weighted similarity (Resnik/Köhler):
            sim(Q, D) = 0.5 * ( avg_max(Q→D) + avg_max(D→Q) )

        candidate_gene (optional): if given, prefilter diseases to those
        associated with that gene via HPO's genes_to_phenotype index. This
        is how the agent combines symptom + variant evidence into a single
        ranked list.
        """
        if not self.loaded or self.use_demo:
            return []
        if not query_hp_ids:
            return []
        # Filter to terms we know about
        q = [t for t in query_hp_ids if t in self.ancestors]
        if not q:
            return []

        candidates = self._candidate_diseases(q)
        if candidate_gene:
            gene_diseases = self.gene_to_diseases.get(candidate_gene.upper(), set())
            if gene_diseases:
                # Keep diseases that overlap with either source
                hard = candidates & gene_diseases
                if hard:
                    candidates = hard

        results: List[Tuple[str, float, float, float]] = []
        for d in candidates:
            d_terms = self.disease_to_hpo.get(d)
            if not d_terms:
                continue
            q_to_d = self._avg_max(q, d_terms)
            d_to_q = self._avg_max(d_terms, q)
            score = 0.5 * (q_to_d + d_to_q)
            if score < min_score:
                continue
            results.append((d, score, q_to_d, d_to_q))

        results.sort(key=lambda r: -r[1])

        out: List[Dict] = []
        for disease_id, score, q_to_d, d_to_q in results[:top_k]:
            meta = self.disease_meta.get(disease_id, {})
            d_terms = self.disease_to_hpo.get(disease_id, set())
            # Shared terms (intersection of query closure and disease closure)
            shared = sorted(set(q) & d_terms,
                            key=lambda t: -self.ic.get(t, 0))[:6]
            genes = sorted(self.disease_to_genes.get(disease_id, set()))[:6]
            out.append({
                "disease_id": disease_id,
                "name": meta.get("name", disease_id),
                "source": meta.get("source", ""),
                "omim": meta.get("omim", ""),
                "score": round(score, 3),
                "q_to_d": round(q_to_d, 3),
                "d_to_q": round(d_to_q, 3),
                "shared_terms": [
                    {"hp_id": t,
                     "name": self.hpo_service.terms.get(t, {}).get("name", t),
                     "ic": round(self.ic.get(t, 0), 2)}
                    for t in shared
                ],
                "genes": genes,
                "url": (
                    f"https://omim.org/entry/{meta.get('omim')}"
                    if meta.get("omim")
                    else f"https://hpo.jax.org/app/browse/disease/{disease_id}"
                ),
            })
        return out

    def stats(self) -> Dict:
        return {
            "loaded": self.loaded,
            "demo": self.use_demo,
            "n_diseases": self.n_diseases,
            "n_ic_terms": len(self.ic),
            "n_gene_links": len(self.gene_to_diseases),
        }
