# Prompts

Reusable prompts for continuing this project in a new session. The first is the
one to paste when picking the work back up; the rest are task-specific.

---

## 1. Continuation prompt (paste this to resume)

> I am continuing a completed computational reanalysis project. Do not restart
> it or re-derive its conclusions — read the state below and work from there.
>
> **Project.** A prespecified cross-species comparison of iron and oxygen stress
> responses in *Pseudomonas aeruginosa* and *Shigella flexneri*, using four
> published transcriptomes arranged as a 2 × 2 (two organisms × two
> perturbations) so that organism and perturbation are never confounded.
>
> **Result, already established.** Iron limitation elicits a conserved response
> in both species — acquisition induced, storage repressed, 28/29 genes up in
> *P. aeruginosa* and 24/25 in *S. flexneri*, despite non-homologous siderophore
> systems. Oxygen limitation does not: *S. flexneri* sharply represses iron
> acquisition and stockpiles iron, while *P. aeruginosa* shows one significant
> gene. The difference is in response magnitude, not regulatory capability —
> both species carry oxygen-responsive sites at iron promoters. Anaerobic
> respiration behaves as a positive control in both organisms.
>
> **Datasets.** GSE81364 (*P.a.* PQS), GSE17179 (*P.a.* anaerobic),
> PRJNA573757 (*S.f.* iron), ERP003817 (*S.f.* anaerobic). GSE3836 appears in
> the original inventory but was never verified and was not used.
>
> **Method constraints that must be preserved.** Seven functional categories,
> frozen 2026-09-08 before any *S. flexneri* data were examined. Thresholds:
> adjusted p < 0.05, |log2FC| > 1, minimum three genes for a direction call.
> Gene sets are at `data/frozen_ontology_current_rev3.csv` and
> `data/shigella_frozen_ontology.csv`. **Do not modify a gene set to change a
> result.** Any set change requires a new revision entry in
> `docs/revision_log.md` recording the trigger, the change, and a before/after
> comparison of every direction call.
>
> **Known traps in this project — check for these in any new work.** All three
> historical errors were text patterns matching something that was not gene
> function: `alginate` matched a database class label; `iron` matched proteins
> containing iron rather than acquiring it; `hydrogenase` matched inside
> `dehydrogenase`. Also: `arcA` names two unrelated genes in these organisms and
> must never be matched across species by name.
>
> **Open items.** Novelty search close to submission. Optionally, the
> *S. flexneri* virulence-plasmid expression table, which would fill the one
> "no data" cell (Vergara-Irigaray Table S1 is chromosomal only).
>
> Tell me what you need before starting.

---

## 2. Dataset triage

> For accession [X], open the accession record and report: sample count per
> condition, whether raw files are attached, and the gene identifier scheme.
> Do not download or analyze anything until those three are settled. If the
> dataset cannot support differential expression at the stated replication, say
> so and stop.

## 3. Freezing a gene set

> Build gene sets for these categories: [list]. Assign membership from annotated
> gene function only. Do not consult fold-change or p-value columns while
> deciding — if the data are in the same file, load only the identifier and
> annotation columns so the blinding is enforced rather than promised. Use
> explicit locus lists, not keyword patterns over annotation text. Record every
> exclusion with its reason in a curation log. Assert set disjointness in code.

## 4. Auditing a gene set

> Audit these gene sets two ways. First, does every gene present meet its
> category definition? Second — and this is the one usually skipped — is there
> any gene in the annotation that meets a definition but was never assigned?
> Report candidates for decision; do not add them automatically. Then recompute
> every direction call before and after, and report whether any changed.

## 5. Requesting external review

> Draft a review request for an outside reader with bacterial physiology
> background. Scope it to gene set membership only — not the hypothesis, not the
> statistics. Disclose known past errors so they know where to look hardest.
> Give a response format. Keep the ask under 90 minutes. Separate genuine
> mistakes from judgment calls you want ratified or overturned.

## 6. Reporting a result honestly

> Report this analysis with the confound stated before the conclusion, not after
> it. Where a cell has fewer than three supporting genes, say "too few" rather
> than naming a direction. Where a source table cannot cover a cell, say "no
> data" rather than treating absence as a negative result. If a finding is
> already known in single organisms, concede that explicitly and state what the
> design adds instead.
