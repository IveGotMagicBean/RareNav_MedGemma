"""
ClinVar Database Service — SQLite backend
=========================================

Drop-in replacement for the original pandas-based ClinVarService.
8.67M rows × pandas DataFrame would sit in ~4 GB of RSS and take 6 s to load.
With SQLite + a handful of B-tree indices the same data is:

    * ~1.5 GB on disk (one-off)
    * ~50 MB resident
    * < 1 s startup
    * gene look-ups in single-digit ms

First start performs a one-time TSV → SQLite migration (~2 min). All
subsequent starts simply mmap the .sqlite file.

Query surface is API-compatible with ClinVarService:
    get_count(), search_by_gene(), search_by_variant(),
    search_by_disease(), get_gene_summary(), get_statistics()
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


WANT_COLS = [
    "AlleleID", "GeneSymbol", "Name", "Type",
    "ClinicalSignificance", "ClinSigSimple",
    "PhenotypeList", "ReviewStatus", "NumberSubmitters",
    "Chromosome", "Start", "Stop",
    "ReferenceAllele", "AlternateAllele",
    "LastEvaluated", "RS# (dbSNP)", "VariationID",
]

# Column → SQLite-friendly column name.
COL_MAP = {
    "AlleleID": "allele_id",
    "GeneSymbol": "gene",
    "Name": "name",
    "Type": "type",
    "ClinicalSignificance": "significance",
    "ClinSigSimple": "sig_simple",
    "PhenotypeList": "phenotype",
    "ReviewStatus": "review_status",
    "NumberSubmitters": "submitters",
    "Chromosome": "chromosome",
    "Start": "pos_start",
    "Stop": "pos_stop",
    "ReferenceAllele": "ref",
    "AlternateAllele": "alt",
    "LastEvaluated": "last_evaluated",
    "RS# (dbSNP)": "dbsnp",
    "VariationID": "variation_id",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS variants (
    rowid          INTEGER PRIMARY KEY AUTOINCREMENT,
    variation_id   INTEGER,
    allele_id      INTEGER,
    gene           TEXT,
    gene_upper     TEXT,
    name           TEXT,
    type           TEXT,
    significance   TEXT,
    sig_simple     INTEGER,
    phenotype      TEXT,
    review_status  TEXT,
    submitters     INTEGER,
    chromosome     TEXT,
    pos_start      INTEGER,
    pos_stop       INTEGER,
    ref            TEXT,
    alt            TEXT,
    dbsnp          TEXT,
    last_evaluated TEXT
);
CREATE INDEX IF NOT EXISTS idx_gene_upper   ON variants(gene_upper);
CREATE INDEX IF NOT EXISTS idx_variation_id ON variants(variation_id);
CREATE INDEX IF NOT EXISTS idx_sig_simple   ON variants(sig_simple);
"""


def _read_header(path: Path) -> List[str]:
    with open(path, "rb") as f:
        line = f.readline().decode("utf-8", errors="replace").rstrip("\n\r")
    line = line.lstrip("#")
    return [c.strip() for c in line.split("\t")]


def _int_or_none(v: str):
    if v is None or v == "" or v == "-":
        return None
    try:
        return int(v)
    except ValueError:
        return None


