const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.defineLayout({ name: "POSTER", width: 48, height: 36 });
pres.layout = "POSTER";

const ORANGE = "BF5700", INK = "3B3B3B", MUTE = "7E848A", WHITE = "FFFFFF";
const UP = "2C5F2D", DOWN = "9E2A2B", NEU = "9AA0A6", PALE = "E6E6E6",
      RUST = "A34500", BLUE = "2E5E8C", TINT = "F7F0E9";

const s = pres.addSlide();
s.background = { color: WHITE };
const B = { fontFace: "Calibri", color: INK, isTextBox: true, fontSize: 18,
            lineSpacing: 26, margin: 0, valign: "top" };

/* --------------------------------------------------------------- header */
s.addShape(pres.ShapeType.rect, { x: 1.0, y: 0.9, w: 46, h: 4.5, fill: { color: ORANGE } });
s.addText("Do iron and oxygen stress trigger the same response in bacteria?",
  { ...B, x: 2.1, y: 1.35, w: 33, h: 1.4, bold: true, color: WHITE, fontSize: 44 });
s.addText("A side-by-side reanalysis of two published pathogens",
  { ...B, x: 2.1, y: 2.8, w: 33, h: 1.0, bold: true, color: WHITE, fontSize: 34 });
s.addText("Zane Salman · College of Natural Sciences · zgs277@eid.utexas.edu",
  { ...B, x: 2.1, y: 3.95, w: 33, h: 0.8, color: "F7DCC8", fontSize: 21 });
s.addImage({ path: "/home/claude/ut_wordmark_white.png",
  x: 36.6, y: 1.75, w: 9.4, h: 9.4 / 3.5 });
s.addText("College of Natural Sciences", { ...B, x: 36.6, y: 1.75 + 9.4 / 3.5 + 0.3,
  w: 9.4, h: 0.55, color: "F7DCC8", fontSize: 18, align: "center" });

/* ------------------------------------------------------------- geometry */
const COLW = 14.4, GAP = 1.1;
const C1 = 1.6, C2 = C1 + COLW + GAP, C3 = C2 + COLW + GAP;
const TOP = 6.2;

function bar(t, x, y) {
  s.addShape(pres.ShapeType.rect, { x, y, w: COLW * 0.78, h: 0.95, fill: { color: ORANGE } });
  s.addText(t, { ...B, x, y: y + 0.16, w: COLW * 0.78, h: 0.6, bold: true, color: WHITE,
    fontSize: 24, align: "center" });
  return y + 1.2;
}
function cap(n, t, x, y) {
  s.addText([{ text: `Figure ${n}. `, options: { bold: true } }, { text: t }],
    { ...B, x, y, w: COLW, h: 0.95, fontSize: 15, color: MUTE, lineSpacing: 20 });
  return y + 1.15;
}
function bul(items, x, y, fs = 17) {
  const h = items.reduce((a, t) => a + Math.ceil(t.length / 78) * (fs + 8) / 72 + 0.24, 0.15);
  s.addText(items.map((t, i) => ({ text: t,
    options: { bullet: true, breakLine: i < items.length - 1 } })),
    { ...B, x, y, w: COLW, h, fontSize: fs, lineSpacing: fs + 8, paraSpaceAfter: 8 });
  return y + h + 0.3;
}
function para(t, x, y, fs = 18) {
  const h = Math.ceil(t.length / 74) * (fs + 8) / 72 + t.split("\n").length * 0.14 + 0.15;
  s.addText(t, { ...B, x, y, w: COLW, h, fontSize: fs, lineSpacing: fs + 8 });
  return y + h + 0.3;
}

/* ======================================================= COLUMN 1 ====== */
let y = TOP;
y = bar("Background", C1, y);
y = para("Inside a human host, bacteria are starved of two things at once. Iron is withheld " +
  "on purpose — a defence called nutritional immunity — while oxygen runs low in abscesses, " +
  "mucus, biofilms and the gut lumen. Both shortages force a major metabolic rewiring, and " +
  "both are tied to how virulent the organism becomes.\n\n" +
  "The two are chemically linked (Figure 1), and some bacteria wire that link into their " +
  "regulation: in Shigella, the oxygen sensor ArcA controls Fur, the master iron regulator. " +
  "Because of this, the literature often treats low iron and low oxygen as one shared " +
  "host-stress program. Whether they actually move the same genes the same way has never " +
  "been tested directly.", C1, y);

