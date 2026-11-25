const pptxgen = require("pptxgenjs");

// Palette: "Forest & Moss" adapted for Siddha/herbal theme + turmeric accent
const FOREST = "2C5F2D";
const MOSS = "97BC62";
const CREAM = "F5F1E6";
const TURMERIC = "C98A2C";
const INK = "2B2620";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5

const DISCLAIMER = "Prototype using SYNTHETIC data for academic demonstration only \u2014 NOT for clinical diagnosis.";

function titleSlide() {
  const s = pres.addSlide();
  s.background = { color: FOREST };
  s.addShape("rect", { x: 0, y: 4.7, w: 13.33, h: 2.8, fill: { color: "255F3B", transparency: 60 } });
  s.addText("Siddha Vision", {
    x: 0.7, y: 1.1, w: 11.5, h: 1.1, fontFace: "Cambria", fontSize: 44, bold: true, color: CREAM,
  });
  s.addText("AI-Assisted Digital Neerkuri & Neikuri Analysis Platform", {
    x: 0.7, y: 2.15, w: 11.5, h: 0.7, fontFace: "Calibri", fontSize: 20, color: MOSS,
  });
  s.addText("Digitizing a traditionally subjective examination into measurable, explainable features", {
    x: 0.7, y: 2.85, w: 11.5, h: 0.5, fontFace: "Calibri", fontSize: 14, italic: true, color: CREAM,
  });
  s.addText("Academic Prototype \u00b7 College Demonstration Project", {
    x: 0.7, y: 6.6, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 13, color: CREAM, italic: true,
  });
  s.addText(DISCLAIMER, {
    x: 0.7, y: 7.0, w: 11.9, h: 0.35, fontFace: "Calibri", fontSize: 10, color: TURMERIC, bold: true,
  });
}

function sectionHeader(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: CREAM };
  s.addShape("rect", { x: 0, y: 0, w: 0.25, h: 7.5, fill: { color: TURMERIC } });
  s.addText(title, { x: 0.7, y: 0.5, w: 11.5, h: 0.9, fontFace: "Cambria", fontSize: 30, bold: true, color: FOREST });
  if (subtitle) s.addText(subtitle, { x: 0.7, y: 1.3, w: 11.5, h: 0.5, fontFace: "Calibri", fontSize: 15, color: INK });
  return s;
}

function bulletBlock(s, items, opts = {}) {
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i !== items.length - 1, paraSpaceAfter: 10 } })),
    { x: opts.x || 0.9, y: opts.y || 2.1, w: opts.w || 6.6, h: opts.h || 4.6, fontFace: "Calibri", fontSize: opts.fs || 15, color: INK, valign: "top" }
  );
}

function iconCircleRow(s, items, y) {
  const startX = 0.9, gap = (11.5) / items.length;
  items.forEach((it, i) => {
    const x = startX + i * gap;
    s.addShape("ellipse", { x, y, w: 0.9, h: 0.9, fill: { color: MOSS } });
    s.addText(it.n, { x, y, w: 0.9, h: 0.9, align: "center", valign: "middle", fontFace: "Cambria", bold: true, fontSize: 20, color: FOREST });
    s.addText(it.label, { x: x - 0.3, y: y + 1.0, w: gap - 0.1, h: 0.9, align: "center", fontFace: "Calibri", fontSize: 12, color: INK });
  });
}

// 1. Title
titleSlide();

// 2. Problem & Objective
{
  const s = sectionHeader("Objective", "What the prototype does \u2014 and does not \u2014 do");
  bulletBlock(s, [
    "Digitize Neerkuri (urine) and Neikuri (oil-drop) observation into objective, measurable features",
    "Standardize an examination that currently depends heavily on practitioner experience",
    "Present transparent, rule-based observations alongside an ML-based pattern category",
    "Estimate an illustrative kidney-health risk category (Low / Moderate / High) for demonstration",
  ], { w: 6.2 });
  s.addShape("roundRect", { x: 7.5, y: 2.1, w: 4.9, h: 3.2, fill: { color: FOREST }, rectRadius: 0.15 });
  s.addText("This AI does NOT diagnose disease.\nIt assists standardization and\ndemonstrates an explainable ML\nworkflow on synthetic data.", {
    x: 7.8, y: 2.4, w: 4.3, h: 2.7, fontFace: "Calibri", fontSize: 14, color: CREAM, valign: "middle",
  });
}

