import pandas as pd, gzip

CONTRASTS = {
    "2vs1  HHQ  vs LB":  "raw/GSE81364_genelist_P_aerug_paired_2vs1_txt.gz",
    "3vs1  PQS  vs LB":  "raw/GSE81364_genelist_P_aerug_paired_3vs1_txt.gz",
    "4vs1  HQNO vs LB":  "raw/GSE81364_genelist_P_aerug_paired_4vs1_txt.gz",
    "5vs1  IPTG vs LB":  "raw/GSE81364_genelist_P_aerug_paired_5vs1_txt.gz",
}

# Canonical iron-starvation / Fur-repressed loci in P. aeruginosa PAO1.
# If PQS chelates iron, these should go UP in 3vs1.
IRON = {
    "PA4468": "sodM (Mn-SOD, iron-starvation induced)",
    "PA4469": "hypothetical, sodM operon",
    "PA4470": "fumC1 (Fe-independent fumarase)",
    "PA4471": "fagA (iron-starvation locus)",
    "PA2426": "pvdS (iron starvation sigma factor)",
    "PA2386": "pvdA (pyoverdine synthesis)",
    "PA4231": "pchA (pyochelin synthesis)",
    "PA4221": "fptA (pyochelin receptor)",
    "PA2398": "fpvA (pyoverdine receptor)",
    "PA4880": "bacterioferritin-like",
}

def load(path):
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh, sep="\t", low_memory=False)
    df["locus"] = df["ID"].str.extract(r"^(PA\d+)", expand=False)
    return df

print("=" * 78)
print("CONTRAST SUMMARY  (adj.P.Val < 0.05, |logFC| > 1)")
print("=" * 78)
print(f"{'contrast':<20} {'probes':>7} {'sig':>7} {'up':>6} {'down':>6}")
frames = {}
for name, path in CONTRASTS.items():
    df = load(path)
    frames[name] = df
    sig = df[(df["adj.P.Val"] < 0.05) & (df["logFC"].abs() > 1)]
    print(f"{name:<20} {len(df):>7} {len(sig):>7} "
          f"{(sig.logFC > 0).sum():>6} {(sig.logFC < 0).sum():>6}")

print()
print("=" * 78)
print("POSITIVE CONTROL: iron-starvation regulon  (logFC, * = adj.P < 0.05)")
print("=" * 78)
hdr = f"{'locus':<9} {'gene':<38}" + "".join(f"{k.split()[1]:>9}" for k in CONTRASTS)
print(hdr)
print("-" * len(hdr))
for locus, desc in IRON.items():
    row = f"{locus:<9} {desc:<38}"
    for name in CONTRASTS:
        df = frames[name]
        hit = df[df["locus"] == locus]
        if hit.empty:
            row += f"{'--':>9}"
        else:
            fc = hit.iloc[0]["logFC"]
            star = "*" if hit.iloc[0]["adj.P.Val"] < 0.05 else " "
            row += f"{fc:>8.2f}{star}"
    print(row)
