"""
ClinVar Database Service
兼容第一行带 # 的 ClinVar variant_summary.txt
"""
import pandas as pd
import pickle
import re
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

WANT_COLS = [
    "AlleleID", "GeneSymbol", "Name", "Type",
    "ClinicalSignificance", "ClinSigSimple",
    "PhenotypeList", "ReviewStatus", "NumberSubmitters",
    "Chromosome", "Start", "Stop",
    "ReferenceAllele", "AlternateAllele",
    "LastEvaluated", "RS# (dbSNP)", "VariationID",
]


def _read_header(path: Path) -> list[str]:
    """读第一行，去掉 # 前缀，返回列名列表"""
    with open(path, "rb") as f:
        line = f.readline().decode("utf-8", errors="replace").rstrip("\n\r")
    line = line.lstrip("#")
    return [c.strip() for c in line.split("\t")]


class ClinVarService:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.df = None
        self.loaded = False
        self.use_demo = False

    def load(self):
        if not self.db_path.exists():
            logger.warning(f"ClinVar not found: {self.db_path} → demo mode")
            self._load_demo()
            return

        cache_path = self.db_path.parent / (self.db_path.stem + "_rarenav.pkl")
        if cache_path.exists() and cache_path.stat().st_mtime > self.db_path.stat().st_mtime:
            logger.info(f"Loading from cache: {cache_path}")
            try:
                with open(cache_path, "rb") as f:
                    self.df = pickle.load(f)
                logger.info(f"Cache: {len(self.df):,} variants")
                self.loaded = True
                return
            except Exception as e:
                logger.warning(f"Cache failed ({e}), re-parsing")

        logger.info(f"Parsing {self.db_path} ...")

        # 1. 读真实列名（去 # 前缀）
        actual_cols = _read_header(self.db_path)
        usecols = [c for c in WANT_COLS if c in actual_cols]
        logger.info(f"Using {len(usecols)} columns: {usecols}")

        # 2. 分块读数据
        #    skiprows=1  跳过第一行（已手动处理为列名）
        #    names=actual_cols  指定列名
        #    usecols=usecols 只保留需要的列
        chunks = []
        for i, chunk in enumerate(pd.read_csv(
            self.db_path,
            sep="\t",
            skiprows=1,           # 跳过 header 行（含 # 前缀）
            names=actual_cols,    # 手动指定列名
            usecols=usecols,
            low_memory=False,
            chunksize=200_000,
            on_bad_lines="skip",
        )):
            chunks.append(chunk)
            if (i + 1) % 5 == 0:
                logger.info(f"  {(i+1)*200_000:,} rows...")

        self.df = pd.concat(chunks, ignore_index=True)

        # 补齐缺失列（用 None 填）
        for c in WANT_COLS:
            if c not in self.df.columns:
                self.df[c] = None

        logger.info(f"Loaded {len(self.df):,} variants")

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(self.df, f)
            logger.info(f"Cache saved → {cache_path}")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

        self.loaded = True

    # ── Demo ─────────────────────────────────────────────────────────────────
    def _load_demo(self):
        self.use_demo = True
        self.df = pd.DataFrame([
            {"AlleleID":1,"GeneSymbol":"CFTR","Name":"NM_000492.4(CFTR):c.1521_1523delCTT (p.Phe508del)","Type":"Deletion","ClinicalSignificance":"Pathogenic","ClinSigSimple":1,"PhenotypeList":"Cystic fibrosis","ReviewStatus":"criteria provided, multiple submitters, no conflicts","NumberSubmitters":25,"Chromosome":"7","Start":117548628,"Stop":117548630,"ReferenceAllele":"CTT","AlternateAllele":"-","LastEvaluated":"2024-01-01","RS# (dbSNP)":"rs113993960","VariationID":7105},
            {"AlleleID":2,"GeneSymbol":"BRCA1","Name":"NM_007294.4(BRCA1):c.5266dupC (p.Gln1756ProfsTer74)","Type":"Insertion","ClinicalSignificance":"Pathogenic","ClinSigSimple":1,"PhenotypeList":"Hereditary breast and ovarian cancer syndrome","ReviewStatus":"criteria provided, multiple submitters, no conflicts","NumberSubmitters":30,"Chromosome":"17","Start":43071077,"Stop":43071077,"ReferenceAllele":"C","AlternateAllele":"CC","LastEvaluated":"2024-01-01","RS# (dbSNP)":"rs80357906","VariationID":17661},
            {"AlleleID":3,"GeneSymbol":"HFE","Name":"NM_000410.4(HFE):c.845G>A (p.Cys282Tyr)","Type":"single nucleotide variant","ClinicalSignificance":"Pathogenic","ClinSigSimple":1,"PhenotypeList":"Hemochromatosis type 1","ReviewStatus":"criteria provided, multiple submitters, no conflicts","NumberSubmitters":15,"Chromosome":"6","Start":26092913,"Stop":26092913,"ReferenceAllele":"G","AlternateAllele":"A","LastEvaluated":"2025-12-29","RS# (dbSNP)":"rs1800562","VariationID":9},
            {"AlleleID":4,"GeneSymbol":"HFE","Name":"NM_000410.4(HFE):c.187C>G (p.His63Asp)","Type":"single nucleotide variant","ClinicalSignificance":"Conflicting classifications of pathogenicity","ClinSigSimple":-1,"PhenotypeList":"Hemochromatosis type 1|Hereditary hemochromatosis","ReviewStatus":"criteria provided, conflicting classifications","NumberSubmitters":56,"Chromosome":"6","Start":26090951,"Stop":26090951,"ReferenceAllele":"C","AlternateAllele":"G","LastEvaluated":"2025-12-29","RS# (dbSNP)":"rs1799945","VariationID":10},
            {"AlleleID":5,"GeneSymbol":"GBA","Name":"NM_001005741.3(GBA):c.1226A>G (p.Asn409Ser)","Type":"single nucleotide variant","ClinicalSignificance":"Pathogenic","ClinSigSimple":1,"PhenotypeList":"Gaucher disease type 1","ReviewStatus":"criteria provided, multiple submitters, no conflicts","NumberSubmitters":12,"Chromosome":"1","Start":155234452,"Stop":155234452,"ReferenceAllele":"A","AlternateAllele":"G","LastEvaluated":"2023-08-01","RS# (dbSNP)":"rs76763715","VariationID":4288},
            {"AlleleID":6,"GeneSymbol":"PKD1","Name":"NM_001009944.3(PKD1):c.4870C>T (p.Arg1624Trp)","Type":"single nucleotide variant","ClinicalSignificance":"Likely pathogenic","ClinSigSimple":1,"PhenotypeList":"Autosomal dominant polycystic kidney disease","ReviewStatus":"criteria provided, single submitter","NumberSubmitters":2,"Chromosome":"16","Start":2172878,"Stop":2172878,"ReferenceAllele":"C","AlternateAllele":"T","LastEvaluated":"2022-05-01","RS# (dbSNP)":"rs121912597","VariationID":521456},
            {"AlleleID":7,"GeneSymbol":"PAH","Name":"NM_000277.3(PAH):c.1222C>T (p.Arg408Trp)","Type":"single nucleotide variant","ClinicalSignificance":"Pathogenic","ClinSigSimple":1,"PhenotypeList":"Phenylketonuria","ReviewStatus":"criteria provided, multiple submitters, no conflicts","NumberSubmitters":18,"Chromosome":"12","Start":102836888,"Stop":102836888,"ReferenceAllele":"C","AlternateAllele":"T","LastEvaluated":"2024-02-01","RS# (dbSNP)":"rs5030858","VariationID":1040},
        ])
        self.loaded = True

    # ── 查询接口 ─────────────────────────────────────────────────────────────
    def get_count(self): return len(self.df) if self.df is not None else 0

    def search_by_gene(self, gene: str, limit: int = 20):
        if self.df is None: return []
        return self._to_records(
            self.df[self.df["GeneSymbol"].astype(str).str.upper() == gene.upper()].head(limit))

    def search_by_variant(self, gene: str, variant: str):
        if self.df is None: return []
        gdf = self.df[self.df["GeneSymbol"].astype(str).str.upper() == gene.upper()]
        if gdf.empty: return []
        aa = {'A':'Ala','R':'Arg','N':'Asn','D':'Asp','C':'Cys','Q':'Gln',
              'E':'Glu','G':'Gly','H':'His','I':'Ile','L':'Leu','K':'Lys',
              'M':'Met','F':'Phe','P':'Pro','S':'Ser','T':'Thr','W':'Trp','Y':'Tyr','V':'Val'}
        patterns = [variant]
        m = re.match(r'([A-Z])(\d+)', variant)
        if m and m.group(1) in aa:
            patterns += [f"{aa[m.group(1)]}{m.group(2)}", f"p.{aa[m.group(1)]}{m.group(2)}"]
        for pat in patterns:
            found = gdf[gdf["Name"].astype(str).str.contains(pat, case=False, na=False, regex=False)]
            if not found.empty: return self._to_records(found.head(5))
        return []

    def search_by_disease(self, disease: str, limit: int = 30):
        if self.df is None: return []
        m1 = self.df["PhenotypeList"].astype(str).str.contains(disease, case=False, na=False)
        m2 = self.df["ClinicalSignificance"].astype(str).str.contains("Pathogenic|Likely pathogenic", case=False, na=False)
        return self._to_records(self.df[m1 & m2].head(limit))

    def get_gene_summary(self, gene: str):
        if self.df is None: return {}
        gdf = self.df[self.df["GeneSymbol"].astype(str).str.upper() == gene.upper()]
        if gdf.empty: return {"gene": gene, "found": False}
        diseases = gdf["PhenotypeList"].dropna().astype(str).str.split("|").explode().str.strip()
        diseases = diseases[diseases.str.len() > 2].value_counts().head(5).index.tolist()
        path = gdf[gdf["ClinicalSignificance"].astype(str).str.contains("Pathogenic", case=False, na=False)]
        return {"gene": gene.upper(), "found": True,
                "total_variants": len(gdf), "pathogenic_count": len(path),
                "significance_distribution": gdf["ClinicalSignificance"].value_counts().to_dict(),
                "associated_diseases": diseases,
                "variant_types": gdf["Type"].value_counts().head(5).to_dict()}

    def get_statistics(self):
        if self.df is None: return {}
        try:
            p = len(self.df[self.df["ClinSigSimple"] == 1])
            b = len(self.df[self.df["ClinSigSimple"] == 0])
        except Exception:
            p = b = 0
        return {"total_variants": len(self.df),
                "unique_genes": self.df["GeneSymbol"].nunique(),
                "pathogenic_count": p, "benign_count": b,
                "top_genes": self.df["GeneSymbol"].value_counts().head(10).to_dict()}

    def _to_records(self, df: pd.DataFrame):
        def g(row, col, default=""):
            v = row.get(col, default)
            return default if pd.isna(v) else v
        out = []
        for _, row in df.iterrows():
            ch, st, sp = g(row,"Chromosome"), g(row,"Start"), g(row,"Stop")
            out.append({
                "variation_id":       str(g(row,"VariationID")),
                "gene":               str(g(row,"GeneSymbol")),
                "name":               str(g(row,"Name")),
                "type":               str(g(row,"Type")),
                "significance":       str(g(row,"ClinicalSignificance","Unknown")),
                "significance_simple": int(g(row,"ClinSigSimple",-1))
                    if str(g(row,"ClinSigSimple","")).strip() not in ("","nan") else -1,
                "phenotype":          str(g(row,"PhenotypeList")),
                "review_status":      str(g(row,"ReviewStatus")),
                "submitters":         int(g(row,"NumberSubmitters",0))
                    if str(g(row,"NumberSubmitters","")).strip() not in ("","nan") else 0,
                "chromosome":         str(ch),
                "position":           f"{ch}:{st}-{sp}",
                "ref":                str(g(row,"ReferenceAllele")),
                "alt":                str(g(row,"AlternateAllele")),
                "dbsnp":              str(g(row,"RS# (dbSNP)")),
                "last_evaluated":     str(g(row,"LastEvaluated")),
            })
        return out
