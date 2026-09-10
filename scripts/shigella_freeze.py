"""
STEP 1 of 2 — build the S. flexneri gene sets.

This script loads ONLY GeneID / GeneName / Annotation from comparison alpha.
The 'Log2 Fold change' and 'P-value' columns are never read here, so set
membership cannot be influenced by which direction a gene moved.
Effect sizes are loaded separately in step 2, after this file is written.
"""
import pandas as pd

OUT = "/mnt/user-data/outputs"
FROZEN = "2026-09-08"

# comparison alpha occupies columns 0-4; deliberately skipping cols 2 and 3
raw = pd.read_excel("raw/tableS2.xlsx", sheet_name="Comparisons",
                    header=2, usecols=[0, 1, 4])
raw.columns = ["gene_id", "gene_name", "annotation"]
alpha = raw.dropna(subset=["gene_id"]).copy()
alpha["gene_name"] = alpha["gene_name"].astype(str).str.strip()
alpha["annotation"] = alpha["annotation"].astype(str).str.strip()
print(f"comparison alpha genes loaded (no stats): {len(alpha)}")

# ---------------------------------------------------------------- gene sets
# Same seven categories as the Pseudomonas ontology. Membership decided from
# the enteric gene name and the annotation string only.
NAME_PREFIX = {
    "Iron uptake and storage": [
        "ent", "fep", "fes", "fhu", "iuc", "iut", "feo", "sit", "fec",
        "exb", "tonb", "ftn", "bfr", "fur", "shu", "chu", "efe", "ybt"],
    "Oxidative stress response": [
        "sod", "kat", "ahp", "tpx", "trx", "grx", "gor", " osm",
        "oxyr", "sox", "yaa", "bcp", "dps"],
    "Anaerobic respiration": [
        "nar", "nap", "nir", "nrf", "frd", "dms", "tor", "fdn", "fdh",
        "hya", "hyb", "hyc", "fnr", "arc", "app", "cyd", "cbd", "pfl", "adh"],
    "Quorum sensing and biofilm": [
        "lsr", "lux", "sdia", "csg", "bcs", "pga", "flu", "wca", "ymg"],
    "Motility": ["fli", "flg", "flh", "che", "mot", "fim", "pil"],
    "Secretion and virulence": [
        "ipa", "mxi", "spa", "icsa", "icsb", "vir", "ospb", "ospc", "ospd",
        "ospe", "ospf", "ospg", "sep", "acp", "sen", "set"],
    "Central carbon and amino acid metabolism": [],   # annotation-driven only
}

ANNOT_RX = {
    "Iron uptake and storage":
        r"siderophore|enterochelin|enterobactin|aerobactin|ferrichrome|"
        r"ferric|ferrous|iron|heme|haem|ferritin|tonb",
    "Oxidative stress response":
        r"superoxide dismutase|catalase|hydroperoxid|peroxidase|peroxired|"
        r"thioredoxin|glutaredoxin|glutathione reductase|oxidative stress",
    "Anaerobic respiration":
        r"nitrate reductase|nitrite reductase|fumarate reductase|"
        r"trimethylamine|dimethyl sulfoxide reductase|formate dehydrogenase|"
        r"hydrogenase|anaerobic|pyruvate formate|cytochrome (bd|d ubiquinol)",
    "Quorum sensing and biofilm":
        r"quorum|autoinducer|curli|cellulose synth|biofilm|poly-beta-1,6|"
        r"antigen 43",
    "Motility":
        r"flagell|chemotaxis|methyl-accepting|motility|fimbri|pilus|pili",
    "Secretion and virulence":
        r"type III secretion|invasion plasmid|invasin|effector|"
        r"secretion system|enterotoxin|hemolysin|actin",
    "Central carbon and amino acid metabolism":
        r"dehydrogenase|synthase|synthetase|aminotransferase|transaminase|"
        r"decarboxylase|isomerase|aldolase|kinase|citrate|succinate|malate|"
        r"biosynthesis|amino acid|glycolysis|tricarboxylic",
}

# genes to force out of a set even when a pattern matches (documented reasons)
EXCLUDE = {
    "Iron uptake and storage": {
        # assimilatory / cofactor, not iron acquisition
        "cysg", "hemb", "hemc", "hemd", "heme", "hemf", "hemg", "hemh",
        "heml", "hemn", "hemx", "nirb", "nird",
    },
    "Anaerobic respiration": {
        "nirb", "nird",          # assimilatory nitrite reduction
        "arca",                  # SEE NOTE: enteric ArcA is the aerobic
                                 # respiration control regulator, NOT the
                                 # arginine deiminase of P. aeruginosa.
    },
}

NOTES = [
    "arcA is EXCLUDED from Anaerobic respiration here and INCLUDED in the "
    "P. aeruginosa set. The two are unrelated genes: in Enterobacteriaceae "
    "arcA encodes the aerobic respiration control response regulator; in "
    "P. aeruginosa it encodes arginine deiminase. Scoring them as one "
    "category across species would be a false ortholog match.",
    "nirB/nirD excluded from Anaerobic respiration in both organisms "
    "(assimilatory nitrogen reduction), consistent with the Pseudomonas freeze.",
    "This table lists only the 292 significant genes, not the full "
    "transcriptome. Set sizes therefore count significant members only and "
    "enrichment testing is NOT possible for this arm — see step 2.",
]


def assign(row):
    name = row["gene_name"].lower()
    annot = row["annotation"].lower()
    hits = []
    for cat in ANNOT_RX:
        if name in EXCLUDE.get(cat, set()):
            continue
        by_name = any(name.startswith(p.strip()) for p in NAME_PREFIX[cat] if p.strip())
        by_annot = bool(pd.Series([annot]).str.contains(
            ANNOT_RX[cat], regex=True).iloc[0])
        if by_name or by_annot:
            hits.append(cat)
    # a gene matching iron AND metabolism is iron (more specific category)
    for specific in ["Iron uptake and storage", "Secretion and virulence",
                     "Anaerobic respiration", "Oxidative stress response",
                     "Motility", "Quorum sensing and biofilm"]:
        if specific in hits:
            return specific
    return hits[0] if hits else None


alpha["pathway"] = alpha.apply(assign, axis=1)
sets = alpha.dropna(subset=["pathway"])

sets[["pathway", "gene_id", "gene_name", "annotation"]].sort_values(
    ["pathway", "gene_name"]).to_csv(
    f"{OUT}/shigella_frozen_ontology_{FROZEN}.csv", index=False)

with open(f"{OUT}/shigella_ontology_curation_log.md", "w") as fh:
    fh.write(f"# S. flexneri ontology curation log\n\nFrozen: {FROZEN}\n\n")
    fh.write("Built from GeneID / GeneName / Annotation only. The fold-change "
             "and p-value columns were not loaded by the script that assigned "
             "membership.\n\n## Set sizes (significant genes only)\n\n")
    fh.write("|pathway|genes|\n|---|---|\n")
    for p, g in sets.groupby("pathway"):
        fh.write(f"|{p}|{len(g)}|\n")
    fh.write(f"|(unassigned)|{alpha['pathway'].isna().sum()}|\n")
    fh.write("\n## Notes and cross-species cautions\n\n")
    for n in NOTES:
        fh.write(f"- {n}\n")

print("\nSET SIZES")
print(sets.groupby("pathway").size().to_string())
print(f"unassigned: {alpha['pathway'].isna().sum()}")
