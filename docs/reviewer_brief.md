# Independent review request — gene set membership

**Project:** Cross-species comparison of iron and oxygen stress responses in
*Pseudomonas aeruginosa* and *Shigella flexneri*
**Requested by:** Zane Salman, UT Austin
**Frozen:** 8 September 2026
**Estimated time:** 60–90 minutes

---

## What I'm asking you to do

Read two gene set files and tell me whether each gene belongs in the category
it was assigned to. That's the whole task.

I am **not** asking you to evaluate the hypothesis, the statistics, the
datasets, or the conclusions. Only membership.

**The one rule:** judge each gene on its annotated function alone. The files
contain a fold-change column for context — please ignore it while deciding.
If a gene's membership looks wrong, it should look wrong regardless of which
direction it moved.

---

## Why this needs an outside reader

The gene sets were drafted with AI assistance using keyword rules over gene
names and annotation text. That method already produced two errors that were
caught and corrected, both in the iron category:

1. **Label matching instead of function matching.** A rule containing the word
   "alginate" matched the PseudoCAP *class label* "Secreted Factors (toxins,
   enzymes, alginate)" rather than any gene's function. This pulled 51
   secreted factors and both siderophore operons into the quorum-sensing
   category, which would have counted the iron signal twice.

2. **Iron-containing vs. iron-acquiring.** A rule containing "iron" and "heme"
   matched cytochrome *c* maturation genes (*ccmABCH*), respiratory
   iron-sulfur subunits (*frdB*, *sdhB*, *hycB*, *fdoH*) and *adhE* —
   proteins that contain iron but do not acquire or store it.

Two errors of the same shape, in the same category, suggests more may remain.
A cross-check against PseudoCAP functional classes was run and found no
further artifacts of this type, but PseudoCAP classifies by molecular function
(regulators are "Transcriptional regulators" regardless of what they regulate)
while these categories are physiological, so it cannot validate the
assignments. Hence a human reader.

---

## The seven categories, as defined

| Category | Intended scope |
|---|---|
| Iron uptake and storage | Siderophore synthesis and transport, heme acquisition, ferrous/ferric transporters, TonB system, iron storage proteins. **Not** proteins that merely contain iron. |
| Oxidative stress response | Enzymes defending against reactive oxygen species: superoxide dismutases, catalases, peroxidases, peroxiredoxins, thioredoxin/glutathione redox systems. **Not** xenobiotic detoxification (glutathione S-transferases) or methylglyoxal detox (glyoxalases). |
| Anaerobic respiration | Terminal reductases and electron transport for respiration without oxygen: nitrate/nitrite/nitric oxide/nitrous oxide reductases, fumarate reductase, hydrogenases, formate dehydrogenases. **Not** assimilatory nitrogen reduction (*nirB*, *nirD*). |
| Quorum sensing and biofilm | Signal synthesis, reception and regulation; biofilm matrix (alginate, curli, lectins). Phenazines were **included** as canonical QS output — flag if you disagree. |
| Motility | Flagellar, chemotaxis, fimbrial and pilus genes. |
| Secretion and virulence | Secretion systems and secreted effectors, toxins, proteases. |
| Central carbon and amino acid metabolism | Core metabolic and biosynthetic enzymes. |

---

## Three decisions I made that you should explicitly ratify or overturn

These are judgment calls, not errors. I want them checked because a reviewer
at a poster session may ask about any of them.

1. **Regulators are inside the sets they control.** *fur* sits in Iron,
   *anr* and *dnr* in Anaerobic respiration, *oxyR* in Oxidative stress.
   This mixes regulator with regulon. Should they be excluded?

2. **`arcA` is treated as two unrelated genes.** In *S. flexneri* it encodes
   the aerobic respiration control regulator and is **excluded** from
   Anaerobic respiration. In *P. aeruginosa* it encodes arginine deiminase
   and is **included** (as fermentative anaerobic energy generation).
   Is that the right call in each organism?

3. **`suf` is in the Shigella iron set but has no Pseudomonas counterpart.**
   The original authors group it with iron acquisition; it is arguably
   iron-sulfur cluster biogenesis. Keep or drop?

Also worth a sanity check: **Motility is empty on the Shigella side.** I
believe this is correct — *S. flexneri* is non-motile with degraded flagellar
genes — but please confirm, because an empty category means that row cannot
be compared across species at all.

---

## What to send back

For each gene you'd change, one line:

```
<locus/gene>  <current category>  ->  <REMOVE | correct category>   reason
```

Plus a yes/no on each of the three decisions above, and anything you think is
missing from a set that should be in it.

If a whole category looks unsound rather than a few genes, say that instead —
it's more useful than a long list.

---

## Files in this packet

| File | What it is |
|---|---|
| `frozen_ontology_2026-09-08.csv` | *P. aeruginosa* sets. 138 curated genes across 4 categories, plus 3 categories using PseudoCAP classes shipped with the array annotation (those need no review). Columns: pathway, ontology, locus, symbol, description, probe. |
| `ontology_curation_log.md` | Every exclusion from the *P. aeruginosa* draft, with the reason for each. Read this before the CSV — it explains what was already removed and why. |
| `shigella_frozen_ontology_2026-09-08.csv` | *S. flexneri* sets from the iron-limitation dataset. Columns: pathway, gene_id, gene_name, annotation. |
| `shigella_ontology_curation_log.md` | Set sizes, exclusions, and cross-species cautions for the *S. flexneri* sets. |
| `shigella_oxygen_gene_level.csv` | *S. flexneri* sets from the anaerobic dataset, with COG categories from the source publication as an additional annotation reference. |
| `master_2x2_direction_matrix.csv` | Context only — the result these sets produce. Not part of the review. |

**Priority if time is short:** Iron uptake and storage in both organisms.
That is the category carrying the finding, and it is where both prior errors
occurred.

---

## Provenance note

These sets were frozen before any *S. flexneri* data were analyzed, and
membership for the Shigella iron arm was assigned by a script that loaded only
identifier and annotation columns — the fold-change column was never read
during assignment. The purpose of this review is to confirm that the frozen
sets are biologically defensible, not to revise them in light of results. If
changes are needed, they will be made and the freeze re-dated, with the
revision disclosed.
