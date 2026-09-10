"""
GSE17179 (Pae_G1a, RMA) — PAO1 anaerobic vs aerobic, scored against the
ontology frozen 2026-09-08.

n=2 per group. A plain two-sample t-test is unusable at that replication
(1 d.f.), so a moderated t is used: the gene-wise variance is shrunk toward
the median gene-wise variance across all probe sets, which is the shrinkage
idea limma implements. This is an approximation of limma, not limma, and is
recorded as such in the registry. Thresholds are the frozen ones.
"""
import gzip
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import fisher_exact

OUT = "/mnt/user-data/outputs"
FDR, LFC = 0.05, 1.0

AERO = ["GSM429472", "GSM429475"]
ANAERO = ["GSM429476", "GSM429477"]
ANR = ["GSM429478", "GSM429479"]
DNR = ["GSM429480", "GSM429481"]


def load_matrix(path):
    rows, inside = [], False
    with gzip.open(path, "rt") as fh:
        for l in fh:
            if l.startswith("!series_matrix_table_begin"):
                inside = True
                continue
            if l.startswith("!series_matrix_table_end"):
                break
            if inside:
                rows.append(l.rstrip("\n").split("\t"))
    df = pd.DataFrame(rows[1:], columns=[c.strip('"') for c in rows[0]])
    df["ID_REF"] = df["ID_REF"].str.strip('"')
    df = df.set_index("ID_REF").apply(pd.to_numeric, errors="coerce")
    return df[~df.index.str.startswith("AFFX")]          # drop spike-ins


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.clip(q, 0, 1)


def contrast(df, treat, ref):
    """Moderated t with variance shrunk toward the global median."""
    a, b = df[treat].values, df[ref].values
    lfc = a.mean(1) - b.mean(1)
    v = (a.var(1, ddof=1) + b.var(1, ddof=1)) / 2          # pooled within-group
    v0 = np.median(v)                                      # prior variance
    d0, d = 4.0, 1.0                                       # prior / residual d.f.
    v_post = (d0 * v0 + d * v) / (d0 + d)
    se = np.sqrt(v_post * (1 / len(treat) + 1 / len(ref)))
    t = lfc / se
    p = 2 * stats.t.sf(np.abs(t), df=d0 + d)
    return pd.DataFrame({"logFC": lfc, "t": t, "P.Value": p,
                         "adj.P.Val": bh(p)}, index=df.index)


mat = load_matrix("raw/GSE17179_series_matrix_txt.gz")
onto = pd.read_csv(f"{OUT}/frozen_ontology_2026-09-08.csv")

CONTRASTS = {
    "anaerobic vs aerobic (PAO1)": (ANAERO, AERO),
    "anr mutant vs PAO1 (anaerobic)": (ANR, ANAERO),
    "dnr mutant vs PAO1 (anaerobic)": (DNR, ANAERO),
}

res = {}
print(f"Thresholds: adj.P < {FDR}, |logFC| > {LFC}   (probe sets: {len(mat)})\n")
print(f"{'contrast':<34}{'sig':>6}{'up':>6}{'down':>6}")
for name, (tr, rf) in CONTRASTS.items():
    r = contrast(mat, tr, rf)
    r["locus"] = pd.Series(r.index, index=r.index).str.extract(
        r"^(PA\d+)", expand=False)
    r["sig"] = (r["adj.P.Val"] < FDR) & (r["logFC"].abs() > LFC)
    res[name] = r
    s = r[r.sig]
    print(f"{name:<34}{len(s):>6}{int((s.logFC>0).sum()):>6}"
          f"{int((s.logFC<0).sum()):>6}")

# ---- positive control: denitrification should be induced anaerobically ----
CTRL = {"PA0519": "nirS", "PA0524": "norB", "PA0523": "norC",
        "PA3392": "nosZ", "PA3875": "narG", "PA5171": "arcA (ADI)",
        "PA1544": "anr", "PA0527": "dnr"}
main = res["anaerobic vs aerobic (PAO1)"]
print("\nPOSITIVE CONTROL — anaerobic vs aerobic (* = adj.P < 0.05)")
for l, nm in CTRL.items():
    h = main[main.locus == l]
    if len(h):
        r = h.iloc[0]
        print(f"  {l:<8}{nm:<12}{r.logFC:>7.2f}"
              f"{'*' if r['adj.P.Val'] < FDR else ' '}")

# ---- score against frozen ontology ----
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
for pathway, g in onto.groupby("pathway"):
    loci = set(g["locus"].dropna())
    for name, r in res.items():
        out.append(dict(pathway=pathway, contrast=name,
                        **score(r, r["locus"].isin(loci))))
long = pd.DataFrame(out)
long.to_csv(f"{OUT}/gse17179_pathway_scores.csv", index=False)
res["anaerobic vs aerobic (PAO1)"].to_csv(f"{OUT}/gse17179_anaerobic_vs_aerobic.csv")

print("\nPATHWAY SCORES — anaerobic vs aerobic (PAO1)")
print(long[long.contrast == "anaerobic vs aerobic (PAO1)"][
    ["pathway", "genes_in_set", "sig", "up", "down",
     "median_logFC", "enrich_p", "direction"]].to_string(index=False))
