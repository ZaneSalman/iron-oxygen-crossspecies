"""
REVISION 2 — rebuilt 2026-09-09 in response to independent review.

Changes, by cause:
  * word-boundary bug: the anaerobic pattern listed "hydrogenase", which matches
    inside "dehydrogenase". Every dehydrogenase in both transcriptomes matched.
    Anaerobic respiration is now built from an explicit gene-family list, not
    from annotation text.
  * adhE remained in the S. flexneri iron set; the correction had reached the
    P. aeruginosa file only.
  * P. aeruginosa sets were not disjoint (44 loci in two categories) because
    curated and PseudoCAP sets were written in independent passes. Curated
    assignment now takes precedence and disjointness is asserted.
  * decision 2 resolved: the category is kept STRICTLY RESPIRATORY. Fermentation
    is excluded in both organisms (P. aeruginosa arcA; S. flexneri pflA/pflB/adhE).
  * decision 3 resolved: suf moves from Iron to Oxidative stress.
  * decision 1 resolved: regulators stay, but carry a `regulator` flag so the
    matrix can be computed both ways.
"""
import re
import gzip
import pandas as pd

OUT = "/mnt/user-data/outputs"
REV = "2026-09-09"
FDR, LFC = 0.05, 1.0

# ===================================================== P. AERUGINOSA =========
PA_CURATED = {
    "Iron uptake and storage": [
        "PA2386", "PA2399", "PA2397", "PA2396", "PA2426", "PA2385",
        "PA4231", "PA4230", "PA4229", "PA4228", "PA4226", "PA4225",
        "PA4224", "PA4227", "PA2398", "PA4221", "PA2688", "PA4159",
        "PA4158", "PA4160", "PA4161", "PA0470", "PA0931", "PA1365",
        "PA3407", "PA3408", "PA4710", "PA0672", "PA1302", "PA4358",
        "PA4687", "PA5216", "PA5217", "PA5531",
        # uncharacterised TonB-dependent receptors — sensitivity-tested below
        "PA0151", "PA0192", "PA1271", "PA1322", "PA1910", "PA1922",
        "PA2335", "PA2466", "PA2911", "PA3268", "PA4156", "PA4168",
        "PA4514", "PA4675", "PA5505",
        "PA4764", "PA4235", "PA3531", "PA4880"],
    "Oxidative stress response": [
        "PA4468", "PA4366", "PA4236", "PA4613", "PA2147", "PA2185",
        "PA0139", "PA0140", "PA0848", "PA2532", "PA1008", "PA5240",
        "PA2616", "PA0849", "PA4061", "PA2694", "PA0953", "PA2025",
        "PA0407", "PA1287", "PA2826", "PA0838", "PA4587", "PA3529", "PA5344"],
    # oprE and arcA removed per review
    "Anaerobic respiration": [
        "PA3875", "PA3874", "PA3872", "PA3873", "PA1174", "PA1175",
        "PA1177", "PA0519", "PA0524", "PA0523", "PA3392", "PA1544", "PA0527"],
    "Quorum sensing and biofilm": [
        "PA1432", "PA1430", "PA3476", "PA3477", "PA0996", "PA0997",
        "PA0998", "PA0999", "PA1000", "PA2587", "PA1003", "PA1431", "PA1898",
        "PA4210", "PA4211", "PA1901", "PA1902", "PA1903", "PA1904",
        "PA1905", "PA4209", "PA0051", "PA2570", "PA3361",
        "PA3540", "PA3541", "PA3542", "PA3543", "PA3544", "PA3545",
        "PA3546", "PA3547", "PA3548", "PA3549", "PA3550", "PA3551",
        "PA5322", "PA5261", "PA5262", "PA5253", "PA5255", "PA4446",
        "PA0764", "PA0765", "PA0766"],
}
PA_REGULATORS = {"PA4764", "PA2426", "PA4227", "PA1544", "PA0527", "PA5344",
                 "PA1430", "PA3477", "PA1003", "PA1431", "PA1898", "PA5261",
                 "PA5262", "PA5253", "PA5255"}
PA_TBDR = {"PA0151", "PA0192", "PA1271", "PA1322", "PA1910", "PA1922",
           "PA2335", "PA2466", "PA2911", "PA3268", "PA4156", "PA4168",
           "PA4514", "PA4675", "PA5505"}
PSEUDOCAP = {
    "Central carbon and amino acid metabolism":
        ["Carbon compound catabolism", "Central intermediary metabolism",
         "Amino acid biosynthesis and metabolism", "Energy metabolism"],
    "Motility": ["Motility & Attachment", "Chemotaxis"],
    "Secretion and virulence":
        ["Protein secretion", "Secreted Factors (toxins, enzymes, alginate)"],
}
PA_ORDER = list(PA_CURATED) + list(PSEUDOCAP)   # curated wins ties


