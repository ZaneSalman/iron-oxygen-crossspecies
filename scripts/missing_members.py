"""
Missing-member audit. Every prior check asked whether the genes IN a set
belong. This asks the opposite: are there genes on the array / in the table
that meet a category definition but were never assigned?

Candidates are reported for human decision, not added automatically. Any
addition requires a revision 3 with disclosure, since this audit runs after
the results are known.
"""
import gzip
import re
import pandas as pd

OUT = "/mnt/user-data/outputs"

# ---------------------------------------------------------- P. aeruginosa --
with gzip.open("raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz", "rt") as fh:
    pa = pd.read_csv(fh, sep="\t", low_memory=False)
pa["locus"] = pa["ID"].str.extract(r"^(PA\d+)", expand=False)
pa["sym"] = pa["Gene.Symbol"].astype(str).str.strip()
pa["desc"] = pa["Target.Description"].str.extract(r"/DEF=([^/]+)", expand=False).fillna("")
pa["text"] = (pa["sym"] + " " + pa["desc"]).str.lower()
pa = pa.dropna(subset=["locus"]).drop_duplicates("locus")

onto = pd.read_csv(f"{OUT}/frozen_ontology_2026-09-08.csv")
assigned = set(onto.locus.dropna())

# definitional probes: what SHOULD be in each curated category
PROBE_PA = {
    "Iron uptake and storage":
        (r"^(exb|ton|feo|hit|fpv|fpt|pch|pvd|has|phu|opt|fec|fiu|cir|bfr|fur|hem[oO])",
         r"siderophore|pyoverdine|pyochelin|ferric|ferrous|iron[- ]?(uptake|transport|"
         r"starvation|receptor)|heme (uptake|receptor|oxygenase)|bacterioferritin|"
         r"tonb-dependent"),
    "Oxidative stress response":
        (r"^(sod|kat|ahp|tpx|trx|grx|gor|gsh|oxy|sox|msr|ohr|bcp|ccp|dps)",
         r"superoxide dismutase|catalase|alkyl hydroperoxide|peroxiredoxin|"
         r"thioredoxin|glutaredoxin|glutathione (reductase|peroxidase)|"
         r"methionine sulfoxide reductase|oxidative stress"),
    "Anaerobic respiration":
        (r"^(nar|nap|nir|nor|nos|dnr|anr|fnr|ccp|azu|nuo)",
         r"nitrate reductase|nitrite reductase|nitric[- ]oxide reductase|"
         r"nitrous[- ]oxide reductase|denitrif|anaerobic"),
    "Quorum sensing and biofilm":
        (r"^(las|rhl|pqs|mvf|qsc|rsa|phz|lec|alg|muc|pel|psl|bdl|cdr)",
         r"quorum|autoinducer|homoserine lactone|quinolone signal|phenazine|"
         r"alginate|biofilm|lectin|exopolysaccharide"),
}

print("=" * 78)
print("P. AERUGINOSA — genes meeting a category definition but NOT in the set")
print("=" * 78)
pa_hits = []
for cat, (namerx, descrx) in PROBE_PA.items():
    cand = pa[(pa.sym.str.lower().str.match(namerx, na=False) |
               pa.text.str.contains(descrx, regex=True, na=False)) &
              (~pa.locus.isin(assigned))]
    print(f"\n== {cat}  ({len(cand)} candidates)")
    for _, r in cand.head(24).iterrows():
        sym = r.sym if r.sym != "---" else ""
        print(f"   {r.locus:<9}{sym[:11]:<12}{r.desc[:52]}")
        pa_hits.append(dict(organism="P. aeruginosa", pathway=cat, locus=r.locus,
                            symbol=sym, description=r.desc))
    if len(cand) > 24:
        print(f"   ... and {len(cand)-24} more")

# ------------------------------------------------------------ S. flexneri --
sf = pd.read_excel("raw/tableS2.xlsx", sheet_name="Comparisons",
                   header=2, usecols=[0, 1, 4])
sf.columns = ["gene_id", "gene_name", "annotation"]
sf = sf.dropna(subset=["gene_id"])
sf["gene_name"] = sf.gene_name.astype(str).str.strip()
sf["text"] = (sf.gene_name + " " + sf.annotation.astype(str)).str.lower()
sf_onto = pd.read_csv(f"{OUT}/shigella_frozen_ontology_2026-09-08.csv")
sf_assigned = set(sf_onto.gene_id)

PROBE_SF = {
    "Iron uptake and storage":
        (r"^(ent|fep|fes|fhu|iuc|iut|feo|sit|fec|exb|tonb|ftn|bfr|fur|shu|chu|efe|fie)",
         r"siderophore|enterobactin|enterochelin|aerobactin|ferrichrome|ferric|"
         r"ferrous|iron (transport|uptake|storage)|ferritin|tonb"),
    "Oxidative stress response":
        (r"^(sod|kat|ahp|tpx|trx|grx|gor|oxy|sox|msr|osmc|bcp|dps|wrba|suf)",
         r"superoxide dismutase|catalase|hydroperoxide reductase|peroxiredoxin|"
         r"thioredoxin|glutaredoxin|methionine sulfoxide"),
    "Anaerobic respiration":
        (r"^(nap|nar|frd|nrf|dms|tor|hya|hyb|hyc|fdn|fdo|glpa|dcu|fnr)",
         r"nitrate reductase|nitrite reductase|fumarate reductase|"
         r"formate dehydrogenase-n|hydrogenase-[0-9]"),
}
print("\n" + "=" * 78)
print("S. FLEXNERI (iron arm) — unassigned genes meeting a category definition")
print("=" * 78)
for cat, (namerx, descrx) in PROBE_SF.items():
    cand = sf[(sf.gene_name.str.lower().str.match(namerx, na=False) |
               sf.text.str.contains(descrx, regex=True, na=False)) &
              (~sf.gene_id.isin(sf_assigned))]
    print(f"\n== {cat}  ({len(cand)} candidates)")
    for _, r in cand.head(20).iterrows():
        print(f"   {r.gene_id:<16}{r.gene_name[:11]:<12}{str(r.annotation)[:48]}")
        pa_hits.append(dict(organism="S. flexneri", pathway=cat, locus=r.gene_id,
                            symbol=r.gene_name, description=str(r.annotation)))

pd.DataFrame(pa_hits).to_csv(f"{OUT}/missing_member_candidates.csv", index=False)

# ------------------------------- reviewer's named genes, checked explicitly --
NAMED = ["exbB", "exbD", "hitB", "feoA", "feoB", "msrA", "msrB", "napB", "napC",
         "norD", "nosZ", "nosR", "nosD", "pelA", "pslA"]
print("\n" + "=" * 78)
print("REVIEWER'S NAMED GENES — present on array? assigned?")
print("=" * 78)
for g in NAMED:
    m = pa[pa.sym.str.lower() == g.lower()]
    if m.empty:
        print(f"   {g:<7} not on array")
    else:
        loc = m.iloc[0].locus
        cat = onto[onto.locus == loc].pathway.unique()
        print(f"   {g:<7} {loc:<9} " +
              (f"assigned -> {cat[0]}" if len(cat) else "NOT ASSIGNED"))
