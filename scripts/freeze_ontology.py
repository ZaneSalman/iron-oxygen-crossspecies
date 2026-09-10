"""
FROZEN ONTOLOGY — GSE81364 / Iron-Oxygen-Quorum project
Frozen 2026-09-08. Curated by explicit locus list, not keyword matching.

Curation rule applied: membership decided on annotated gene function only.
The logFC/adj.P columns were not consulted for any include/exclude decision.

Supersedes the keyword-derived draft, which had two defects:
  (1) the token "alginate" matched the PseudoCAP class label
      "Secreted Factors (toxins, enzymes, alginate)", pulling 51 secreted
      factors into quorum sensing;
  (2) the token "glutathione" pulled xenobiotic-detox glutathione
      S-transferases into oxidative stress.
"""
import gzip
import pandas as pd
from scipy.stats import fisher_exact

OUT = "/mnt/user-data/outputs"
FROZEN = "2026-09-08"
FDR, LFC = 0.05, 1.0

CURATED = {
    "Iron uptake and storage": dict(loci=[
        # siderophore biosynthesis + regulation
        "PA2386", "PA2399", "PA2397", "PA2396", "PA2426", "PA2385",
        "PA4231", "PA4230", "PA4229", "PA4228", "PA4226", "PA4225",
        "PA4224", "PA4227",
        # siderophore receptors / transport
        "PA2398", "PA4221", "PA2688", "PA4159", "PA4158", "PA4160",
        "PA4161", "PA0470", "PA0931", "PA1365",
        # heme acquisition
        "PA3407", "PA3408", "PA4710", "PA0672", "PA1302",
        # ferrous / ferric transport
        "PA4358", "PA4687", "PA5216", "PA5217",
        # TonB and TonB-dependent receptors
        "PA5531", "PA0151", "PA0192", "PA1271", "PA1322", "PA1910",
        "PA1922", "PA2335", "PA2466", "PA2911", "PA3268", "PA4156",
        "PA4168", "PA4514", "PA4675", "PA5505",
        # regulator
        "PA4764",
        # storage
        "PA4235", "PA3531", "PA4880",
    ]),
    "Oxidative stress response": dict(loci=[
        "PA4468", "PA4366",                                # sodM, sodB
        "PA4236", "PA4613", "PA2147", "PA2185",            # katA/B/E/N
        "PA0139", "PA0140", "PA0848",                      # ahpC/F, AhpD-like
        "PA2532", "PA1008",                                # tpx, bcp (prx)
        "PA5240", "PA2616", "PA0849",                      # trxA, trxB1/2
        "PA4061", "PA2694", "PA0953",                      # probable thioredoxins
        "PA2025", "PA0407",                                # gor, gshB
        "PA1287", "PA2826", "PA0838",                      # Gpx
        "PA4587", "PA3529", "PA5344",                      # ccpR, peroxidase, oxyR
    ]),
    "Anaerobic respiration": dict(loci=[
        "PA3875", "PA3874", "PA3872", "PA3873",            # narGHIJ
        "PA1174", "PA1175", "PA1177",                      # napADE
        "PA0519", "PA0524", "PA0523", "PA3392",            # nirS, norBC, nosZ
        "PA1544", "PA0527",                                # anr, dnr
        "PA0291", "PA5171",                                # oprE, arcA
    ]),
    "Quorum sensing and biofilm": dict(loci=[
        # signal synthesis / reception / regulation
        "PA1432", "PA1430", "PA3476", "PA3477",            # lasI/R, rhlI/R
        "PA0996", "PA0997", "PA0998", "PA0999", "PA1000",  # pqsABCDE
        "PA2587", "PA1003", "PA1431", "PA1898",            # pqsH, mvfR, rsaL, qscR
        # phenazines (canonical QS output — see note)
        "PA4210", "PA4211", "PA1901", "PA1902", "PA1903",
        "PA1904", "PA1905", "PA4209", "PA0051",
        # lectins
        "PA2570", "PA3361",
        # alginate / biofilm matrix
        "PA3540", "PA3541", "PA3542", "PA3543", "PA3544", "PA3545",
        "PA3546", "PA3547", "PA3548", "PA3549", "PA3550", "PA3551",
        "PA5322", "PA5261", "PA5262", "PA5253", "PA5255", "PA4446",
        "PA0764", "PA0765", "PA0766",
    ]),
}

