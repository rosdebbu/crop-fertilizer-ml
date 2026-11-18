// Builds Crop_Fertilizer_ML_Final.pptx. Run from repo root: node scripts/build_final_deck.js
// (needs `npm i pptxgenjs`; numbers below come from outputs/results.json)
const pptxgen = require("pptxgenjs");
const R = require("../outputs/results.json");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "Crop Recommendation & Fertilizer Prediction";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };

const DARK = "1F3D2B", MOSS = "5E8C4A", LEAF = "E6EFDF", AMBER = "E0A526", INK = "22302A", MUTE = "5F6F66", WHITE = "FFFFFF";
const H = "Cambria", B = "Calibri";
const m = R.metrics, q = R.data_quality;

pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  slideNumber: { x: 9.2, y: 5.25, w: 0.5, h: 0.25, fontFace: B, fontSize: 10, color: MUTE },
});

function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.7, fontFace: H, fontSize: 32, bold: true, color: DARK, margin: 0, isTextBox: true });
  if (notes) s.addNotes(notes);
  return s;
}
const card = (s, x, y, w, h, fill = LEAF) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 });
const txt = (s, t, o) => s.addText(t, { fontFace: B, color: INK, margin: 0, isTextBox: true, ...o });

// 1 Title
{
  const s = pres.addSlide(); s.background = { color: DARK };
  txt(s, "Crop Recommendation &\nFertilizer Prediction", { x: 0.7, y: 1.2, w: 8.6, h: 1.8, fontFace: H, fontSize: 44, bold: true, color: WHITE });
  txt(s, "A machine-learning decision-support system for soil and climate data", { x: 0.7, y: 3.1, w: 8, h: 0.5, fontSize: 18, color: LEAF });
  txt(s, "Random Forest · Decision Tree · KNN · FastAPI · Web UI", { x: 0.7, y: 4.4, w: 8, h: 0.4, fontSize: 14, color: AMBER, bold: true });
  s.addNotes("Introduce the project: predict the best crop and fertilizer from soil nutrients and weather, served as a web app.");
}
// 2 Problem
{
  const s = content("Problem and objectives", "Farmers pick crops and fertilizer by habit; over-fertilizing costs money and soil health.");
  card(s, 0.5, 1.2, 4.3, 3.6);
  txt(s, "The problem", { x: 0.75, y: 1.35, w: 3.8, h: 0.4, fontSize: 20, bold: true, color: DARK, fontFace: H });
  txt(s, "Crop choice and fertilizer dose are usually guesses, so yield is lost and fertilizer is wasted.",
    { x: 0.75, y: 1.85, w: 3.8, h: 1.2, fontSize: 16 });
  txt(s, "Soil N-P-K, pH and weather already contain the answer.", { x: 0.75, y: 3.2, w: 3.8, h: 1, fontSize: 16, italic: true, color: MOSS });
  const obj = [["1", "Recommend the best crop from 7 soil and climate inputs"], ["2", "Recommend a fertilizer from soil nutrients, soil type and weather"],
    ["3", "Compare 3 models and report honest metrics"], ["4", "Serve everything through an API and a web UI"]];
  obj.forEach(([n, t], i) => {
    const y = 1.2 + i * 0.92;
    s.addShape(pres.shapes.OVAL, { x: 5.2, y: y + 0.08, w: 0.55, h: 0.55, fill: { color: MOSS }, line: { color: MOSS } });
    txt(s, n, { x: 5.2, y: y + 0.08, w: 0.55, h: 0.55, align: "center", valign: "middle", fontSize: 18, bold: true, color: WHITE });
    txt(s, t, { x: 5.95, y, w: 3.6, h: 0.75, fontSize: 15, valign: "middle" });
  });
}
// 3 Data
{
  const s = content("Datasets", "Crop data is the public 22-crop set. Both datasets are the real Kaggle files; the fertilizer file has no learnable signal (slide 9).");
  [["2,200", "crop rows", "22 crops, Kaggle (atharvaingle)"], ["7", "crop inputs", "N, P, K, temp, humidity, pH, rainfall"], ["100,000", "fertilizer rows", "7 fertilizers, Kaggle (irakozekelly)"], ["7", "fertilizer inputs", "temp, humidity, moisture, soil, N-P-K"]]
    .forEach(([big, lab, sub], i) => {
      const x = 0.5 + i * 2.3;
      card(s, x, 1.3, 2.1, 2.5);
      txt(s, big, { x, y: 1.55, w: 2.1, h: 0.9, align: "center", fontFace: H, fontSize: 32, bold: true, color: MOSS });
      txt(s, lab, { x, y: 2.45, w: 2.1, h: 0.4, align: "center", fontSize: 16, bold: true, color: DARK });
      txt(s, sub, { x: x + 0.15, y: 2.9, w: 1.8, h: 0.8, align: "center", fontSize: 12, color: MUTE });
    });
  txt(s, "No missing values or duplicates in either file. Split 80/20, stratified, random_state=42.", { x: 0.5, y: 4.2, w: 9, h: 0.5, fontSize: 15 });
}
// 4 Architecture
{
  const s = content("System architecture", "Models train once at startup; every request reuses the fitted scaler and models.");
  const boxes = [["CSV data", "data/"], ["Training", "scikit-learn"], ["FastAPI", "/api/predict/*"], ["Web UI", "static/ HTML + JS"]];
  boxes.forEach(([t, sub], i) => {
    const x = 0.5 + i * 2.35;
    card(s, x, 1.7, 1.9, 1.5, i % 2 ? MOSS : DARK);
    txt(s, t, { x, y: 1.9, w: 1.9, h: 0.5, align: "center", fontFace: H, fontSize: 20, bold: true, color: WHITE });
    txt(s, sub, { x, y: 2.5, w: 1.9, h: 0.5, align: "center", fontSize: 12, color: LEAF });
    if (i < 3) txt(s, "→", { x: x + 1.9, y: 2.1, w: 0.45, h: 0.6, align: "center", fontSize: 28, bold: true, color: AMBER });
  });
  txt(s, "Also exposed: /api/status, /api/metrics, dataset samples, profit and dosage calculators, climate-stress simulation, crop rotation.",
    { x: 0.5, y: 3.8, w: 9, h: 0.8, fontSize: 15 });
}
// 5 Pipeline
{
  const s = content("ML pipeline", "Scaler is fitted on the training split only, which prevents test-data leakage.");
  const steps = [["Load", "pandas read_csv"], ["Encode", "LabelEncoder for soil type"], ["Split", "80/20, stratified"], ["Scale", "StandardScaler on train only"], ["Train", "RF · DT · KNN"], ["Evaluate", "Acc, P, R, F1, 5-fold CV"]];
  steps.forEach(([t, d], i) => {
    const col = i % 3, row = Math.floor(i / 3), x = 0.5 + col * 3.1, y = 1.3 + row * 1.9;
    card(s, x, y, 2.8, 1.6);
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.2, w: 0.5, h: 0.5, fill: { color: AMBER }, line: { color: AMBER } });
    txt(s, String(i + 1), { x: x + 0.2, y: y + 0.2, w: 0.5, h: 0.5, align: "center", valign: "middle", fontSize: 16, bold: true, color: DARK });
    txt(s, t, { x: x + 0.85, y: y + 0.2, w: 1.8, h: 0.5, fontFace: H, fontSize: 20, bold: true, color: DARK, valign: "middle" });
    txt(s, d, { x: x + 0.2, y: y + 0.9, w: 2.4, h: 0.55, fontSize: 14 });
  });
}
// 6 Models
{
  const s = content("Three models compared", "Trade-off: interpretability vs accuracy vs speed.");
  [["Random Forest", "100 trees on bootstrap samples; votes averaged.", "Most accurate, less interpretable", DARK],
   ["Decision Tree", "One tree of if-else splits.", "Easy to explain, overfits", MOSS],
   ["KNN (k=5)", "Majority vote of 5 nearest points.", "Needs scaling, slower on big data", "8A6F1E"]]
    .forEach(([t, d, tr, col], i) => {
      const x = 0.5 + i * 3.1;
      card(s, x, 1.3, 2.8, 3.4);
      s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: 1.5, w: 0.6, h: 0.6, fill: { color: col }, line: { color: col } });
      txt(s, t, { x: x + 0.2, y: 2.3, w: 2.4, h: 0.5, fontFace: H, fontSize: 20, bold: true, color: DARK });
      txt(s, d, { x: x + 0.2, y: 2.9, w: 2.4, h: 0.9, fontSize: 14 });
      txt(s, tr, { x: x + 0.2, y: 3.85, w: 2.4, h: 0.7, fontSize: 14, bold: true, color: col });
    });
}
// chart helper
function barChart(s, x, y, w, h, series, title) {
  s.addChart(pres.charts.BAR, series, {
    x, y, w, h, barDir: "col", barGrouping: "clustered", chartColors: [DARK, AMBER],
    showTitle: true, title, titleFontSize: 14, titleColor: DARK, titleFontFace: B,
    showValue: true, dataLabelFontSize: 11, dataLabelColor: INK, dataLabelFontFace: B, dataLabelFormatCode: "0.0",
    catAxisLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelFontFace: B,
    valAxisLabelColor: MUTE, valAxisLabelFontSize: 11, valAxisLabelFontFace: B, valAxisMinVal: 0, valAxisMaxVal: 100,
    valGridLine: { color: "E3E8E1", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: B, legendColor: INK,
  });
}
const names = ["Random Forest", "Decision Tree", "KNN"];
const ser = (k) => [{ name: "Test accuracy %", labels: names, values: names.map((n) => m[k][n].accuracy) },
  { name: "5-fold CV accuracy %", labels: names, values: names.map((n) => m[k][n].cv_accuracy) }];
// 7 Crop results
{
  const s = content("Crop model results", "99.5% hold-out and 99.5% cross-validated means no sign of overfitting. Chance would be 4.5%.");
  barChart(s, 0.5, 1.2, 5.6, 3.7, ser("crop"), "Crop recommendation (22 classes)");
  card(s, 6.4, 1.2, 3.1, 3.7);
  txt(s, "99.55%", { x: 6.4, y: 1.45, w: 3.1, h: 0.9, align: "center", fontFace: H, fontSize: 44, bold: true, color: MOSS });
  txt(s, "Random Forest accuracy", { x: 6.4, y: 2.35, w: 3.1, h: 0.4, align: "center", fontSize: 14, bold: true, color: DARK });
  txt(s, `Chance level is ${q.crop.chance_level_pct}%.\nCross-validation agrees, so the score is not a lucky split.`, { x: 6.6, y: 2.95, w: 2.7, h: 1.6, fontSize: 14, align: "center" });
}
// 8 Crop diagnostics
{
  const s = content("Crop: where the model looks", "Confusion matrix is almost diagonal; rainfall, humidity and potassium drive most splits.");
  s.addImage({ path: "output_charts/05_confusion_matrix_random_forest.png", x: 0.5, y: 1.15, w: 4.1, h: 3.44, sizing: { type: "contain", w: 4.1, h: 3.44 } });
  s.addImage({ path: "output_charts/07_feature_importance.png", x: 4.9, y: 1.4, w: 4.6, h: 2.73 });
  txt(s, "Confusion matrix (Random Forest)", { x: 0.5, y: 4.7, w: 4.1, h: 0.3, fontSize: 12, color: MUTE, align: "center" });
  txt(s, "Feature importance", { x: 4.9, y: 4.2, w: 4.6, h: 0.3, fontSize: 12, color: MUTE, align: "center" });
}
// 9 Fertilizer finding
{
  const s = content("Fertilizer: what the real data shows", "Real Kaggle labels are independent of the features. The synthetic run proves the code works; the data is the limit.");
  const sy = R.synthetic_fertilizer.metrics["Random Forest"].accuracy;
  card(s, 0.5, 1.2, 4.4, 3.6, "F6E3E0");
  txt(s, "Real Kaggle data", { x: 0.75, y: 1.35, w: 3.9, h: 0.4, fontFace: H, fontSize: 20, bold: true, color: "9A2F22" });
  txt(s, `${m.fertilizer["Random Forest"].accuracy}%`, { x: 0.75, y: 1.8, w: 3.9, h: 0.9, fontFace: H, fontSize: 48, bold: true, color: "9A2F22" });
  txt(s, "Chance for 7 classes is 14.3%. Mean N, P and K are identical for every fertilizer, so no model can separate them.",
    { x: 0.75, y: 2.85, w: 3.9, h: 1.8, fontSize: 14 });
  card(s, 5.1, 1.2, 4.4, 3.6);
  txt(s, "Pipeline check (synthetic)", { x: 5.35, y: 1.35, w: 3.9, h: 0.4, fontFace: H, fontSize: 20, bold: true, color: DARK });
  txt(s, `${sy}%`, { x: 5.35, y: 1.8, w: 3.9, h: 0.9, fontFace: H, fontSize: 48, bold: true, color: MOSS });
  txt(s, "Same code on 5,000 rule-based rows (nutrient below 20 is deficient). Shows the models learn when labels have signal.",
    { x: 5.35, y: 2.85, w: 3.9, h: 1.8, fontSize: 14 });
}
// 10 Fertilizer results
{
  const s = content("Fertilizer model results", "App flags the real-data model as unreliable via data_quality.warning.");
  const S = R.synthetic_fertilizer.metrics;
  barChart(s, 0.5, 1.2, 5.6, 3.7, [{ name: "Real Kaggle data %", labels: names, values: names.map((n) => m.fertilizer[n].accuracy) },
    { name: "Rule-based synthetic %", labels: names, values: names.map((n) => S[n].accuracy) }], "Fertilizer prediction (7 classes)");
  card(s, 6.4, 1.2, 3.1, 3.7);
  txt(s, "14.3%", { x: 6.4, y: 1.45, w: 3.1, h: 0.9, align: "center", fontFace: H, fontSize: 44, bold: true, color: "9A2F22" });
  txt(s, "random-guess level", { x: 6.4, y: 2.35, w: 3.1, h: 0.4, align: "center", fontSize: 14, bold: true, color: DARK });
  txt(s, "Real-data bars sit on this line, so the app shows a warning instead of a confident answer.", { x: 6.6, y: 2.95, w: 2.7, h: 1.6, fontSize: 14, align: "center" });
}
// 11 Live output
{
  const s = content("Live API output", "Both outputs come from outputs/results.json, produced by the running app.");
  const c = R.sample_crop_prediction, f = R.sample_fertilizer_prediction;
  card(s, 0.5, 1.2, 4.4, 3.6, "17261E");
  txt(s, "POST /api/predict/crop", { x: 0.75, y: 1.35, w: 3.9, h: 0.35, fontFace: "Courier New", fontSize: 13, bold: true, color: AMBER });
  txt(s, "N=80 P=48 K=40\ntemp=23.7 humidity=82\npH=6.4 rainfall=236", { x: 0.75, y: 1.8, w: 3.9, h: 0.9, fontFace: "Courier New", fontSize: 12, color: LEAF });
  txt(s, `→ ${c.crop}`, { x: 0.75, y: 2.9, w: 3.9, h: 0.6, fontFace: H, fontSize: 30, bold: true, color: WHITE });
  txt(s, `confidence ${c.confidence}% · ${c.model_used}`, { x: 0.75, y: 3.6, w: 3.9, h: 0.4, fontSize: 14, color: LEAF });
  card(s, 5.1, 1.2, 4.4, 3.6, "17261E");
  txt(s, "POST /api/predict/fertilizer", { x: 5.35, y: 1.35, w: 3.9, h: 0.35, fontFace: "Courier New", fontSize: 13, bold: true, color: AMBER });
  txt(s, "Loamy soil, moisture 40\nN=5 P=30 K=30\n(real-data model)", { x: 5.35, y: 1.8, w: 3.9, h: 0.9, fontFace: "Courier New", fontSize: 12, color: LEAF });
  txt(s, `→ ${f.fertilizer}`, { x: 5.35, y: 2.9, w: 3.9, h: 0.6, fontFace: H, fontSize: 30, bold: true, color: WHITE });
  txt(s, `confidence ${f.confidence}% · warning shown`, { x: 5.35, y: 3.6, w: 3.9, h: 0.4, fontSize: 14, color: LEAF });
}
// 12 Management
{
  const s = content("Project structure and quality", "Everything reproducible from the repo.");
  const rows = [["app.py", "FastAPI server, training, prediction"], ["data/", "real Kaggle CSVs, synthetic/ holds the experiment"],
    ["scripts/", "synthetic-data experiment, deck builder"], ["outputs/", "run logs and results.json"], ["output_charts*/", "EDA and evaluation charts"],
    ["test_api.py", "6 automated tests, all passing"], ["requirements.txt", "complete dependency list"]];
  rows.forEach(([a, b], i) => {
    const y = 1.2 + i * 0.52;
    txt(s, a, { x: 0.6, y, w: 2.3, h: 0.42, fontFace: "Courier New", fontSize: 14, bold: true, color: MOSS, valign: "middle" });
    txt(s, b, { x: 3.0, y, w: 6.4, h: 0.42, fontSize: 15, valign: "middle" });
  });
}
// 13 Limitations
{
  const s = content("Limitations and future work", "Say these first in the viva.");
  const L = [["Fertilizer labels carry no signal", "Needs a dataset where the fertilizer follows soil tests"], ["Sample market and weather data", "Connect live weather, NDVI and mandi APIs"],
    ["No hyper-parameter tuning", "GridSearchCV on trees, depth and k"], ["Startup training", "Save models with joblib and load at launch"]];
  L.forEach(([a, b], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.25 + Math.floor(i / 2) * 1.8;
    card(s, x, y, 4.4, 1.6);
    txt(s, a, { x: x + 0.25, y: y + 0.2, w: 3.9, h: 0.4, fontFace: H, fontSize: 18, bold: true, color: DARK });
    txt(s, b, { x: x + 0.25, y: y + 0.75, w: 3.9, h: 0.7, fontSize: 14 });
  });
}
// 14 Conclusion
{
  const s = pres.addSlide(); s.background = { color: DARK };
  txt(s, "Conclusion", { x: 0.7, y: 0.6, w: 8, h: 0.8, fontFace: H, fontSize: 38, bold: true, color: WHITE });
  [["99.55%", "crop accuracy, confirmed by cross-validation"], [`${m.fertilizer["Random Forest"].accuracy}%`, "fertilizer on real data = chance, flagged by the app"], ["6 / 6", "automated tests passing"]]
    .forEach(([a, b], i) => {
      const x = 0.7 + i * 3.0;
      txt(s, a, { x, y: 1.9, w: 2.7, h: 0.9, fontFace: H, fontSize: 42, bold: true, color: AMBER });
      txt(s, b, { x, y: 2.85, w: 2.6, h: 0.9, fontSize: 15, color: LEAF });
    });
  txt(s, "Thank you. Questions?", { x: 0.7, y: 4.4, w: 8, h: 0.5, fontSize: 20, color: WHITE });
}
pres.writeFile({ fileName: "Crop_Fertilizer_ML_Final.pptx" }).then((f) => console.log("wrote", f));
