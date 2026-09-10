"""
STEP 2 of 2 — score the frozen S. flexneri sets against comparison alpha.

Sign convention is determined empirically, not assumed: the paper states fes
is the most strongly repressed gene by iron (21-fold). Whichever sign fes
carries in this sheet therefore corresponds to "higher under iron limitation".
"""
import numpy as np
import pandas as pd

OUT = "/mnt/user-data/outputs"

stats = pd.read_excel("raw/tableS2.xlsx", sheet_name="Comparisons",
                      header=2, usecols=[0, 1, 2, 3])
stats.columns = ["gene_id", "gene_name", "log2FC", "p_value"]
stats = stats.dropna(subset=["gene_id"])
stats["gene_name"] = stats["gene_name"].astype(str).str.strip()

onto = pd.read_csv(f"{OUT}/shigella_frozen_ontology_2026-09-08.csv")
df = onto.merge(stats[["gene_id", "log2FC", "p_value"]], on="gene_id", how="left")

# --- establish sign convention from fes ---
fes = stats[stats.gene_name.str.lower() == "fes"]
print("SIGN CHECK")
for _, r in fes.iterrows():
    print(f"  fes log2FC = {r.log2FC:+.2f}  (paper: most repressed by iron, ~21-fold)")
sign = 1 if fes.iloc[0]["log2FC"] > 0 else -1
print(f"  => positive log2FC means "
      f"{'HIGHER under iron limitation' if sign > 0 else 'HIGHER under iron repletion'}")
print(f"  reported as iron-limitation direction; multiplier = {sign:+d}\n")

df["logFC_ironlim"] = df["log2FC"] * sign

rows = []
for pathway, g in df.groupby("pathway"):
    up = int((g.logFC_ironlim > 0).sum())
    dn = int((g.logFC_ironlim < 0).sum())
    call = ("induced" if dn == 0 else "repressed" if up == 0 else
            "induced" if up >= 3 * dn else
            "repressed" if dn >= 3 * up else "mixed")
    rows.append(dict(pathway=pathway, sig_genes=len(g), up=up, down=dn,
                     median_logFC=round(g.logFC_ironlim.median(), 2),
                     max_abs_logFC=round(g.logFC_ironlim.abs().max(), 2),
                     direction=call))
res = pd.DataFrame(rows).sort_values("pathway")
res.to_csv(f"{OUT}/shigella_iron_pathway_scores.csv", index=False)
df.sort_values(["pathway", "logFC_ironlim"], ascending=[True, False]).to_csv(
    f"{OUT}/shigella_iron_gene_level.csv", index=False)

print("S. FLEXNERI — iron limitation vs iron replete (comparison alpha)")
print(res.to_string(index=False))

print("\nIron set, strongest movers (iron-limitation direction):")
iron = df[df.pathway == "Iron uptake and storage"].sort_values(
    "logFC_ironlim", ascending=False)
for _, r in pd.concat([iron.head(8), iron.tail(3)]).iterrows():
    print(f"  {r.gene_name:<10}{r.logFC_ironlim:>7.2f}   {str(r.annotation)[:48]}")