EXCLUSIONS = [
    ("Iron uptake and storage", "PA4468 sodM, PA2185 katN",
     "Fur-regulated but enzymatic function is redox -> Oxidative stress"),
    ("Iron uptake and storage", "PA4470 fumC1",
     "Fe-independent fumarase; iron-sparing metabolism -> central metabolism"),
    ("Iron uptake and storage", "PA4469, PA4471",
     "hypothetical proteins; no annotated function to justify membership"),
    ("Iron uptake and storage", "PA5034 hemE, PA2611 cysG, PA0511/0514/0516 nirJLF",
     "tetrapyrrole/cofactor biosynthesis, not iron acquisition"),
    ("Iron uptake and storage", "PA1475/1476/1477 ccmABC, PA5328",
     "cytochrome c maturation and export, not iron acquisition"),
    ("Iron uptake and storage", "PA1008 bcp",
     "named 'bacterioferritin comigratory' but is a peroxiredoxin -> Oxidative stress"),
    ("Oxidative stress response", "PA0473/1033/1185/1655/1890/2473/2813/2821/3035/4401",
     "probable glutathione S-transferases; xenobiotic detox, not ROS defense"),
    ("Oxidative stress response", "PA0710/3524/5111 gloA1-3, PA1813",
     "methylglyoxal detoxification (glyoxalase system)"),
    ("Oxidative stress response", "PA1207 kefB",
     "potassium efflux; glutathione-gated but not a redox defense enzyme"),
    ("Oxidative stress response", "PA5421 fdhA, PA2717 cpo",
     "formaldehyde metabolism; haloperoxidase - neither is ROS defense"),
    ("Anaerobic respiration", "PA1779, PA1780 nirD, PA1781 nirB",
     "assimilatory nitrate/nitrite reduction (N assimilation), not respiration"),
    ("Anaerobic respiration", "PA4130",
     "probable sulfite OR nitrite reductase; assignment too uncertain"),
    ("Quorum sensing and biofilm", "51 secreted factors (exoS/T/Y, apr*, lasA/B, "
     "toxA, plc*, lip*, pys2, hcpA, est A, pepA ...)",
     "ARTIFACT: matched the PseudoCAP class label 'Secreted Factors (toxins, "
     "enzymes, alginate)', not gene function -> Secretion & virulence"),
    ("Quorum sensing and biofilm", "pch*, pvd*, pvc* operons",
     "siderophore biosynthesis, entered via same class-label artifact -> Iron"),
]

NOTES = [
    "arcA (PA5171) retained in Anaerobic respiration: arginine deiminase is "
    "anaerobic energy generation by fermentation, not respiration. Flagged.",
    "Phenazine genes retained in Quorum sensing: pyocyanin is the standard QS "
    "output readout in P. aeruginosa. This makes the category machinery+output "
    "rather than machinery-only; it is a defensible but reviewable choice.",
    "pvcABCD retained in Iron: annotated as pyoverdine biosynthesis on this "
    "array, though later work reassigns them to paerucumarin. Flagged.",
]

PSEUDOCAP = {
    "Central carbon and amino acid metabolism":
        ["Carbon compound catabolism", "Central intermediary metabolism",
         "Amino acid biosynthesis and metabolism", "Energy metabolism"],
    "Motility": ["Motility & Attachment", "Chemotaxis"],
    "Secretion and virulence":
        ["Protein secretion", "Secreted Factors (toxins, enzymes, alginate)"],
}

CONTRASTS = {
    "2vs1": ("raw/GSE81364_genelist_P_aerug_paired_2vs1_txt.gz", "40 uM HHQ"),
    "3vs1": ("raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz", "40 uM PQS"),
    "4vs1": ("raw/GSE81364_genelist_P_aerug_paired_4vs1_txt.gz", "40 uM HQNO"),
    "5vs1": ("raw/GSE81364_genelist_P_aerug_paired_5vs1_txt.gz", "1 mM IPTG"),
}


def load(path):
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh, sep="\t", low_memory=False)
    df["locus"] = df["ID"].str.extract(r"^(PA\d+)", expand=False)
    df["desc"] = df["Target.Description"].str.extract(r"/DEF=([^/]+)", expand=False)
    df["classes"] = (df["Target.Description"]
                     .str.extract(r"/FUNCTION=([^/]+)", expand=False)
                     .fillna("").str.strip())
    df["sig"] = (df["adj.P.Val"] < FDR) & (df["logFC"].abs() > LFC)
    return df


frames = {k: load(v[0]) for k, v in CONTRASTS.items()}
ref = frames["3vs1"]