/* ---- FIGURE 1 : iron chemistry depends on oxygen ---- */
let fy = y;
const PW = (COLW - 0.7) / 2;
[["WITH oxygen", RUST, "Fe³⁺", "insoluble rust", "must be hunted with\nsecreted siderophores"],
 ["WITHOUT oxygen", BLUE, "Fe²⁺", "stays dissolved", "imported directly,\nno hunting needed"]
].forEach(([hd, col, ion, state, note], i) => {
  const x = C1 + i * (PW + 0.7);
  s.addShape(pres.ShapeType.rect, { x, y: fy, w: PW, h: 6.0, fill: { color: "F5F5F5" } });
  s.addShape(pres.ShapeType.rect, { x, y: fy, w: PW, h: 0.72, fill: { color: col } });
  s.addText(hd, { ...B, x, y: fy + 0.14, w: PW, h: 0.5, bold: true, color: WHITE,
    fontSize: 17, align: "center" });
  s.addShape(pres.ShapeType.ellipse, { x: x + PW / 2 - 1.25, y: fy + 1.25, w: 2.5, h: 2.5,
    fill: { color: col } });
  s.addText(ion, { ...B, x: x + PW / 2 - 1.25, y: fy + 2.15, w: 2.5, h: 0.8, bold: true,
    color: WHITE, fontSize: 32, align: "center" });
  s.addText(state, { ...B, x, y: fy + 4.0, w: PW, h: 0.55, bold: true, fontSize: 19,
    align: "center", color: col });
  s.addText(note, { ...B, x: x + 0.3, y: fy + 4.6, w: PW - 0.6, h: 1.2, fontSize: 17,
    align: "center", color: MUTE, lineSpacing: 19 });
});
s.addShape(pres.ShapeType.rightArrow, { x: C1 + PW + 0.02, y: fy + 2.25, w: 0.66, h: 0.55,
  fill: { color: INK } });
y = fy + 6.25;
y = cap(1, "Removing oxygen makes iron easier to obtain, not harder. Any shared response " +
  "between the two shortages should reflect this.", C1, y);

y = bar("Methods", C1, y);
y = bul([
  "No new experiments. Four published datasets were retrieved from GEO, ENA and journal supplements and re-analyzed under one common procedure.",
  "Two organisms from different bacterial families: P. aeruginosa, an environmental opportunist causing lung and wound infection, and S. flexneri, an obligate human gut pathogen.",
  "Microarrays were re-normalized from raw intensity files with RMA; RNA-seq arms use the original authors' published differential expression tables.",
  "Genes were sorted into seven functional categories. Definitions and cutoffs were written down and locked before any Shigella data were examined.",
  "For the Shigella iron arm the blinding was enforced in code: the assignment script loaded only identifier and annotation columns, never the fold-change column.",
  "Cutoffs: adjusted p < 0.05 and at least two-fold change. A direction is reported only when three or more genes support it.",
  "Gene sets were externally reviewed and revised three times, including a completeness audit that added 47 genes. No revision changed any direction call; all are published in a revision log.",
], C1, y, 16);

/* ---- FIGURE 2 : the 2x2 design ---- */
fy = y;
const RL = 4.6, CWD = (COLW - RL) / 2, RHD = 2.75;
s.addText("low iron", { ...B, x: C1 + RL, y: fy, w: CWD, h: 0.5, bold: true, fontSize: 17,
  align: "center", color: MUTE });
s.addText("low oxygen", { ...B, x: C1 + RL + CWD, y: fy, w: CWD, h: 0.5, bold: true,
  fontSize: 17, align: "center", color: MUTE });
