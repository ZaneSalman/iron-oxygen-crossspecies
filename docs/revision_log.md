# Revision 2 — changes made in response to independent review

**Original freeze:** 2026-09-08
**Revised:** 2026-09-09, after external review of gene set membership
**Reason for revision:** review identified a third keyword artifact, one
unpropagated correction, and a structural double-counting fault.

Disclosure: this revision was made after the reviewer had seen direction calls
computed from the original sets. The reviewer wrote all membership decisions
before opening any fold-change column and states so. Set membership was not
adjusted to produce any particular result — the two cells that changed
direction both moved *toward* "unresolved," i.e. away from a claim.

---

## Root causes

**1. Missing word boundary (new).** The anaerobic respiration pattern listed
`hydrogenase` as an alternative. `hydrogenase` is a substring of
`dehydrogenase`, so every dehydrogenase in both transcriptomes matched:
NADH dehydrogenase (Complex I), succinate dehydrogenase, pyruvate
dehydrogenase, erythrose-4-phosphate dehydrogenase, and every ORF annotated
only "putative dehydrogenase."

This is the third artifact of one family, after the alginate class-label match
and the iron-containing/iron-acquiring conflation. All three shared a cause:
a pattern matched text that was not gene function. **Anaerobic respiration is
now built from an explicit gene-family list, not from annotation text.**

**2. Correction not propagated.** `adhE` was removed from the *P. aeruginosa*
iron set in revision 1 and left in the *S. flexneri* iron set. Its annotation
reads "iron-dependent alcohol dehydrogenase" — it contains iron, does not
acquire or store it.

**3. Sets were not disjoint.** 44 *P. aeruginosa* loci sat in two categories,
because curated and PseudoCAP sets were written in independent passes. All six
phenazine genes voted in both Quorum sensing and Secretion. Curated assignment
now takes precedence and disjointness is asserted in code.

---

## Decisions resolved

| # | Question | Resolution |
|---|---|---|
| 1 | Regulators inside their own regulons | Kept, but now carry a `regulator` flag so the matrix can be recomputed without them. The reviewer's point stands that a regulator often moves opposite its regulon. |
| 2 | `arcA` across species | Category kept **strictly respiratory**. Fermentation excluded in both organisms: *P. aeruginosa* `arcA` (arginine deiminase) removed; *S. flexneri* `pflA`, `pflB`, `adhE` removed. The two organisms are now scored by one rule. |
| 3 | `suf` in Iron | Moved to Oxidative stress. SUF assembles Fe-S clusters; it neither acquires nor stores iron, which is the definitional exclusion. Reviewer's correction noted: `suf` was in the *anaerobic* arm, not the iron-limitation arm as the brief stated. |
| — | `dps` | Assigned to Iron, per the category definition's explicit inclusion of iron storage proteins. |
| — | `oprE` | Removed from Anaerobic respiration — a porin, included by regulation rather than function. |

---

## Gene-level changes applied

**Removed entirely:** `adhE`, `yihU`, `osmY`, `nrdH`, `mrcA`, `ppiC`, `slpA`,
`fdhF`, `dmsA`, `narQ`, `flhA`, `fliY`, `cydA`, `appC`, `yhdH`, `yiaK`,
`ykgE`, `lrhA`, `nrdD`, `nrdG`, `pflA`, `pflB`, `ymgG`, `shiF`,
*P. aeruginosa* `oprE` and `arcA`.

**Reassigned to Central metabolism:** all eleven `nuo` subunits, `sdhABCD`,
`glpD`, `aceE`, `aceF`, `pdhR`, `epd`, `tyrA`, `gapA`, `gnd`, `gcd`, `icdA`,
`aldA`, `betA`, `betB`, `udhA`.

**Reassigned:** `wrbA` to Oxidative stress; `suf` operon to Oxidative stress.

**Deduplicated:** `SF5M90T_602` appeared twice (as `appC` and `cydA`) with
different fold changes; collapsed to one record.

**Retained but disclosed (`KEEP*`):** 15 uncharacterised TonB-dependent
receptors, `pvdQ`, `sitABCD`, `osmC`. See sensitivity below.

---

## Effect on the result

| Cell | Revision 1 | Revision 2 | Why |
|---|---|---|---|
| *P. aeruginosa* / oxygen / Iron | induced | **unresolved** | n = 1; a direction call was never supportable |
| *S. flexneri* / iron / Anaerobic respiration | repressed | **unresolved** | collapsed to `napD` alone once Complex I was removed |
| *S. flexneri* / oxygen / Motility | induced | **unresolved** | collapsed to `fliQ` alone |
| *S. flexneri* / oxygen / Anaerobic respiration | induced (n=82, median +3.28) | **induced** (n=47, median +4.20) | cleaner set, stronger signal |

**A minimum of three genes is now required for a direction call.** Cells below
that threshold report "unresolved" rather than a direction.