# --- verify every curated locus is actually on the array ---
missing = []
for name, spec in CURATED.items():
    on = set(ref["locus"].dropna())
    for l in spec["loci"]:
        if l not in on:
            missing.append((name, l))
if missing:
    print("WARNING - loci not on array:", missing)

# --- write frozen ontology ---
rows = []
for name, spec in CURATED.items():
    for l in spec["loci"]:
        r = ref[ref["locus"] == l]
        if r.empty:
            continue
        r = r.iloc[0]
        rows.append(dict(pathway=name, ontology="curated", frozen=FROZEN,
                         locus=l, symbol=r["Gene.Symbol"],
                         description=r["desc"], probe=r["ID"]))
for name, keys in PSEUDOCAP.items():
    m = ref["classes"].apply(
        lambda c: any(k in [p.strip() for p in c.split(";")] for k in keys))
    for _, r in ref[m].iterrows():
        rows.append(dict(pathway=name, ontology="PseudoCAP", frozen=FROZEN,
                         locus=r["locus"], symbol=r["Gene.Symbol"],
                         description=r["desc"], probe=r["ID"]))
onto = pd.DataFrame(rows)
onto.to_csv(f"{OUT}/frozen_ontology_{FROZEN}.csv", index=False)

# --- changelog ---
with open(f"{OUT}/ontology_curation_log.md", "w") as fh:
    fh.write(f"# Ontology curation log\n\nFrozen: {FROZEN}\n\n")
    fh.write(f"Thresholds frozen with it: adj.P.Val < {FDR}, |logFC| > {LFC}\n\n")
    fh.write("Membership decided on annotated gene function only. Effect sizes "
             "were not consulted for any include/exclude decision.\n\n")
    fh.write("## Set sizes\n\n|pathway|ontology|genes|\n|---|---|---|\n")
    for (p, o), g in onto.groupby(["pathway", "ontology"]):
        fh.write(f"|{p}|{o}|{len(g)}|\n")
    fh.write("\n## Exclusions from the keyword-derived draft\n\n")
    fh.write("|pathway|excluded|reason|\n|---|---|---|\n")
    for p, g, why in EXCLUSIONS:
        fh.write(f"|{p}|{g}|{why}|\n")
    fh.write("\n## Retained with reservations\n\n")
    for n in NOTES:
        fh.write(f"- {n}\n")

# --- rescore against frozen sets ---
def score(df, mask):
    hits = df[mask & df["sig"]]
    n = int(mask.sum())
    up, dn = int((hits.logFC > 0).sum()), int((hits.logFC < 0).sum())
    a, b = len(hits), n - len(hits)
    c = int(df["sig"].sum()) - a
    d = len(df) - n - c
    p = fisher_exact([[a, b], [c, d]], alternative="greater")[1] if n else 1.0
    call = ("unresolved" if up + dn == 0 else
            "induced" if dn == 0 else "repressed" if up == 0 else
            "induced" if up >= 3 * dn else
            "repressed" if dn >= 3 * up else "mixed")
    med = hits.logFC.median() if len(hits) else float("nan")
    return dict(genes_in_set=n, sig=len(hits), up=up, down=dn,
                median_logFC=round(med, 2) if med == med else "",
                enrich_p=f"{p:.2e}", direction=call)


out = []
for name in list(CURATED) + list(PSEUDOCAP):
    for k, (_, treat) in CONTRASTS.items():
        df = frames[k]
        if name in CURATED:
            m = df["locus"].isin(CURATED[name]["loci"])
        else:
            keys = PSEUDOCAP[name]
            m = df["classes"].apply(
                lambda c: any(x in [p.strip() for p in c.split(";")] for x in keys))
        out.append(dict(pathway=name, contrast=k, treatment=treat, **score(df, m)))

long = pd.DataFrame(out)
long.to_csv(f"{OUT}/pathway_scores_frozen.csv", index=False)
mat = long.pivot(index="pathway", columns="treatment", values="direction")[
    ["40 uM HHQ", "40 uM PQS", "40 uM HQNO", "1 mM IPTG"]]
mat.to_csv(f"{OUT}/pathway_direction_matrix_frozen.csv")

print("SET SIZES (frozen vs draft)")
print(onto.groupby(["ontology", "pathway"]).size().to_string())
print("\nPATHWAY DIRECTION MATRIX (frozen)")
print(mat.to_string())
print("\nPQS detail")
print(long[long.contrast == "3vs1"][
    ["pathway", "genes_in_set", "sig", "up", "down",
     "median_logFC", "enrich_p"]].to_string(index=False))
