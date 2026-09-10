"""
Vergara-Irigaray Table S1 — S. flexneri WT anaerobic vs aerobic.

Parsing note: the table carries merged cells, so 'Description' repeats and the
numeric columns shift. Column 4 is log2FC(WT no O2 / WT O2); column 5 is the
dfnr/WT comparison. COG section headers appear as full-width rows and are
captured as the paper's own functional grouping.

Membership is assigned from gene name + description only, using the same
category definitions frozen for the iron arm. The fold-change column is not
consulted during assignment.
"""
import re
import pandas as pd
from docx import Document

OUT = "/mnt/user-data/outputs"

doc = Document("raw/vergara_s1.docx")
t = doc.tables[0]

rows, cog = [], None
for r in t.rows[2:]:
    cells = [c.text.strip().replace("\n", " ") for c in r.cells]
    uniq = list(dict.fromkeys([c for c in cells if c]))
    # section header: one repeated value across the row
    if len(uniq) == 1:
        cog = uniq[0]
        continue
    if not cells[0].startswith("SF5M90T"):
        continue
    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    rows.append(dict(orf=cells[0], gene=cells[1], desc=cells[2],
                     cog=cog, log2FC_anaer=num(cells[4]),
                     log2FC_fnr=num(cells[5])))

df = pd.DataFrame(rows)
df = df[df.log2FC_anaer.notna()]
print(f"genes parsed: {len(df)}   (paper reports 528 chromosomal DE genes)")
print(f"up: {(df.log2FC_anaer>0).sum()}   down: {(df.log2FC_anaer<0).sum()}\n")

# ---- category assignment: name + description only -------------------------
NAME_PREFIX = {
    "Iron uptake and storage": ["ent", "fep", "fes", "fhu", "iuc", "iut",
                                "feo", "sit", "fec", "exb", "tonb", "ftn",
                                "bfr", "fur", "shu", "chu", "suf", "ybt"],
    "Oxidative stress response": ["sod", "kat", "ahp", "tpx", "trx", "grx",
                                  "gor", "oxyr", "sox", "bcp", "dps"],
    "Anaerobic respiration": ["nar", "nap", "nir", "nrf", "frd", "dms", "tor",
                              "fdn", "fdh", "hya", "hyb", "hyc", "hyd", "fnr",
                              "app", "cyd", "pfl", "ttr", "yne"],
    "Quorum sensing and biofilm": ["lsr", "lux", "sdia", "csg", "bcs", "pga",
                                   "flu", "ymg"],
    "Motility": ["fli", "flg", "flh", "che", "mot", "fim", "pil"],
    "Secretion and virulence": ["ipa", "mxi", "spa", "ics", "vir", "osp",
                                "sep", "sen", "set", "shi", "shf"],
    "Central carbon and amino acid metabolism": [],
}
ANNOT_RX = {
    "Iron uptake and storage":
        r"siderophore|enterochelin|enterobactin|aerobactin|ferrichrome|"
        r"ferric|ferrous|iron|heme|haem|ferritin|tonb",
    "Oxidative stress response":
        r"superoxide dismutase|catalase|hydroperoxid|peroxidase|peroxired|"
        r"thioredoxin|glutaredoxin|oxidative stress",
    "Anaerobic respiration":
        r"nitrate reductase|nitrite reductase|fumarate reductase|hydrogenase|"
        r"formate dehydrogenase|trimethylamine|dimethyl sulfoxide reductase|"
        r"anaerobic|pyruvate formate|cytochrome bd",
    "Quorum sensing and biofilm":
        r"quorum|autoinducer|curli|cellulose synth|biofilm|antigen 43",
    "Motility": r"flagell|chemotaxis|methyl-accepting|motility|fimbri|pilus",
    "Secretion and virulence":
        r"type III secretion|invasion plasmid|invasin|effector|"
        r"secretion system|enterotoxin|hemolysin",
    "Central carbon and amino acid metabolism":
        r"dehydrogenase|synthase|synthetase|aminotransferase|decarboxylase|"
        r"isomerase|aldolase|citrate|succinate|malate|biosynthesis|"
        r"amino acid|glycolysis|tricarboxylic",
}
# arcA excluded: enteric ArcA is the aerobic respiration control regulator,
# an unrelated gene from the P. aeruginosa arcA (arginine deiminase).
EXCLUDE = {"Anaerobic respiration": {"arca", "nirb", "nird"},
           # Same rule applied in the P. aeruginosa freeze: proteins that
           # merely CONTAIN iron (respiratory Fe-S subunits, cytochrome c
           # maturation, heme export) are not iron acquisition or storage.
           "Iron uptake and storage": {
               "cysg", "nirb", "nird",
               "ccma", "ccmb", "ccmc", "ccmd", "ccme", "ccmf", "ccmg", "ccmh",
               "hyca", "hycb", "hycc", "hycd", "hyce", "hycf", "hycg",
               "frda", "frdb", "frdc", "frdd", "sdha", "sdhb", "sdhc", "sdhd",
               "fdoh", "fdog", "fdoi", "fdnh", "fdng", "nrfb", "nrfc",
               "adhe", "hmpa", "napb", "napf", "napg", "naph"}}

ORDER = ["Iron uptake and storage", "Secretion and virulence",
         "Anaerobic respiration", "Oxidative stress response",
         "Motility", "Quorum sensing and biofilm",
         "Central carbon and amino acid metabolism"]


def assign(r):
    name, desc = str(r.gene).lower().strip(), str(r.desc).lower()
    for cat in ORDER:
        if name in EXCLUDE.get(cat, set()):
            continue
        if any(name.startswith(p) for p in NAME_PREFIX[cat] if p):
            return cat
        if re.search(ANNOT_RX[cat], desc):
            return cat
    return None


df["pathway"] = df.apply(assign, axis=1)
sets = df.dropna(subset=["pathway"])

out = []
for p, g in sets.groupby("pathway"):
    up, dn = int((g.log2FC_anaer > 0).sum()), int((g.log2FC_anaer < 0).sum())
    call = ("induced" if dn == 0 else "repressed" if up == 0 else
            "induced" if up >= 3 * dn else
            "repressed" if dn >= 3 * up else "mixed")
    out.append(dict(pathway=p, sig_genes=len(g), up=up, down=dn,
                    median_logFC=round(g.log2FC_anaer.median(), 2),
                    direction=call))
res = pd.DataFrame(out).sort_values("pathway")
res.to_csv(f"{OUT}/shigella_oxygen_pathway_scores.csv", index=False)
sets.to_csv(f"{OUT}/shigella_oxygen_gene_level.csv", index=False)

print("S. FLEXNERI — anaerobic vs aerobic (WT M90T)")
print(res.to_string(index=False))

print("\nIron set members:")
for _, r in sets[sets.pathway == "Iron uptake and storage"].sort_values(
        "log2FC_anaer").iterrows():
    print(f"  {str(r.gene):<8}{r.log2FC_anaer:>7.2f}   {str(r.desc)[:46]}")