**The iron row is unchanged.** All four cells hold their revision-1 direction.

**Sensitivity — uncharacterised TonB-dependent receptors.** TonB-dependence is
a transport architecture, not an iron-specific one. Recomputing the
*P. aeruginosa* iron cell without all 15 uncharacterised TBDRs: n = 21 rather
than 22, median log2FC 4.98 rather than 4.92, still induced. The finding does
not rest on them.

---

## Outstanding, not fixed here

- **Quorum sensing is not comparable across species.** The *S. flexneri* side
  contains zero quorum sensing genes — no AHL synthase exists in this organism
  and `luxS` does not appear in either dataset. The row should be renamed
  "Biofilm matrix" for *S. flexneri*, or the QS comparison restricted to
  *P. aeruginosa*.
- **Secretion, *S. flexneri* / oxygen, is now empty.** Vergara-Irigaray Table S1
  lists chromosomal genes only; the T3SS repression they report is on the
  virulence plasmid, in a table not obtained. That cell is unavailable rather
  than negative.
- **The PQS arm perturbs iron and quorum sensing jointly.** PQS is both an iron
  chelator and the PqsR ligand, so *P. aeruginosa* / iron / Quorum sensing may
  be partly circular. Counter-evidence worth stating: HHQ, also a PqsR ligand,
  produced zero significant genes at the same concentration. Disclose the
  confound rather than argue it away.
- **Curation log vs. frozen file:** the revision-1 log claimed `pvcABCD` were
  retained in Iron; they are in Secretion. Corrected here.
- **Missing members not yet checked:** `exbB`/`exbD`, `hitB`, `feoA`,
  `msrA`/`msrB`, `napBC`, `norD`, `nos` operon, `pel` and `psl` operons.

---

# Revision 3 — completeness pass (2026-09-10)

**What this asked.** Revisions 1 and 2 both asked whether the genes *in* each
set belonged. This one asks the opposite: are there genes on the array that
meet a category definition but were never assigned? That is the one error class
none of the earlier audits could have caught.

**Disclosure.** This audit ran after the results were known. Every direction
call was recomputed before and after. **No cell changed.** Genes were added on
category definition alone; none was added or withheld on the basis of which way
it moved.

## Found and added — *P. aeruginosa*, 47 genes

| Category | Added | Why they qualify |
|---|---|---|
| Iron uptake and storage | 13 | Seven *pvd* pyoverdine biosynthesis genes; *fecA* (ferric dicitrate transport); *hitB* (iron III permease); both *exbB*/*exbD* pairs, which energize TonB-dependent transport |
| Oxidative stress response | 2 | *ohr* (organic hydroperoxide resistance), *msrA* (methionine sulfoxide reductase) |
| Anaerobic respiration | 6 | *napB*, *napC* (periplasmic nitrate reductase subunits); *nosR*, *nosD* (nitrous oxide reductase accessories); *narK1*, *narK2* (nitrite extrusion) |
| Quorum sensing and biofilm | 26 | The complete *psl* and *pel* exopolysaccharide operons, plus *algU*, *mucA*, *algB*, *phzS* |

*S. flexneri* returned **zero** candidates across all three testable categories.

## The two defects behind these gaps

**Operon partners were missed.** Curated lists named *napA*/*napD*/*napE* but
not *napB*/*napC*; *nosZ* but not *nosR*/*nosD*. The unnamed partners fell
through to the PseudoCAP fallback and were filed under Energy metabolism, hence
Central carbon. Curated assignment now claims them.

**One polysaccharide stood for three.** The biofilm category contained the
alginate operon but neither *psl* nor *pel* — the other two major
*P. aeruginosa* matrix exopolysaccharides. "Quorum sensing and biofilm" was in
practice "quorum sensing plus alginate."

## Effect

| Cell | rev2 | rev3 |
|---|---|---|
| Iron uptake and storage / iron | induced, 21 up / 1 down | induced, **28 up** / 1 down |
| Anaerobic respiration / iron | repressed, 0 / 8 | repressed, 0 / **12** |
| Central carbon / iron | repressed, 10 / 48 | repressed, 10 / **44** |
| All other cells | — | unchanged |

Three cells gained or lost members; **none changed direction**. The iron result
is now supported by 29 significant genes rather than 22.

**Also fixed here:** the revision-2 disjointness rule (curated assignment beats
the PseudoCAP fallback) had been enforced in code but never written to an
ontology file. `frozen_ontology_2026-09-10_rev3.csv` is the first published set
file in which it holds.

## Still outstanding

- Missing-member auditing for *S. flexneri* could only test three categories,
  since both source tables list significant genes only.
- The *S. flexneri* secretion cell remains unavailable, not negative
  (Vergara-Irigaray Table S1 is chromosomal; their T3SS result is plasmid).
