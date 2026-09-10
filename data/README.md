# Data

Derived outputs only. **Source data are not redistributed** — retrieve them from
the accessions listed in the root README.

| File | Contents |
|---|---|
| `frozen_ontology_current_rev3.csv` | *P. aeruginosa* gene sets, revision 3. Columns: pathway, ontology (curated / PseudoCAP), frozen date, locus, symbol, description, probe, added_rev3, reason |
| `shigella_frozen_ontology.csv` | *S. flexneri* gene sets, built blind to effect size |
| `master_2x2_direction_matrix.csv` | The headline figure: 7 categories × 4 cells |
| `pathway_scores.csv` | Per-cell detail: n, up, down, median log2FC, direction |
| `contrast_registry.csv` | One row per contrast — strain, treatment, control, platform, replication, normalization, statistics |
| `gse17179_anaerobic_vs_aerobic.csv` | Per-gene results, *P. aeruginosa* oxygen arm |
| `gse17179_pathway_scores.csv` | Pathway scores for all three GSE17179 contrasts |
| `shigella_iron_gene_level.csv` | Per-gene results, *S. flexneri* iron arm |
| `shigella_oxygen_gene_level.csv` | Per-gene results, *S. flexneri* oxygen arm |
| `shigella_*_pathway_scores.csv` | Pathway scores per Shigella arm |
| `missing_member_candidates.csv` | Output of the revision 3 completeness audit |

## Sign conventions

`shigella_iron_gene_level.csv` reports **`logFC_ironlim`** — positive means
higher under iron limitation. The convention was established empirically from
*fes*, which the source paper identifies as the most strongly iron-repressed
gene (21-fold), not assumed.

All other files report the contrast named in the filename, treatment over
control.

## Direction calls

`induced` all significant members up, or up ≥ 3 × down
`repressed` all down, or down ≥ 3 × up
`mixed` neither threshold met
`unresolved` fewer than three significant members — no direction claimed
