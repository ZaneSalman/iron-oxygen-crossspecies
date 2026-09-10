# S. flexneri ontology curation log

Frozen: 2026-09-08

Built from GeneID / GeneName / Annotation only. The fold-change and p-value columns were not loaded by the script that assigned membership.

## Set sizes (significant genes only)

|pathway|genes|
|---|---|
|Anaerobic respiration|15|
|Central carbon and amino acid metabolism|25|
|Iron uptake and storage|25|
|Oxidative stress response|7|
|Quorum sensing and biofilm|3|
|Secretion and virulence|17|
|(unassigned)|200|

## Notes and cross-species cautions

- arcA is EXCLUDED from Anaerobic respiration here and INCLUDED in the P. aeruginosa set. The two are unrelated genes: in Enterobacteriaceae arcA encodes the aerobic respiration control response regulator; in P. aeruginosa it encodes arginine deiminase. Scoring them as one category across species would be a false ortholog match.
- nirB/nirD excluded from Anaerobic respiration in both organisms (assimilatory nitrogen reduction), consistent with the Pseudomonas freeze.
- This table lists only the 292 significant genes, not the full transcriptome. Set sizes therefore count significant members only and enrichment testing is NOT possible for this arm — see step 2.
