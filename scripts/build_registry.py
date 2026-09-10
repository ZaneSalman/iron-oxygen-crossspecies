"""
GSE81364 — contrast registry + pathway scoring.

Two ontologies are used, and they are NOT equivalent in provenance:

  A. PseudoCAP functional classes. Curator-assigned, shipped inside the GEO
     annotation columns. Not invented here.
  B. Curated gene sets for the four protocol categories PseudoCAP does not
     cover (iron, oxidative stress, quorum sensing, anaerobic respiration).
     These are keyword-derived and MUST be reviewed and frozen by the analyst
     before any convergence claim. Membership is exported for that review.
"""
import gzip
import pandas as pd
from scipy.stats import fisher_exact

OUT = "/mnt/user-data/outputs"
FDR, LFC = 0.05, 1.0

CONTRASTS = {
    "2vs1": dict(file="raw/GSE81364_genelist_P_aerug_paired_2vs1_txt.gz",
                 treat="40 uM HHQ",  ref="LB"),
    "3vs1": dict(file="raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz",
                 treat="40 uM PQS",  ref="LB"),
    "4vs1": dict(file="raw/GSE81364_genelist_P_aerug_paired_4vs1_txt.gz",
                 treat="40 uM HQNO", ref="LB"),
    "5vs1": dict(file="raw/GSE81364_genelist_P_aerug_paired_5vs1_txt.gz",
                 treat="1 mM IPTG",  ref="LB"),
}

# ---- B. Curated sets: (regex over gene symbol + annotation text, explicit loci)
CURATED = {
    "Iron uptake": (
        r"pyoverdine|pyochelin|siderophore|ferric|ferrous|ferri|heme|haem|"
        r"iron[- ]?(uptake|transport|starvation)|TonB",
        ["PA4468", "PA4469", "PA4470", "PA4471"]),
    "Iron storage": (r"bacterioferritin|ferritin", []),
    "Oxidative stress": (
        r"superoxide dismutase|catalase|alkyl hydroperoxide|peroxidase|"
        r"glutathione|thioredoxin|oxidative stress", []),
    "Quorum sensing / biofilm": (
        r"quorum|autoinducer|homoserine lactone|quinolone signal|phenazine|"
        r"lectin|alginate|biofilm", []),
    "Anaerobic respiration": (
        r"nitrate reductase|nitrite reductase|nitric oxide reductase|"
        r"nitrous oxide|denitrificat|anaerobic|arginine deiminase", []),
}

# ---- A. PseudoCAP classes mapped to protocol categories
PSEUDOCAP = {
    "Central carbon & amino acid metabolism":
        ["Carbon compound catabolism", "Central intermediary metabolism",
         "Amino acid biosynthesis and metabolism", "Energy metabolism"],
    "Motility": ["Motility & Attachment", "Chemotaxis"],
    "Secretion & virulence":
        ["Protein secretion", "Secreted Factors (toxins, enzymes, alginate)"],
}


def load(path):
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh, sep="\t", low_memory=False)
    df["locus"] = df["ID"].str.extract(r"^(PA\d+)", expand=False)
    df["classes"] = (df["Target.Description"]
                     .str.extract(r"/FUNCTION=([^/]+)", expand=False)
                     .fillna("").str.strip())
    df["text"] = (df["Gene.Symbol"].fillna("") + " " +
                  df["Gene.Title"].fillna("") + " " +
                  df["Target.Description"].fillna(""))
    df["sig"] = (df["adj.P.Val"] < FDR) & (df["logFC"].abs() > LFC)
    return df


def members(df, name):
    if name in CURATED:
        rx, loci = CURATED[name]
        return df["text"].str.contains(rx, case=False, regex=True, na=False) | \
               df["locus"].isin(loci)
    return df["classes"].apply(
        lambda c: any(k in [p.strip() for p in c.split(";")]
                      for k in PSEUDOCAP[name]))