class ClinVarSQLiteService:
    def __init__(self, db_path: str, sqlite_path: Optional[str] = None):
        self.tsv_path = Path(db_path)
        # SQLite cache lives next to the TSV so cleanup is obvious to the user.
        self.sqlite_path = Path(sqlite_path) if sqlite_path else (
            self.tsv_path.with_suffix("") .as_posix() + "_rarenav.sqlite"
        )
        self.sqlite_path = Path(self.sqlite_path)
        self.conn: Optional[sqlite3.Connection] = None
        self.loaded: bool = False
        self.use_demo: bool = False
        self._count: int = 0

    # ── Build / load ───────────────────────────────────────────────────
    def _migrate_from_tsv(self) -> None:
        actual_cols = _read_header(self.tsv_path)
        present = [c for c in WANT_COLS if c in actual_cols]
        logger.info(f"ClinVar SQLite migration: {len(present)} columns from TSV")

        if self.sqlite_path.exists():
            self.sqlite_path.unlink()

        conn = sqlite3.connect(self.sqlite_path)
        conn.executescript(SCHEMA)
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=MEMORY")
        cur = conn.cursor()

        idx_map = {col: actual_cols.index(col) for col in present}
        t0 = time.time()
        n = 0
        batch = []
        BATCH = 50000

        # Note: we keep all rows from the TSV (GRCh37 and GRCh38 share a
        # VariationID but are distinct submissions). The autoincrement rowid
        # carries uniqueness so callers see the same record count as the
        # source TSV.
        sql = """
        INSERT INTO variants(
            variation_id, allele_id, gene, gene_upper, name, type,
            significance, sig_simple, phenotype, review_status, submitters,
            chromosome, pos_start, pos_stop, ref, alt, dbsnp, last_evaluated
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

        with open(self.tsv_path, "r", encoding="utf-8", errors="replace") as f:
            f.readline()   # header
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < max(idx_map.values()) + 1:
                    continue
                def g(col):
                    i = idx_map.get(col)
                    if i is None or i >= len(parts):
                        return ""
                    return parts[i]
                vid = _int_or_none(g("VariationID"))
                if vid is None:
                    continue
                gene = g("GeneSymbol")
                batch.append((
                    vid,
                    _int_or_none(g("AlleleID")),
                    gene,
                    gene.upper() if gene else "",
                    g("Name"),
                    g("Type"),
                    g("ClinicalSignificance"),
                    _int_or_none(g("ClinSigSimple")),
                    g("PhenotypeList"),
                    g("ReviewStatus"),
                    _int_or_none(g("NumberSubmitters")) or 0,
                    g("Chromosome"),
                    _int_or_none(g("Start")),
                    _int_or_none(g("Stop")),
                    g("ReferenceAllele"),
                    g("AlternateAllele"),
                    g("RS# (dbSNP)"),
                    g("LastEvaluated"),
                ))
                n += 1
                if len(batch) >= BATCH:
                    cur.executemany(sql, batch)
                    batch.clear()
                    if n % 500000 == 0:
                        logger.info(f"  ClinVar SQLite: {n:,} rows inserted")
        if batch:
            cur.executemany(sql, batch)
        conn.commit()

        logger.info(f"ClinVar SQLite: total {n:,} rows in {time.time()-t0:.1f}s")
        # Build remaining indices after bulk insert (faster than maintaining)
        logger.info("ClinVar SQLite: building indices...")
        t1 = time.time()
        conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_gene_upper ON variants(gene_upper);
            CREATE INDEX IF NOT EXISTS idx_sig_simple ON variants(sig_simple);
        """)
        conn.execute("PRAGMA optimize")
        conn.commit()
        logger.info(f"ClinVar SQLite: indices done in {time.time()-t1:.1f}s")
        conn.close()

    def load(self) -> None:
        if not self.tsv_path.exists() and not self.sqlite_path.exists():
            logger.warning(f"ClinVar TSV+SQLite both missing → demo mode")
            self._load_demo()
            return

        if (not self.sqlite_path.exists()
            or (self.tsv_path.exists()
                and self.sqlite_path.stat().st_mtime < self.tsv_path.stat().st_mtime)):
            try:
                self._migrate_from_tsv()
            except Exception as e:
                logger.error(f"ClinVar SQLite migration failed: {e}")
                self._load_demo()
                return

        try:
            # check_same_thread=False so we can serve from Flask request threads
            self.conn = sqlite3.connect(
                self.sqlite_path, check_same_thread=False, uri=False
            )
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA query_only=ON")
            (self._count,) = self.conn.execute("SELECT COUNT(*) FROM variants").fetchone()
            logger.info(f"ClinVar SQLite ready: {self._count:,} variants (cache={self.sqlite_path})")
            self.loaded = True
        except Exception as e:
            logger.error(f"ClinVar SQLite open failed: {e}")
            self._load_demo()

    def _load_demo(self):
        # Build an in-memory SQLite with a tiny demo set so the rest of the
        # API keeps working — same return shape, no special-casing in callers.
        self.use_demo = True
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        demo = [
            (1, 1, "CFTR", "CFTR",
             "NM_000492.4(CFTR):c.1521_1523delCTT (p.Phe508del)", "Deletion",
             "Pathogenic", 1, "Cystic fibrosis",
             "criteria provided, multiple submitters, no conflicts", 25,
             "7", 117548628, 117548630, "CTT", "-", "rs113993960", "2024-01-01"),
            (2, 2, "BRCA1", "BRCA1",
             "NM_007294.4(BRCA1):c.5266dupC (p.Gln1756ProfsTer74)", "Insertion",
             "Pathogenic", 1, "Hereditary breast and ovarian cancer syndrome",
             "criteria provided, multiple submitters, no conflicts", 30,
             "17", 43071077, 43071077, "C", "CC", "rs80357906", "2024-01-01"),
            (9, 3, "HFE", "HFE",
             "NM_000410.4(HFE):c.845G>A (p.Cys282Tyr)", "single nucleotide variant",
             "Pathogenic", 1, "Hemochromatosis type 1",
             "criteria provided, multiple submitters, no conflicts", 15,
             "6", 26092913, 26092913, "G", "A", "rs1800562", "2025-12-29"),
        ]
        self.conn.executemany(
            "INSERT INTO variants("
            "variation_id, allele_id, gene, gene_upper, name, type, "
            "significance, sig_simple, phenotype, review_status, submitters, "
            "chromosome, pos_start, pos_stop, ref, alt, dbsnp, last_evaluated"
            ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            demo,
        )
        self.conn.commit()
        self._count = len(demo)
        self.loaded = True

    # ── Query API (compatible with the old pandas-based service) ───────
    def get_count(self) -> int:
        return self._count

    def search_by_gene(self, gene: str, limit: int = 20) -> List[Dict]:
        if not self.conn or not gene:
            return []
        rows = self.conn.execute(
            "SELECT * FROM variants WHERE gene_upper = ? "
            "ORDER BY (sig_simple = 1) DESC, submitters DESC LIMIT ?",
            (gene.upper(), limit),
        ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def search_by_variant(self, gene: str, variant: str) -> List[Dict]:
        if not self.conn or not gene or not variant:
            return []
        aa = {'A':'Ala','R':'Arg','N':'Asn','D':'Asp','C':'Cys','Q':'Gln',
              'E':'Glu','G':'Gly','H':'His','I':'Ile','L':'Leu','K':'Lys',
              'M':'Met','F':'Phe','P':'Pro','S':'Ser','T':'Thr','W':'Trp',
              'Y':'Tyr','V':'Val'}
        patterns = [variant]
        m = re.match(r'([A-Z])(\d+)', variant)
        if m and m.group(1) in aa:
            patterns.append(f"{aa[m.group(1)]}{m.group(2)}")
            patterns.append(f"p.{aa[m.group(1)]}{m.group(2)}")
        for pat in patterns:
            rows = self.conn.execute(
                "SELECT * FROM variants WHERE gene_upper = ? "
                "AND name LIKE ? LIMIT 5",
                (gene.upper(), f"%{pat}%"),
            ).fetchall()
            if rows:
                return [self._row_to_record(r) for r in rows]
        return []

    def search_by_disease(self, disease: str, limit: int = 30) -> List[Dict]:
        if not self.conn or not disease:
            return []
        rows = self.conn.execute(
            "SELECT * FROM variants "
            "WHERE phenotype LIKE ? "
            "AND significance LIKE ? "
            "ORDER BY (sig_simple = 1) DESC, submitters DESC "
            "LIMIT ?",
            (f"%{disease}%", "%athogenic%", limit),
        ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_gene_summary(self, gene: str) -> Dict:
        if not self.conn:
            return {}
        cur = self.conn
        gu = gene.upper()
        n_total = cur.execute(
            "SELECT COUNT(*) FROM variants WHERE gene_upper = ?", (gu,)
        ).fetchone()[0]
        if not n_total:
            return {"gene": gene, "found": False}
        n_path = cur.execute(
            "SELECT COUNT(*) FROM variants WHERE gene_upper = ? "
            "AND significance LIKE '%athogenic%'", (gu,)
        ).fetchone()[0]
        sig_rows = cur.execute(
            "SELECT significance, COUNT(*) FROM variants WHERE gene_upper = ? "
            "GROUP BY significance ORDER BY 2 DESC LIMIT 6", (gu,)
        ).fetchall()
        type_rows = cur.execute(
            "SELECT type, COUNT(*) FROM variants WHERE gene_upper = ? "
            "GROUP BY type ORDER BY 2 DESC LIMIT 5", (gu,)
        ).fetchall()
        ph_rows = cur.execute(
            "SELECT phenotype FROM variants WHERE gene_upper = ? "
            "AND phenotype IS NOT NULL AND phenotype != '' LIMIT 1500", (gu,)
        ).fetchall()
        phen_counter: Dict[str, int] = {}
        for (ph,) in ph_rows:
            for chunk in (ph or "").split("|"):
                c = chunk.strip()
                if len(c) > 2:
                    phen_counter[c] = phen_counter.get(c, 0) + 1
        top_diseases = [k for k, _ in sorted(
            phen_counter.items(), key=lambda kv: -kv[1])[:5]]
        return {
            "gene": gu, "found": True,
            "total_variants": n_total, "pathogenic_count": n_path,
            "significance_distribution": {r[0]: r[1] for r in sig_rows},
            "associated_diseases": top_diseases,
            "variant_types": {r[0]: r[1] for r in type_rows},
        }

    def get_statistics(self) -> Dict:
        if not self.conn:
            return {}
        cur = self.conn
        total = self._count
        p = cur.execute(
            "SELECT COUNT(*) FROM variants WHERE sig_simple = 1"
        ).fetchone()[0]
        b = cur.execute(
            "SELECT COUNT(*) FROM variants WHERE sig_simple = 0"
        ).fetchone()[0]
        unique = cur.execute(
            "SELECT COUNT(DISTINCT gene_upper) FROM variants"
        ).fetchone()[0]
        top = cur.execute(
            "SELECT gene_upper, COUNT(*) c FROM variants "
            "GROUP BY gene_upper ORDER BY c DESC LIMIT 10"
        ).fetchall()
        return {
            "total_variants": total,
            "unique_genes": unique,
            "pathogenic_count": p,
            "benign_count": b,
            "top_genes": {r[0]: r[1] for r in top},
        }

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _row_to_record(r: sqlite3.Row) -> Dict:
        sig = r["significance"] or "Unknown"
        ch = r["chromosome"] or ""
        st = r["pos_start"]
        sp = r["pos_stop"]
        return {
            "variation_id": str(r["variation_id"]),
            "gene":         r["gene"] or "",
            "name":         r["name"] or "",
            "type":         r["type"] or "",
            "significance": sig,
            "significance_simple": int(r["sig_simple"]) if r["sig_simple"] is not None else -1,
            "phenotype":    r["phenotype"] or "",
            "review_status": r["review_status"] or "",
            "submitters":   int(r["submitters"] or 0),
            "chromosome":   ch,
            "position":     f"{ch}:{st}-{sp}",
            "ref":          r["ref"] or "",
            "alt":          r["alt"] or "",
            "dbsnp":        r["dbsnp"] or "",
            "last_evaluated": r["last_evaluated"] or "",
        }