[["P. aeruginosa", [["GSE81364", "40 µM PQS vs untreated\nAffymetrix array · n = 2"],
                    ["GSE17179", "anaerobic vs aerobic\nsame array · n = 2"]]],
 ["S. flexneri", [["PRJNA573757", "iron-free vs 40 µM FeCl\u2083\nRNA-seq, edgeR · n = 3"],
                  ["ERP003817", "anaerobic vs aerobic\nRNA-seq, DESeq · n = 3"]]]
].forEach(([org, accs], ri) => {
  const yy = fy + 0.6 + ri * RHD;
  s.addText(org, { ...B, x: C1, y: yy + 1.05, w: RL - 0.3, h: 0.6, bold: true, italic: true,
    fontSize: 19 });
  accs.forEach(([a, d], ci) => {
    const x = C1 + RL + ci * CWD;
    s.addShape(pres.ShapeType.rect, { x: x + 0.08, y: yy, w: CWD - 0.16, h: RHD - 0.2,
      fill: { color: TINT } });
    s.addText(a, { ...B, x: x + 0.08, y: yy + 0.42, w: CWD - 0.16, h: 0.55, bold: true,
      color: ORANGE, fontSize: 18, align: "center" });
    s.addText(d, { ...B, x: x + 0.2, y: yy + 1.05, w: CWD - 0.4, h: 1.3, fontSize: 15,
      align: "center", color: MUTE, lineSpacing: 19 });
  });
});
y = fy + 0.6 + 2 * RHD + 0.3;
y = cap(2, "All four cells are filled, so organism and perturbation are never confounded. " +
  "Most published comparisons fill only two.", C1, y);

/* ======================================================= COLUMN 2 ====== */
y = TOP;
y = bar("Results", C2, y);
y = para("Both bacteria answer iron scarcity the same way: switch on the machinery that " +
  "scavenges iron from outside the cell, switch off the protein that stores it inside. In " +
  "S. flexneri 24 of 25 iron genes rose; in P. aeruginosa, 28 of 29. The organisms use " +
  "different siderophores and different regulators, yet the logic is identical — acquire " +
  "more, store less. The result survives dropping all fifteen uncharacterised iron " +
  "transporters.", C2, y, 17);

