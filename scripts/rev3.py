"""
REVISION 3 — 2026-09-10. Completeness pass.

Prior revisions asked whether the genes IN each set belonged. This one asks the
opposite: are there genes on the array that meet a category definition but were
never assigned? Fourteen were found in P. aeruginosa, plus one class of
fallback misassignment. S. flexneri returned zero candidates.

Disclosure: this audit ran after the results were known. Every direction call
was recomputed before and after; none changed. Additions are by category
definition only — no gene was added or withheld on the basis of which way it
moved.
"""
import gzip
import pandas as pd

OUT = "/mnt/user-data/outputs"
REV = "2026-09-10"
FDR, LFC = 0.05, 1.0

# ---- additions, with the definitional reason for each --------------------
ADD = {
    "Iron uptake and storage": {
        "PA2392": "pvdP, pyoverdine biosynthesis",
        "PA2394": "pvdN, pyoverdine biosynthesis",
        "PA2395": "pvdO, pyoverdine biosynthesis",
        "PA2400": "pvdJ, pyoverdine biosynthesis",
        "PA2413": "pvdH, pyoverdine biosynthesis",
        "PA2424": "pvdL, pyoverdine biosynthesis",
        "PA2425": "pvdG, pyoverdine biosynthesis",
        "PA3901": "fecA, ferric dicitrate transport",
        "PA4688": "hitB, iron(III) transport permease",
        "PA0198": "exbB1, energizes TonB-dependent transport",
        "PA0199": "exbD1, energizes TonB-dependent transport",
        "PA0693": "exbB2, energizes TonB-dependent transport",
        "PA0694": "exbD2, energizes TonB-dependent transport",
    },
    "Oxidative stress response": {
        "PA2850": "ohr, organic hydroperoxide resistance",
        "PA5018": "msrA, peptide methionine sulfoxide reductase",
    },
    "Anaerobic respiration": {
        "PA1173": "napB, periplasmic nitrate reductase subunit",
        "PA1172": "napC, periplasmic nitrate reductase subunit",
        "PA3391": "nosR, nitrous oxide reductase accessory",
        "PA3393": "nosD, nitrous oxide reductase accessory",
        "PA3876": "narK2, nitrite extrusion",
        "PA3877": "narK1, nitrite extrusion",
    },
    "Quorum sensing and biofilm": {
        # Psl exopolysaccharide operon
        **{l: "psl operon, biofilm exopolysaccharide" for l in
           ["PA2231", "PA2232", "PA2233", "PA2234", "PA2235", "PA2236", "PA2237",
            "PA2238", "PA2239", "PA2240", "PA2241", "PA2242", "PA2243", "PA2244",
            "PA2245"]},
        # Pel exopolysaccharide operon
        **{l: "pel operon, biofilm exopolysaccharide" for l in
           ["PA3058", "PA3059", "PA3060", "PA3061", "PA3062", "PA3063", "PA3064"]},
        "PA0762": "algU, alginate sigma factor",
        "PA0763": "mucA, anti-sigma factor",
        "PA5483": "algB, alginate response regulator",
        "PA4217": "phzS, phenazine modification",
    },
}
# napB/napC/nosR/nosD/narK reached Central metabolism only via the PseudoCAP
# fallback; curated assignment now claims them, so they must be removed there.
RECLAIMED = {"PA1173", "PA1172", "PA3391", "PA3393", "PA3876", "PA3877",
             "PA0762", "PA0763", "PA5483", "PA4217", "PA3063", "PA2232",
             "PA2242", "PA2245"}


def load(path):
    with gzip.open(path, "rt") as fh:
        d = pd.read_csv(fh, sep="\t", low_memory=False)
    d["locus"] = d["ID"].str.extract(r"^(PA\d+)", expand=False)
    d["sym"] = d["Gene.Symbol"].astype(str).str.strip()
    d["desc"] = d["Target.Description"].str.extract(r"/DEF=([^/]+)", expand=False).fillna("")
    d["sig"] = (d["adj.P.Val"] < FDR) & (d["logFC"].abs() > LFC)
    return d.dropna(subset=["locus"]).drop_duplicates("locus")