// 3. Traditional background
{
  const s = sectionHeader("Siddha Background", "Neerkuri & Neikuri examination");
  bulletBlock(s, [
    "Neerkuri: observation of urine colour, transparency, foam and odour",
    "Neikuri: a drop of gingelly (sesame) oil is placed on urine; its spread pattern is observed",
    "Traditional practice links patterns to Vatham, Pitham, Kabham \u2014 the three humors",
    "This prototype encodes these ideas as measurable, synthetic numeric features",
  ]);
}

// 4. System architecture
{
  const s = sectionHeader("System Architecture");
  const boxes = [
    { t: "React Dashboard", x: 0.8 },
    { t: "FastAPI Backend", x: 4.9 },
    { t: "ML Model\n(Random Forest)", x: 9.0 },
  ];
  boxes.forEach((b) => {
    s.addShape("roundRect", { x: b.x, y: 2.6, w: 3.3, h: 1.3, fill: { color: MOSS }, rectRadius: 0.12 });
    s.addText(b.t, { x: b.x, y: 2.6, w: 3.3, h: 1.3, align: "center", valign: "middle", fontFace: "Calibri", bold: true, fontSize: 15, color: INK });
  });
  s.addText("\u2192", { x: 4.1, y: 2.85, w: 0.8, h: 0.8, fontSize: 28, color: FOREST, align: "center" });
  s.addText("\u2192", { x: 8.2, y: 2.85, w: 0.8, h: 0.8, fontSize: 28, color: FOREST, align: "center" });
  s.addText("Upload image / enter values \u2192 extract features \u2192 encode + classify \u2192 return risk, humor, feature importance, printable report", {
    x: 0.9, y: 4.4, w: 11.2, h: 0.8, fontFace: "Calibri", fontSize: 14, color: INK, italic: true,
  });
}

// 5. Dataset
{
  const s = sectionHeader("Synthetic Dataset", "500 rows \u00b7 25 columns \u00b7 fully generated for this demo");
  bulletBlock(s, [
    "Urine features: colour, HSV, transparency, foam %, sediment %, odour score",
    "Neikuri features: spread diameter/speed, shape, branch count, circularity, fractal dimension",
    "Tridosha proxy scores: Vatham, Pitham, Kabham (%) + predominant humor label",
    "Target: prototype_risk (Low / Moderate / High)",
  ], { w: 11.2, y: 2.2 });
  s.addText("Generated with hidden \u201crisk_latent\u201d logic so features correlate realistically \u2014 e.g. high foam + high sediment + irregular oil + high branching \u2192 higher risk.", {
    x: 0.9, y: 5.1, w: 11.2, h: 1.0, fontFace: "Calibri", fontSize: 13, italic: true, color: FOREST,
  });
}

// 6. ML pipeline
{
  const s = sectionHeader("Machine Learning Pipeline");
  iconCircleRow(s, [
    { n: "1", label: "Load CSV" },
    { n: "2", label: "Encode categorical\nvariables" },
    { n: "3", label: "Train/test split" },
    { n: "4", label: "Random Forest\n(300 trees)" },
    { n: "5", label: "Evaluate & save\nmodel.pkl" },
  ], 2.4);
  s.addText("Test accuracy: ~73% on held-out synthetic data \u00b7 balanced class weighting", {
    x: 0.9, y: 5.2, w: 11.2, h: 0.5, fontFace: "Calibri", fontSize: 14, color: INK,
  });
}