/* ---- FIGURE 3 : acquisition vs storage ---- */
const chartY = y;
{
  const PX = C2 + 1.45, PY = chartY + 1.15, PWD = COLW - 1.6, PHT = 6.0;
  const VMIN = -6, VMAX = 6, ZERO = PY + PHT * (VMAX / (VMAX - VMIN));
  const px = v => PHT * (v / (VMAX - VMIN));

  // legend
  [["Iron acquisition (median)", ORANGE], ["Iron storage (ferritin)", "5B8FA8"]]
    .forEach(([lab, col], i) => {
      const lx = C2 + 1.6 + i * 6.4;
      s.addShape(pres.ShapeType.rect, { x: lx, y: chartY + 0.25, w: 0.42, h: 0.42,
        fill: { color: col } });
      s.addText(lab, { ...B, x: lx + 0.6, y: chartY + 0.2, w: 5.6, h: 0.5, fontSize: 15 });
    });

  // gridlines + value axis
  for (let v = VMIN; v <= VMAX; v += 2) {
    const gy = ZERO - px(v);
    s.addShape(pres.ShapeType.line, { x: PX, y: gy, w: PWD, h: 0,
      line: { color: v === 0 ? "9AA0A6" : "ECECEC", width: v === 0 ? 1.4 : 1 } });
    s.addText(String(v), { ...B, x: PX - 1.35, y: gy - 0.25, w: 1.15, h: 0.5,
      fontSize: 14, color: MUTE, align: "right" });
  }
  s.addText("log2 fold change", { ...B, x: PX - 2.55, y: PY + PHT / 2 - 1.5, w: 3.0, h: 0.5,
    fontSize: 15, color: MUTE, align: "center", rotate: 270 });

  const CELLS = [
    ["P. aeruginosa", "low Fe", 4.84, -3.38],
    ["P. aeruginosa", "low O\u2082", null, null],
    ["S. flexneri", "low Fe", 2.18, -1.45],
    ["S. flexneri", "low O\u2082", -3.00, 3.96],
  ];
  const GW = PWD / 4, BW = GW * 0.26;
  CELLS.forEach(([org, pert, acq, sto], i) => {
    const gx = PX + i * GW;
    if (acq === null) {
      s.addText("n = 1\nno direction called", { ...B, x: gx, y: ZERO - 1.15, w: GW, h: 1.2,
        fontSize: 14, color: MUTE, align: "center", italic: true, lineSpacing: 19 });
    } else {
      [[acq, ORANGE, gx + GW * 0.20], [sto, "5B8FA8", gx + GW * 0.54]]
        .forEach(([v, col, bx]) => {
          const h = Math.abs(px(v));
          s.addShape(pres.ShapeType.rect, { x: bx, y: v > 0 ? ZERO - h : ZERO, w: BW, h,
            fill: { color: col } });
          s.addText(v.toFixed(2), { ...B, x: bx - 0.45, y: v > 0 ? ZERO - h - 0.55 : ZERO + h + 0.06,
            w: BW + 0.9, h: 0.5, fontSize: 14, bold: true, color: col, align: "center" });
        });
    }
    s.addText(pert, { ...B, x: gx, y: PY + PHT + 0.18, w: GW, h: 0.45, fontSize: 15,
      align: "center" });
  });
  // organism spans
  s.addShape(pres.ShapeType.line, { x: PX + 0.2, y: PY + PHT + 0.82, w: GW * 2 - 0.4, h: 0,
    line: { color: "C8CCD0", width: 1 } });
  s.addShape(pres.ShapeType.line, { x: PX + GW * 2 + 0.2, y: PY + PHT + 0.82, w: GW * 2 - 0.4, h: 0,
    line: { color: "C8CCD0", width: 1 } });
  s.addText("P. aeruginosa", { ...B, x: PX, y: PY + PHT + 0.92, w: GW * 2, h: 0.5,
    fontSize: 16, bold: true, italic: true, align: "center" });
  s.addText("S. flexneri", { ...B, x: PX + GW * 2, y: PY + PHT + 0.92, w: GW * 2, h: 0.5,
    fontSize: 16, bold: true, italic: true, align: "center" });
  y = PY + PHT + 1.65;
}
y = cap(3, "Iron limitation drives acquisition up and storage down in both species. " +
  "Oxygen limitation reverses that in S. flexneri and does nothing in P. aeruginosa " +
  "(one gene, no bar drawn).", C2, y);

y = para("Oxygen scarcity splits them. S. flexneri reverses its iron program — 20 of 22 " +
  "genes fall and ferritin rises about 16-fold, consistent with ferrous iron becoming freely " +
  "available. P. aeruginosa registers a single gene across the whole category, too few to " +
  "call a direction at all.", C2, y, 17);

/* ---- FIGURE 4 : direction matrix ---- */
const rows = [
  ["Iron uptake & storage",      "up",   "n/a",  "up",   "down"],
  ["Anaerobic respiration",      "down", "up",   "n/a",  "up"],
  ["Oxidative stress",           "down", "mix",  "up",   "down"],
  ["Carbon / amino acid",        "down", "mix",  "mix",  "mix"],
  ["Secretion & virulence",      "up",   "down", "up",   "--"],
  ["Motility",                   "n/a",  "mix",  "n/a",  "n/a"],
  ["Quorum sensing / biofilm *", "up",   "n/a",  "up",   "--"],
];
const CC = { up: UP, down: DOWN, mix: NEU, "n/a": PALE, "--": PALE };
const TX = { up: "UP", down: "DOWN", mix: "mixed", "n/a": "too few", "--": "no data" };
const LABW = 5.7, CW = (COLW - LABW) / 4, RH = 1.06;
s.addText("P. aeruginosa", { ...B, x: C2 + LABW, y, w: CW * 2, h: 0.5, bold: true,
  italic: true, fontSize: 18, align: "center" });