def load_pa(path):
    with gzip.open(path, "rt") as fh:
        d = pd.read_csv(fh, sep="\t", low_memory=False)
    d["locus"] = d["ID"].str.extract(r"^(PA\d+)", expand=False)
    d["classes"] = (d["Target.Description"]
                    .str.extract(r"/FUNCTION=([^/]+)", expand=False)
                    .fillna("").str.strip())
    d["sig"] = (d["adj.P.Val"] < FDR) & (d["logFC"].abs() > LFC)
    return d


def pa_assign(row):
    for cat in PA_ORDER:                       # curated categories first
        if cat in PA_CURATED:
            if row["locus"] in PA_CURATED[cat]:
                return cat
        else:
            cls = [p.strip() for p in row["classes"].split(";")]
            if any(k in cls for k in PSEUDOCAP[cat]):
                return cat
    return None


pa_files = {
    "P. aeruginosa | iron (PQS)": "raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz",
}
pa = load_pa(pa_files["P. aeruginosa | iron (PQS)"])
pa["pathway"] = pa.apply(pa_assign, axis=1)
dupes = pa.dropna(subset=["pathway"]).groupby("locus")["pathway"].nunique()
assert (dupes > 1).sum() == 0, f"{(dupes>1).sum()} loci still double-assigned"
print(f"P. aeruginosa disjointness enforced: 0 loci in >1 category")

# ======================================================= S. FLEXNERI =========
# Anaerobic respiration rebuilt from explicit gene families (reviewer's list).
SF_ANAER = re.compile(
    r"^(nap|nar|frd|nrf|dms|tor|hya|hyb|hyc|hyp|fdn|fdo|glpA|glpB|glpC|dcu|nirC|fnr)",
    re.I)
SF_NAME = {
    "Iron uptake and storage": r"^(ent|fep|fes|fhu|iuc|iut|feo|sit|fec|exb|tonB|ftn|bfr|fur|shu|chu|dps)",
    "Oxidative stress response": r"^(sod|kat|ahp|tpx|trx|grx|gor|oxyR|sox|bcp|osmC|suf)",
    "Motility": r"^(fli|flg|flh|che|mot|fim|pil)",
    "Secretion and virulence": r"^(ipa|mxi|spa|ics|vir|osp|sep|sen|set)",
    "Quorum sensing and biofilm": r"^(lsr|lux|sdiA|csg|bcs|pga|flu)",
}
SF_ANNOT_CENTRAL = re.compile(
    r"dehydrogenase|synthase|synthetase|aminotransferase|decarboxylase|"
    r"isomerase|aldolase|citrate|succinate|malate|biosynthesis|amino acid|"
    r"glycolysis|tricarboxylic|transhydrogenase|oxidoreductase", re.I)
# explicit removals from the review
SF_DROP = {
    "adhe", "yihu", "osmy", "nrdh", "mrca", "ppic", "slpa",       # iron / ox / central
    "fdhf", "dmsa", "narq", "flha", "fliy",                       # pseudogenes, misname
    "cyda", "appc",                                               # O2-reducing oxidases
    "yhdh", "yiak", "ykge", "lrha", "nrdd", "nrdg",               # putative / not energy
    "pfla", "pflb",                                               # fermentation
    "ymgg", "shif",                                               # hypothetical / ambiguous
}
SF_TO_CENTRAL = {"epd", "tyra", "sdha", "sdhb", "sdhc", "sdhd", "glpd",
                 "acee", "acef", "pdhr", "gapa", "gnd", "gcd", "icda",
                 "alda", "beta", "betb", "udha", "nuoa", "nuob", "nuoc",
                 "nuod", "nuoe", "nuof", "nuog", "nuoh", "nuoi", "nuoj",
                 "nuok", "nuol", "nuom", "nuon"}
SF_TO_OXID = {"wrba"}
SF_REGULATORS = {"fnr", "soxr", "oxyr", "fur", "pdhr", "lrha", "hyca"}


def sf_assign(gene, annot):
    g = str(gene).lower().strip()
    if g in SF_DROP:
        return None
    if g in SF_TO_CENTRAL:
        return "Central carbon and amino acid metabolism"
    if g in SF_TO_OXID:
        return "Oxidative stress response"
    if SF_ANAER.match(g):
        return "Anaerobic respiration"
    for cat, rx in SF_NAME.items():
        if re.match(rx, g, re.I):
            return cat
    if SF_ANNOT_CENTRAL.search(str(annot)):
        return "Central carbon and amino acid metabolism"
    return None