def score(df, mask):
    """Direction call for one pathway in one contrast."""
    n = int(mask.sum())
    hits = df[mask & df["sig"]]
    up, dn = int((hits.logFC > 0).sum()), int((hits.logFC < 0).sum())
    a, b = len(hits), n - len(hits)
    c = int(df["sig"].sum()) - a
    d = len(df) - n - c
    p = fisher_exact([[a, b], [c, d]], alternative="greater")[1] if n else 1.0
    if up + dn == 0:
        call = "unresolved"
    elif up and dn == 0:
        call = "induced"
    elif dn and up == 0:
        call = "repressed"
    else:
        call = "induced" if up >= 3 * dn else \
               "repressed" if dn >= 3 * up else "mixed"
    med = hits.logFC.median() if len(hits) else float("nan")
    return dict(genes_in_set=n, sig=len(hits), up=up, down=dn,
                median_logFC=round(med, 2) if med == med else "",
                enrich_p=f"{p:.2e}", direction=call)


frames = {k: load(v["file"]) for k, v in CONTRASTS.items()}
ref = frames["3vs1"]

# ---------- registry ----------
reg = []
for k, meta in CONTRASTS.items():
    d = frames[k]
    reg.append(dict(
        contrast=k, series="GSE81364", organism="Pseudomonas aeruginosa",
        strain="alkylquinolone-null (delta-4AQ) mutant",
        treatment=meta["treat"], control=meta["ref"], medium="LB",
        n_per_group=2, pairing="paired by experiment day (A/B)",
        platform="Affymetrix P. aeruginosa array (PseudoCAP annotation)",
        technology="microarray", normalization="submitter (see summary PDF)",
        stat_method="paired moderated t-test (limma-style)",
        identifiers="PAxxxx locus tags", probes=len(d),
        sig_genes=int(d["sig"].sum()),
        raw_available="yes (GSE81364_RAW.tar, 10 CEL)",
        role="quantitative reanalysis"))
reg = pd.DataFrame(reg)
reg.to_csv(f"{OUT}/contrast_registry.csv", index=False)

# ---------- pathway matrix ----------
rows, memb = [], []
for name in list(CURATED) + list(PSEUDOCAP):
    mask = members(ref, name)
    src = "curated (REVIEW)" if name in CURATED else "PseudoCAP"
    for k in CONTRASTS:
        d = frames[k]
        m = members(d, name)
        rows.append(dict(pathway=name, ontology=src, contrast=k,
                         treatment=CONTRASTS[k]["treat"], **score(d, m)))
    for _, r in ref[mask].iterrows():
        memb.append(dict(pathway=name, ontology=src, probe=r["ID"],
                         locus=r["locus"], symbol=r["Gene.Symbol"],
                         title=r["Gene.Title"],
                         logFC_PQS=round(r["logFC"], 2),
                         adjP_PQS=f'{r["adj.P.Val"]:.2e}'))

long = pd.DataFrame(rows)
long.to_csv(f"{OUT}/pathway_scores_long.csv", index=False)
pd.DataFrame(memb).sort_values(
    ["pathway", "logFC_PQS"], ascending=[True, False]).to_csv(
    f"{OUT}/pathway_gene_membership.csv", index=False)

matrix = long.pivot(index="pathway", columns="treatment", values="direction")
matrix = matrix[["40 uM HHQ", "40 uM PQS", "40 uM HQNO", "1 mM IPTG"]]
matrix.to_csv(f"{OUT}/pathway_direction_matrix.csv")

print(f"Thresholds: adj.P < {FDR}, |logFC| > {LFC}\n")
print("PATHWAY DIRECTION MATRIX")
print(matrix.to_string())
print("\nPQS (3vs1) detail")
print(long[long.contrast == "3vs1"][
    ["pathway", "genes_in_set", "sig", "up", "down",
     "median_logFC", "enrich_p"]].to_string(index=False))