s.addText("S. flexneri", { ...B, x: C2 + LABW + CW * 2, y, w: CW * 2, h: 0.5, bold: true,
  italic: true, fontSize: 16, align: "center" });
["low Fe", "low O₂", "low Fe", "low O₂"].forEach((t, i) =>
  s.addText(t, { ...B, x: C2 + LABW + i * CW, y: y + 0.55, w: CW, h: 0.45, fontSize: 14,
    align: "center", color: MUTE }));
const tY = y + 1.2;
rows.forEach((r, ri) => {
  const yy = tY + ri * RH;
  if (ri % 2 === 0)
    s.addShape(pres.ShapeType.rect, { x: C2, y: yy, w: COLW, h: RH, fill: { color: "F7F7F7" } });
  s.addText(r[0], { ...B, x: C2 + 0.22, y: yy + 0.34, w: LABW - 0.3, h: 0.7, fontSize: 17,
    lineSpacing: 21 });
  for (let ci = 1; ci <= 4; ci++) {
    const v = r[ci];
    s.addShape(pres.ShapeType.rect, { x: C2 + LABW + (ci - 1) * CW + 0.13, y: yy + 0.16,
      w: CW - 0.26, h: RH - 0.32, fill: { color: CC[v] } });
    s.addText(TX[v], { ...B, x: C2 + LABW + (ci - 1) * CW + 0.13, y: yy + 0.38,
      w: CW - 0.26, h: 0.48, color: (v === "n/a" || v === "--") ? MUTE : WHITE, bold: true,
      fontSize: 15, align: "center" });
  }
});
y = tY + rows.length * RH + 0.25;
y = cap(4, "All seven categories. Row 2 is the internal control: anaerobic respiration rises " +
  "without oxygen and falls without iron, as it must, since those enzymes are iron-dependent. " +
  "That the categories recover known biology is what licenses reading the iron row above. " +
  "* Not comparable — S. flexneri has no quorum-signal synthase.", C2, y);

y = bar("Conclusion", C2, y);
y = bul([
  "Iron shortage produces a conserved response. Two bacteria separated by hundreds of millions of years, using different siderophores and regulators, move the same category the same way.",
  "Oxygen shortage does not. Only the gut pathogen converts low oxygen into a major iron response.",
  "The two shortages are therefore not interchangeable, and describing them as one host-stress program blurs a real difference between organisms.",
  "The gap is in how strongly each organism responds, not in whether it could — both carry oxygen-responsive regulatory sites at iron genes.",
], C2, y, 16);

/* ======================================================= COLUMN 3 ====== */
y = TOP;
y = bar("Three Errors, One Cause", C3, y);
y = para("Categories were first built by keyword matching. It failed three times — each time " +
  "the pattern matched text that was not gene function.", C3, y, 17);