# ---- iron arm
sf_i = pd.read_excel("raw/tableS2.xlsx", sheet_name="Comparisons",
                     header=2, usecols=[0, 1, 2, 3, 4])
sf_i.columns = ["gene_id", "gene_name", "log2FC", "p_value", "annotation"]
sf_i = sf_i.dropna(subset=["gene_id"])
sf_i["gene_name"] = sf_i.gene_name.astype(str).str.strip()
fes = sf_i[sf_i.gene_name.str.lower() == "fes"].iloc[0]["log2FC"]
sign = 1 if fes > 0 else -1
sf_i["logFC"] = sf_i["log2FC"] * sign
sf_i["pathway"] = sf_i.apply(lambda r: sf_assign(r.gene_name, r.annotation), axis=1)

# ---- oxygen arm
sf_o = pd.read_csv(f"{OUT}/shigella_oxygen_gene_level.csv")
sf_o = sf_o.drop_duplicates(subset=["orf"], keep="first")      # SF5M90T_602 dup
sf_o["logFC"] = sf_o["log2FC_anaer"]
sf_o["pathway"] = sf_o.apply(lambda r: sf_assign(r.gene, r.desc), axis=1)

# ======================================================== SCORING ============
def call(g, col="logFC"):
    up, dn = int((g[col] > 0).sum()), int((g[col] < 0).sum())
    if len(g) < 3:
        return "unresolved", up, dn          # n<3 cannot support a direction
    if dn == 0:
        return "induced", up, dn
    if up == 0:
        return "repressed", up, dn
    if up >= 3 * dn:
        return "induced", up, dn
    if dn >= 3 * up:
        return "repressed", up, dn
    return "mixed", up, dn


ARMS = {}
sig = pa[pa["sig"] & pa.pathway.notna()]
ARMS[("P. aeruginosa", "iron")] = sig.rename(columns={"logFC": "logFC"})
pa_o = load_pa if False else None
# Pseudomonas oxygen arm: reuse the frozen GSE17179 result, reassigned
g17 = pd.read_csv(f"{OUT}/gse17179_anaerobic_vs_aerobic.csv")
g17["locus"] = g17["ID_REF"].str.extract(r"^(PA\d+)", expand=False)
cls = pa[["locus", "classes"]].drop_duplicates("locus")
g17 = g17.merge(cls, on="locus", how="left")
g17["classes"] = g17["classes"].fillna("")
g17["pathway"] = g17.apply(pa_assign, axis=1)
ARMS[("P. aeruginosa", "oxygen")] = g17[g17["sig"] & g17.pathway.notna()]
ARMS[("S. flexneri", "iron")] = sf_i[sf_i.pathway.notna()]
ARMS[("S. flexneri", "oxygen")] = sf_o[sf_o.pathway.notna()]

CATS = ["Iron uptake and storage", "Anaerobic respiration",
        "Oxidative stress response", "Central carbon and amino acid metabolism",
        "Secretion and virulence", "Motility", "Quorum sensing and biofilm"]

rows, detail = [], []
for cat in CATS:
    row = {"pathway": cat}
    for (org, pert), d in ARMS.items():
        g = d[d.pathway == cat]
        c, up, dn = call(g)
        row[f"{org} | {pert}"] = c
        detail.append(dict(pathway=cat, organism=org, perturbation=pert,
                           n=len(g), up=up, down=dn,
                           median_logFC=round(g.logFC.median(), 2) if len(g) else "",
                           direction=c))
    rows.append(row)
mat = pd.DataFrame(rows).set_index("pathway")
mat.to_csv(f"{OUT}/master_2x2_matrix_rev2.csv")
pd.DataFrame(detail).to_csv(f"{OUT}/pathway_scores_rev2.csv", index=False)

# ---- sensitivity: iron call without uncharacterised TBDRs
g = ARMS[("P. aeruginosa", "iron")]
iron = g[g.pathway == "Iron uptake and storage"]
strict = iron[~iron.locus.isin(PA_TBDR)]
print(f"\nSENSITIVITY  P. aeruginosa iron:")
print(f"  with TBDRs    n={len(iron):>3}  {call(iron)[0]:<10} median {iron.logFC.median():.2f}")
print(f"  without TBDRs n={len(strict):>3}  {call(strict)[0]:<10} median {strict.logFC.median():.2f}")

pd.set_option("display.width", 220)
print("\nMASTER 2x2 — REVISION 2")
print(mat.to_string())
print("\nPer-cell detail")
print(pd.DataFrame(detail)[["pathway", "organism", "perturbation", "n",
                            "up", "down", "median_logFC", "direction"]].to_string(index=False))