// 6b. Rule Engine + Explainability (hybrid architecture)
{
  const s = sectionHeader("Hybrid Architecture", "Rule engine + ML, not ML alone");
  s.addShape("roundRect", { x: 0.8, y: 2.3, w: 5.6, h: 3.6, fill: { color: MOSS }, rectRadius: 0.12 });
  s.addText("Rule Engine", { x: 1.1, y: 2.5, w: 5, h: 0.5, fontFace: "Cambria", bold: true, fontSize: 18, color: FOREST });
  s.addText([
    { text: "Plain IF/THEN conditions on measured features", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "e.g. foam % > 40 \u2192 \"high foam observed\"", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Fully transparent \u2014 no learning, no black box", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Describes observations only, never a disease", options: { bullet: true, breakLine: false } },
  ], { x: 1.1, y: 3.1, w: 5, h: 2.6, fontFace: "Calibri", fontSize: 13, color: INK });

  s.addShape("roundRect", { x: 6.9, y: 2.3, w: 5.6, h: 3.6, fill: { color: FOREST }, rectRadius: 0.12 });
  s.addText("ML + SHAP", { x: 7.2, y: 2.5, w: 5, h: 0.5, fontFace: "Cambria", bold: true, fontSize: 18, color: CREAM });
  s.addText([
    { text: "Random Forest finds patterns across all features", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "SHAP explains WHY a specific sample got its category", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Per-patient + global explainability, not just a black-box score", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Labelled clearly as illustrative, not diagnostic", options: { bullet: true, breakLine: false } },
  ], { x: 7.2, y: 3.1, w: 5, h: 2.6, fontFace: "Calibri", fontSize: 13, color: CREAM });
}

// 7. Results
{
  const s = sectionHeader("Model Results");
  bulletBlock(s, [
    "Accuracy: ~0.73 (3-class: Low / Moderate / High)",
    "Top predictive features (RF + SHAP agree): circularity, HSV saturation, fractal dimension, sediment %, foam %",
    "Confusion matrix, global feature importance, and SHAP summary generated automatically",
  ], { w: 11.2, y: 2.2, h: 2.2 });
  s.addText("(See ml/confusion_matrix.png, ml/feature_importance.csv, ml/shap_summary.png)", {
    x: 0.9, y: 4.6, w: 11.2, h: 0.5, fontFace: "Calibri", fontSize: 13, italic: true, color: FOREST,
  });
}

// 8. Dashboard
{
  const s = sectionHeader("Dashboard Preview", "React + Tailwind, herbal/earthy design language");
  bulletBlock(s, [
    "Upload panel: urine/Neikuri photo or manual feature entry",
    "Digitized observations: transparent rule-based findings (non-ML)",
    "Model-associated pattern: prototype risk category + per-patient SHAP explanation",
    "Printable patient report combining both layers",
  ]);
}

// 9. Limitations
{
  const s = sectionHeader("Limitations");
  bulletBlock(s, [
    "100% synthetic data \u2014 not derived from real patients",
    "Image feature extraction is a placeholder CV pipeline, not validated",
    "No clinical validation or peer review performed",
    "Small sample (500 rows); humor scoring is a simplified numeric proxy",
  ]);
}

// 10. Future scope
{
  const s = sectionHeader("Future Scope");
  bulletBlock(s, [
    "Standardised capture rig + 20\u201330 sec video for oil-spread growth rate / velocity",
    "Ethically-approved real Neerkuri/Neikuri dataset with domain experts",
    "U-Net based oil-pattern segmentation for precise branch/boundary detection",
    "Expand rule engine with Siddha practitioners; ML for pattern grouping only",
    "Clinical validation study vs practitioner assessment",
  ]);
}

// 11. Closing / disclaimer
{
  const s = pres.addSlide();
  s.background = { color: FOREST };
  s.addText("Thank You", { x: 0.9, y: 2.4, w: 11, h: 1.2, fontFace: "Cambria", fontSize: 36, bold: true, color: CREAM });
  s.addText(DISCLAIMER, { x: 0.9, y: 3.7, w: 11, h: 0.6, fontFace: "Calibri", fontSize: 15, color: TURMERIC, bold: true });
  s.addText("Questions & discussion welcome.", { x: 0.9, y: 4.4, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 14, color: MOSS });
}

pres.writeFile({ fileName: "Siddha_AI_Prototype_Presentation.pptx" }).then(() => console.log("done"));