/* ---- FIGURE 5 : how the keyword rules failed ---- */
fy = y;
const ERRS = [
  ['"alginate"', "a database category label,\nnot any gene",
   "51 secreted factors + both iron operons → quorum sensing"],
  ['"iron"', "proteins that contain iron,\nnot acquire it",
   "cytochrome maturation, Fe-S subunits → iron"],
  ['"hydrogenase"', "inside the word\nde-hydrogenase",
   "Complex I, TCA cycle, glycolysis → anaerobic respiration"],
];
{
  const RH5 = 2.05, PATW = 4.2, MATW = 4.6;
  s.addText("pattern", { ...B, x: C3 + 1.0, y: fy, w: PATW, h: 0.4, fontSize: 13,
    color: MUTE, italic: true });
  s.addText("matched", { ...B, x: C3 + 1.0 + PATW + 0.7, y: fy, w: MATW, h: 0.4,
    fontSize: 13, color: MUTE, italic: true });
  ERRS.forEach(([pat, matched, effect], i) => {
    const yy = fy + 0.45 + i * RH5;
    s.addShape(pres.ShapeType.rect, { x: C3, y: yy, w: COLW, h: RH5 - 0.18,
      fill: { color: i % 2 ? "FAF6F2" : TINT } });
    s.addText(String(i + 1), { ...B, x: C3 + 0.28, y: yy + 0.24, w: 0.7, h: 0.6, bold: true,
      color: ORANGE, fontSize: 21 });
    s.addText(pat, { ...B, x: C3 + 1.0, y: yy + 0.26, w: PATW, h: 0.55, bold: true,
      fontFace: "Courier New", fontSize: 18 });
    s.addShape(pres.ShapeType.rightArrow, { x: C3 + 1.0 + PATW + 0.1, y: yy + 0.4, w: 0.45,
      h: 0.26, fill: { color: MUTE } });
    s.addText(matched, { ...B, x: C3 + 1.0 + PATW + 0.7, y: yy + 0.2, w: MATW, h: 0.9,
      fontSize: 15, lineSpacing: 19 });
    s.addText(effect, { ...B, x: C3 + 1.0, y: yy + 1.16, w: COLW - 1.3, h: 0.6,
      fontSize: 15, color: DOWN, lineSpacing: 19 });
  });
  y = fy + 0.45 + ERRS.length * RH5 + 0.1;
}
y = cap(5, "The third was found only by independent review, after the sets had already been " +
  "audited twice. Separately, arcA names two unrelated genes in these organisms — matching " +
  "sets by name would have created a false agreement.", C3, y);

y = bar("What This Means", C3, y);
y = para("The conserved iron response is not new on its own — the iron-sparing program is " +
  "well described in single organisms. What the matched design adds is the comparison. It " +
  "shows the program holds across lineages while the oxygen response does not, and it does so " +
  "with the perturbation held constant, which single-organism studies cannot do.\n\n" +
  "The practical implication is for anyone reading host-infection transcriptomes, where a " +
  "bacterium is short of iron and oxygen simultaneously. These results say the iron half of " +
  "that signature should look similar between species while the oxygen half will not — so an " +
  "iron signature seen in one organism cannot be assumed to mean the same thing in another.",
  C3, y, 16);

y = bar("Limitations", C3, y);
y = bul([
  "The Pseudomonas iron treatment (PQS) is both an iron chelator and a quorum-sensing signal, so that column is not a clean iron perturbation. A closely related signal, HHQ, produced no detectable response at the same dose — which argues against a purely quorum-driven explanation, but the confound stands and is disclosed rather than argued away.",
  "Both species carry oxygen-responsive regulation at iron promoters; P. aeruginosa has an ANR site alongside Fur and BqsR sites upstream of the ferrous transporter. The finding concerns response magnitude under these conditions, not regulatory capability.",
  "The Shigella datasets publish only genes reaching significance, so no non-significant background exists and enrichment testing was not possible for those cells.",
  "Two biological replicates per Pseudomonas condition; one contrast used a variance-shrinkage moderated t-test approximating limma rather than limma itself.",
  "The hypothesis was revised once after the first dataset was examined, so the Pseudomonas findings are exploratory. The category freeze preceded all Shigella analysis.",
  "Three keyword artifacts were found and corrected, all of one kind: a pattern matching text that was not gene function. A later completeness audit added 47 genes that met a category definition but had never been assigned. No revision changed a result.",
], C3, y, 16);

y = bar("Acknowledgments & References", C3, y);
para("Thanks to _______________________ for mentorship and guidance throughout this project; " +
  "to the authors of all four source studies for depositing their data publicly; and to " +
  "Zain Baki, whose independent audit of the gene sets identified a third annotation error " +
  "and three category corrections. No external funding supported this work.\n\n" +
  "Boulette & Payne 2007 J Bacteriol 189:6957 · Trunk et al. 2010 Environ Microbiol · " +
  "Rampioni et al. GSE81364 · Lozano Aguirre et al. 2020 PeerJ 8:e9553 · " +
  "Vergara-Irigaray et al. 2014 BMC Genomics 15:438.", C3, y, 17);

pres.writeFile({ fileName: "/home/claude/poster_ut.pptx" }).then(() => console.log("written"));