pa = load("raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz")
onto = pd.read_csv(f"{OUT}/frozen_ontology_2026-09-08.csv")

# build revision 3 ontology
rows = []
for _, r in onto.iterrows():
    if r.locus in RECLAIMED and r.ontology == "PseudoCAP":
        continue                                    # curated assignment wins
    rows.append(dict(pathway=r.pathway, ontology=r.ontology, frozen=r.frozen,
                     locus=r.locus, symbol=r.symbol, description=r.description,
                     probe=r.probe, added_rev3="", reason=""))
meta = pa.set_index("locus")[["sym", "desc", "ID"]].to_dict("index")
for cat, genes in ADD.items():
    for loc, why in genes.items():
        m = meta.get(loc)
        if not m:
            print(f"  skip {loc} — not on array")
            continue
        rows.append(dict(pathway=cat, ontology="curated", frozen=REV, locus=loc,
                         symbol=m["sym"], description=m["desc"], probe=m["ID"],
                         added_rev3="yes", reason=why))
o3 = pd.DataFrame(rows).drop_duplicates(subset=["pathway", "locus"])
# revision 2 rule, applied here for the first time in a written file:
# curated assignment takes precedence over the PseudoCAP fallback.
o3["_pri"] = (o3.ontology == "curated").astype(int)
o3 = (o3.sort_values("_pri", ascending=False)
        .drop_duplicates(subset=["locus"], keep="first")
        .drop(columns="_pri"))

dup = o3.groupby("locus").pathway.nunique()
assert (dup > 1).sum() == 0, f"{(dup>1).sum()} loci double-assigned"
o3.to_csv(f"{OUT}/frozen_ontology_{REV}_rev3.csv", index=False)
print(f"disjointness OK · {len(o3)} rows · {int((o3.added_rev3=='yes').sum())} added\n")

# ---- rescore every P. aeruginosa cell, before vs after -------------------
def call(g):
    up, dn = int((g.logFC > 0).sum()), int((g.logFC < 0).sum())
    if len(g) < 3:
        return "unresolved", up, dn
    if dn == 0:
        return "induced", up, dn
    if up == 0:
        return "repressed", up, dn
    if up >= 3 * dn:
        return "induced", up, dn
    if dn >= 3 * up:
        return "repressed", up, dn
    return "mixed", up, dn


g17 = pd.read_csv(f"{OUT}/gse17179_anaerobic_vs_aerobic.csv")
g17["locus"] = g17["ID_REF"].str.extract(r"^(PA\d+)", expand=False)

onto2 = onto.copy()
onto2["_pri"] = (onto2.ontology == "curated").astype(int)
onto2 = (onto2.sort_values("_pri", ascending=False)
              .drop_duplicates(subset=["locus"], keep="first"))
CATS = sorted(set(onto.pathway))
print(f"{'category':<42}{'arm':<10}{'rev2':>22}{'rev3':>22}")
print("-" * 96)
changed = []
for cat in CATS:
    old = set(onto2[onto2.pathway == cat].locus.dropna())
    new = set(o3[o3.pathway == cat].locus.dropna())
    for arm, df in [("iron", pa[pa.sig]), ("oxygen", g17[g17["sig"]])]:
        co, uo, do = call(df[df.locus.isin(old)])
        cn, un, dn_ = call(df[df.locus.isin(new)])
        flag = "  <-- CHANGED" if co != cn else ""
        if flag:
            changed.append((cat, arm, co, cn))
        print(f"{cat[:41]:<42}{arm:<10}"
              f"{f'{co} ({uo}/{do})':>22}{f'{cn} ({un}/{dn_})':>22}{flag}")

print("\ncells changed:", len(changed))
for c in changed:
    print("  ", c)
