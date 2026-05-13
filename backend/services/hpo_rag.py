"""
HPO Retrieval-Augmented Generation Service
==========================================

Real RAG for HPO phenotype lookup: encode all 18,252 HPO terms (plus synonyms
and definitions) with a sentence-transformer, then match user symptoms by
cosine similarity over normalised embeddings.

Replaces the regex / substring matching previously used in HPOService.

Design:
    corpus = [name, synonym_1, synonym_2, ..., def] for every HPO term
    each row carries (hp_id, surface_form_kind)   so we can dedup at query time
    embeddings stored normalised → search reduces to a single GEMV

Cache strategy:
    First start  :  encode 18k * ~5 surface forms ≈ 90k vectors  (~70s on CPU)
                    persisted to  <cache_dir>/hpo_embeddings.npz
    Later starts :  mmap-load,   build time < 1 s
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Below this similarity we treat hits as noise.
DEFAULT_MIN_SCORE = 0.35


class HPORagIndex:
    """
    A FAISS-free dense retriever over HPO terms.

    18k * ~5 surface forms ≈ 90k 384-d float32 vectors ≈ 130 MB.
    Brute-force cosine over this is ~5 ms per query on a modern CPU,
    so a FAISS / HNSW index is unnecessary for this corpus size.
    """

    def __init__(
        self,
        terms: Dict[str, dict],
        model_name: str = DEFAULT_MODEL,
        cache_dir: Optional[str] = None,
        embedding_cache: Optional[str] = None,
    ):
        self.terms = terms
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.embedding_cache = Path(embedding_cache) if embedding_cache else None

        self.model = None
        self.row_hp_ids: List[str] = []
        self.row_surfaces: List[str] = []
        self.row_kinds: List[str] = []        # name | synonym | definition
        self.embeddings: Optional[np.ndarray] = None
        self.dim: int = 0
        self.loaded: bool = False
        self.use_demo: bool = False

    # ── Build / cache ──────────────────────────────────────────────────
    def _build_corpus(self) -> None:
        for hp_id, term in self.terms.items():
            name = (term.get("name") or "").strip()
            if not name:
                continue
            self.row_hp_ids.append(hp_id)
            self.row_surfaces.append(name)
            self.row_kinds.append("name")

            for syn in (term.get("synonyms") or [])[:6]:
                syn = syn.strip()
                if not syn or syn.lower() == name.lower():
                    continue
                self.row_hp_ids.append(hp_id)
                self.row_surfaces.append(syn)
                self.row_kinds.append("synonym")

            defn = (term.get("def") or "").strip()
            if defn and len(defn) > 30:
                # keep just the first sentence to bias semantic match toward the
                # phenotype itself rather than incidental wording
                first_sentence = defn.split(".")[0]
                self.row_hp_ids.append(hp_id)
                self.row_surfaces.append(first_sentence[:200])
                self.row_kinds.append("definition")

    def _load_model(self):
        from sentence_transformers import SentenceTransformer
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)
        self.dim = self.model.get_sentence_embedding_dimension()

    def _try_load_cache(self) -> bool:
        if not self.embedding_cache or not self.embedding_cache.exists():
            return False
        try:
            data = np.load(self.embedding_cache, allow_pickle=True)
            cached_terms = int(data["n_terms"][0]) if "n_terms" in data else -1
            if cached_terms != len(self.terms):
                logger.warning(
                    f"HPO RAG cache stale ({cached_terms} terms cached vs "
                    f"{len(self.terms)} loaded) — rebuilding"
                )
                return False
            self.row_hp_ids = list(data["row_hp_ids"])
            self.row_surfaces = list(data["row_surfaces"])
            self.row_kinds = list(data["row_kinds"])
            self.embeddings = data["embeddings"].astype(np.float32, copy=False)
            self.dim = int(self.embeddings.shape[1])
            logger.info(
                f"HPO RAG cache hit: {len(self.row_hp_ids):,} surface forms × "
                f"{self.dim}d  ({self.embeddings.nbytes / 1e6:.1f} MB)"
            )
            return True
        except Exception as e:
            logger.warning(f"HPO RAG cache load failed: {e}")
            return False

    def _save_cache(self) -> None:
        if not self.embedding_cache:
            return
        try:
            self.embedding_cache.parent.mkdir(parents=True, exist_ok=True)
            np.savez(
                self.embedding_cache,
                row_hp_ids=np.array(self.row_hp_ids, dtype=object),
                row_surfaces=np.array(self.row_surfaces, dtype=object),
                row_kinds=np.array(self.row_kinds, dtype=object),
                embeddings=self.embeddings,
                n_terms=np.array([len(self.terms)]),
                model=np.array([self.model_name]),
            )
            logger.info(f"HPO RAG cache saved → {self.embedding_cache}")
        except Exception as e:
            logger.warning(f"HPO RAG cache save failed: {e}")

    def build(self) -> None:
        """Load embeddings from cache or build them from scratch."""
        if not self.terms:
            logger.warning("HPO RAG: empty term dict, falling back to demo mode")
            self.use_demo = True
            self.loaded = True
            return

        t0 = time.time()
        if self._try_load_cache():
            self.loaded = True
            return

        try:
            self._load_model()
        except Exception as e:
            logger.error(f"HPO RAG: failed to load sentence-transformer ({e}) — "
                         f"semantic search disabled, falling back to substring match")
            self.use_demo = True
            self.loaded = True
            return

        self._build_corpus()
        logger.info(
            f"HPO RAG: encoding {len(self.row_surfaces):,} surface forms "
            f"({len(self.terms):,} unique terms) with {self.model_name}..."
        )
        try:
            self.embeddings = self.model.encode(
                self.row_surfaces,
                batch_size=128,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            ).astype(np.float32, copy=False)
        except Exception as e:
            logger.error(f"HPO RAG encoding failed: {e}")
            self.use_demo = True
            self.loaded = True
            return

        elapsed = time.time() - t0
        logger.info(
            f"HPO RAG ready: {self.embeddings.shape[0]:,} × {self.dim}d "
            f"({self.embeddings.nbytes / 1e6:.1f} MB) in {elapsed:.1f}s"
        )
        self._save_cache()
        self.loaded = True

    # ── Query ──────────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = DEFAULT_MIN_SCORE,
    ) -> List[Dict]:
        """
        Return up to top_k HPO terms ranked by cosine similarity against the
        query. Each result includes the surface form that matched (so the
        Agent can show the user *why* this term was retrieved).
        """
        if not self.loaded or self.use_demo or self.embeddings is None:
            return []
        if not query or not query.strip():
            return []

        try:
            q = self.model.encode(
                [query], normalize_embeddings=True, convert_to_numpy=True
            ).astype(np.float32, copy=False)
        except Exception as e:
            logger.warning(f"HPO RAG query encode failed: {e}")
            return []

        # Over-fetch so we can dedup multiple surface forms of the same term
        sims = (q @ self.embeddings.T)[0]
        order = np.argsort(-sims)

        seen: Dict[str, Tuple[float, int]] = {}
        for idx in order[: top_k * 8]:
            hp_id = self.row_hp_ids[idx]
            score = float(sims[idx])
            if score < min_score:
                break
            if hp_id not in seen or score > seen[hp_id][0]:
                seen[hp_id] = (score, idx)
            if len(seen) >= top_k:
                break

        out: List[Dict] = []
        ranked = sorted(seen.items(), key=lambda kv: -kv[1][0])[:top_k]
        for hp_id, (score, idx) in ranked:
            term = self.terms.get(hp_id, {})
            out.append({
                "id": hp_id,
                "name": term.get("name", ""),
                "score": round(score, 4),
                "matched_surface": self.row_surfaces[idx],
                "matched_kind": self.row_kinds[idx],
                "definition": (term.get("def") or "")[:240],
                "synonyms": (term.get("synonyms") or [])[:3],
                "category": term.get("category", ""),
            })
        return out

    def search_multi(
        self,
        symptoms: List[str],
        top_k_per_symptom: int = 3,
        min_score: float = DEFAULT_MIN_SCORE,
    ) -> Dict[str, List[Dict]]:
        """Run search() for every symptom in one call; useful for the Agent."""
        return {
            sym: self.search(sym, top_k=top_k_per_symptom, min_score=min_score)
            for sym in symptoms if sym and sym.strip()
        }

    def stats(self) -> Dict:
        return {
            "loaded": self.loaded,
            "demo": self.use_demo,
            "terms": len(self.terms),
            "surface_forms": len(self.row_hp_ids),
            "embedding_dim": self.dim,
            "model": self.model_name,
        }
