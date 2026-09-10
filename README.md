# Iron and oxygen stress are not one response

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22698569.svg)](https://doi.org/10.5281/zenodo.22698569)

A prespecified cross-species reanalysis of published transcriptomes in
*Pseudomonas aeruginosa* and *Shigella flexneri*.

**Zane Salman** · College of Natural Sciences, The University of Texas at Austin
· zgs277@eid.utexas.edu

---

## The question

Bacteria inside a host are starved of iron and oxygen at once. The two shortages
are chemically coupled — ferric iron is insoluble and must be chased with
siderophores, while ferrous iron stays dissolved once oxygen is gone — and some
organisms wire that coupling into regulation (in *Shigella*, ArcA controls Fur).
The literature therefore often treats low iron and low oxygen as one shared
host-stress program.

**Do the two shortages actually move the same genes in the same direction, and
do distantly related pathogens resolve the coupling the same way?**

## The finding

**Iron limitation elicits a conserved response; oxygen limitation does not.**

| Category | *P.a.* low Fe | *P.a.* low O₂ | *S.f.* low Fe | *S.f.* low O₂ |
|---|---|---|---|---|
| **Iron uptake & storage** | **induced** | too few (n=1) | **induced** | **repressed** |
| Anaerobic respiration | repressed | induced | too few | induced |
| Oxidative stress | repressed | mixed | induced | repressed |
| Carbon / amino acid | repressed | mixed | mixed | mixed |
| Secretion & virulence | induced | repressed | induced | no data |
| Motility | too few | mixed | too few | too few |
| Quorum sensing / biofilm\* | induced | too few | induced | no data |

Under iron limitation both species induce acquisition and repress storage —
28 of 29 iron genes up in *P. aeruginosa*, 24 of 25 in *S. flexneri* — despite
non-homologous siderophore systems. Under oxygen limitation *S. flexneri*
reverses that program (20 of 22 down, ferritin up ~16-fold) while
*P. aeruginosa* registers a single gene.

The difference is in **response magnitude, not regulatory capability**: both
species carry oxygen-responsive sites at iron promoters, and *P. aeruginosa*
does mount an iron-starvation response anaerobically when iron is actually
withheld.

Row 2 is the internal control. Anaerobic respiration rises without oxygen and
falls without iron, as it must, since those enzymes are iron-dependent.

\* Not comparable across species — *S. flexneri* encodes no quorum-signal
synthase, so its cells reflect biofilm matrix genes only.

## Design

Four published contrasts fill a 2 × 2, so organism and perturbation are never
confounded. Most published cross-species comparisons fill only two cells.

| Accession | Organism | Contrast | Platform | n |
|---|---|---|---|---|
| [GSE81364](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE81364) | *P. aeruginosa* PAO1 (AQ-null) | 40 µM PQS vs untreated | Affymetrix Pae_G1a | 2 |
| [GSE17179](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE17179) | *P. aeruginosa* PAO1 | anaerobic vs aerobic | Affymetrix Pae_G1a | 2 |
| [PRJNA573757](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA573757) | *S. flexneri* 2457T | iron-free vs 40 µM FeCl₃ | Illumina, edgeR | 3 |
| [ERP003817](https://www.ebi.ac.uk/ena/browser/view/ERP003817) | *S. flexneri* M90T | anaerobic vs aerobic | Illumina, DESeq | 3 |

Both *P. aeruginosa* arms are on the same array, so gene sets transfer without
remapping.

## Method

- **No new experiments.** Public data only.
- **Seven functional categories**, defined and frozen **before any
  *S. flexneri* data were examined**. Three use PseudoCAP classes shipped with
  the array annotation; four are curated gene sets.
- **Blinding enforced in code** for the *S. flexneri* iron arm: the assignment
  script loads only identifier and annotation columns and never reads the
  fold-change column (`scripts/shigella_freeze.py`).
- **Thresholds:** adjusted p < 0.05, |log2FC| > 1. A direction is reported only
  where **three or more genes** support it.
- Microarrays re-normalized from raw CEL files with RMA; RNA-seq arms use the
  original authors' published differential expression tables.

## Provenance

Gene sets were revised three times. **No revision changed any direction call.**
Full detail in [`docs/revision_log.md`](docs/revision_log.md).

| Rev | Date | Trigger | Effect |
|---|---|---|---|
| 1 | 2026-09-08 | initial freeze | — |
| 2 | 2026-09-09 | independent external review | 3 keyword artifacts corrected, disjointness enforced; 3 cells moved *toward* "unresolved" |
| 3 | 2026-09-10 | completeness audit | 47 genes added that met a definition but were never assigned; **no cell changed** |

**Three keyword artifacts were found, all of one kind — a pattern matching text
that was not gene function:**

1. `alginate` matched the PseudoCAP class label *"Secreted Factors (toxins,
   enzymes, alginate)"*, sweeping 51 secreted factors and both siderophore
   operons into quorum sensing.
2. `iron` matched proteins that *contain* iron rather than acquire it —
   cytochrome maturation, respiratory Fe-S subunits.
3. `hydrogenase` matched inside `dehydrogenase`, pulling every dehydrogenase in
   both transcriptomes — Complex I, TCA cycle, glycolysis — into anaerobic
   respiration. Found only by independent review, after two prior audits.

A separate trap: **`arcA` names two unrelated genes** — the aerobic respiration
control regulator in Enterobacteriaceae, arginine deiminase in *P. aeruginosa*.
Mapping sets by gene name across species would have manufactured a false
convergence in the category central to this study.

## Limitations

- **PQS is not a clean iron perturbation.** It is simultaneously an iron
  chelator and the PqsR ligand. HHQ, also a PqsR ligand, produced zero
  significant genes at the same concentration — which argues against a purely
  quorum-driven explanation, but the confound stands.
- **No enrichment testing on either *S. flexneri* cell.** Both sources publish
  only genes reaching significance, so no non-significant background exists.
- **n = 2 per *P. aeruginosa* condition.** The GSE17179 contrast used a
  variance-shrinkage moderated *t*-test approximating limma, not limma itself.
- **The hypothesis was revised after data were seen**, so the *P. aeruginosa*
  findings are exploratory. The category freeze preceded all *S. flexneri*
  analysis, so the cross-species comparison remains prespecified.
- **One cell is unavailable, not negative.** Vergara-Irigaray Table S1 covers
  chromosomal genes only; their T3SS result is plasmid-encoded.
- **Motility is structurally empty** on the *S. flexneri* side — non-motile,
  degraded flagellar genes.

## Repository

```
data/    frozen gene sets, per-gene results, pathway scores, direction matrix
docs/    protocol, revision log, curation logs, reviewer brief
scripts/ analysis pipeline, in execution order (see below)
poster/  conference poster (48 × 36 in)
```

**Execution order**

| Script | Does |
|---|---|
| `check_contrasts.py` | GSE81364 triage and iron positive control |
| `build_registry.py` | contrast registry, first draft ontology |
| `freeze_ontology.py` | rev 1 freeze — curated sets by explicit locus list |
| `gse17179_analysis.py` | *P. aeruginosa* oxygen arm, moderated *t* |
| `shigella_freeze.py` | *S. flexneri* sets, **blind to effect size** |
| `shigella_score.py` | *S. flexneri* iron arm scoring |
| `vergara_analysis.py` | *S. flexneri* oxygen arm |
| `rebuild_rev2.py` | rev 2 — post-review rebuild |
| `missing_members.py` | completeness audit |
| `rev3.py` | rev 3 — additions, before/after comparison |
| `build_poster.js` | poster (pptxgenjs) |

**Source data are not redistributed here.** Retrieve them from the accessions
in the table above; supplementary tables come from the source publications.

## References

- Boulette ML & Payne SM. 2007. *J Bacteriol* 189:6957
- Trunk K et al. 2010. *Environ Microbiol* (GSE17179)
- Rampioni G et al. GSE81364, Gene Expression Omnibus
- Lozano Aguirre LF et al. 2020. *PeerJ* 8:e9553
- Vergara-Irigaray M et al. 2014. *BMC Genomics* 15:438

## Acknowledgments

Thanks to the authors of all four source studies for depositing their data
publicly, and to **Zain Baki**, whose independent audit of the gene sets
identified a third annotation error and three category corrections.
No external funding supported this work.

## License

Code: MIT. Data and documentation: CC BY 4.0.
