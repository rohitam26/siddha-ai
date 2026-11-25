import React, { useState } from "react";
import axios from "axios";

const COLORS = ["Pale Yellow", "Yellow", "Amber", "Dark Amber", "Reddish", "Brownish"];
const OIL_SHAPES = ["Circular", "Ring", "Snake", "Pearl", "Lotus", "Branched", "Spiral", "Irregular"];
const HUMORS = ["Vatham", "Pitham", "Kabham", "Vatha-Pitha", "Pitha-Kabha", "Vatha-Kabha"];

const DEFAULTS = {
  age: 45,
  gender: "Male",
  predominant_humor: "Pitham",
  vatham_score: 33,
  pitham_score: 34,
  kabham_score: 33,
  // Neerkuri
  urine_color: "Yellow",
  HSV_H: 45,
  HSV_S: 50,
  HSV_V: 70,
  transparency_score: 6.5,
  foam_percentage: 20,
  foam_bubble_count: 50,
  sediment_percentage: 12,
  odor_score: 4,
  // Neikuri
  oil_spread_diameter_mm: 18,
  oil_spread_speed: 5.2,
  oil_shape: "Ring",
  branch_count: 2,
  circularity: 0.72,
  symmetry_score: 6.8,
  edge_roughness: 2.8,
  fractal_dimension: 1.18,
};

export default function UploadPanel({ apiBase, onResult }) {
  const [form, setForm] = useState(DEFAULTS);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState(null);

  // Neerkuri (Urine) Image State
  const [neerkuriFile, setNeerkuriFile] = useState(null);
  const [neerkuriPreview, setNeerkuriPreview] = useState(null);
  const [neerkuriQuality, setNeerkuriQuality] = useState(null);
  const [neerkuriLoading, setNeerkuriLoading] = useState(false);

  // Neikuri (Oil Drop) Image State
  const [neikuriFile, setNeikuriFile] = useState(null);
  const [neikuriPreview, setNeikuriPreview] = useState(null);
  const [neikuriQuality, setNeikuriQuality] = useState(null);
  const [neikuriLoading, setNeikuriLoading] = useState(false);

  const update = (k, v) => setForm((prev) => ({ ...prev, [k]: v }));

  // Handle Neerkuri Upload
  const handleNeerkuriUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setNeerkuriFile(file);
    setNeerkuriLoading(true);
    setError(null);

    const fd = new FormData();
    fd.append("file", file);

    try {
      // Use modular endpoint or fallback
      const url = `${apiBase}/api/v1/vision/neerkuri`;
      const res = await axios.post(url, fd);
      const data = res.data;
      if (data.annotated_preview_base64) {
        setNeerkuriPreview(data.annotated_preview_base64);
      } else {
        setNeerkuriPreview(URL.createObjectURL(file));
      }
      setNeerkuriQuality(data.quality);

      if (data.extracted_features) {
        setForm((prev) => ({
          ...prev,
          ...data.extracted_features,
        }));
      }
    } catch (err) {
      console.warn("Vision endpoint failed, attempting legacy fallback:", err);
      try {
        const res = await axios.post(`${apiBase}/upload`, fd);
        setNeerkuriPreview(res.data.annotated_preview || URL.createObjectURL(file));
        if (res.data.extracted_features) {
          setForm((prev) => ({ ...prev, ...res.data.extracted_features }));
        }
      } catch (fallbackErr) {
        setError("Failed to process urine image. Ensure backend is running.");
      }
    } finally {
      setNeerkuriLoading(false);
    }
  };

  // Handle Neikuri Upload
  const handleNeikuriUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setNeikuriFile(file);
    setNeikuriLoading(true);
    setError(null);

    const fd = new FormData();
    fd.append("file", file);

    try {
      const url = `${apiBase}/api/v1/vision/neikuri`;
      const res = await axios.post(url, fd);
      const data = res.data;
      if (data.annotated_preview_base64) {
        setNeikuriPreview(data.annotated_preview_base64);
      } else {
        setNeikuriPreview(URL.createObjectURL(file));
      }
      setNeikuriQuality(data.quality);

      if (data.extracted_features) {
        setForm((prev) => ({
          ...prev,
          ...data.extracted_features,
        }));
      }
    } catch (err) {
      console.warn("Neikuri vision endpoint failed, attempting fallback:", err);
      try {
        const res = await axios.post(`${apiBase}/upload`, fd);
        setNeikuriPreview(res.data.annotated_preview || URL.createObjectURL(file));
        if (res.data.extracted_features) {
          setForm((prev) => ({ ...prev, ...res.data.extracted_features }));
        }
      } catch (fallbackErr) {
        setError("Failed to process oil-drop image. Ensure backend is running.");
      }
    } finally {
      setNeikuriLoading(false);
    }
  };

  // Run Prediction
  const handlePredict = async () => {
    setPredicting(true);
    setError(null);
    try {
      // First try modular endpoint
      const res = await axios.post(`${apiBase}/api/v1/analysis/predict`, form);
      onResult(res.data);
    } catch (err) {
      console.warn("Modular predict endpoint failed, attempting legacy /predict:", err);
      try {
        const res = await axios.post(`${apiBase}/predict`, form);
        onResult(res.data);
      } catch (fallbackErr) {
        setError("Could not run prediction. Please verify that the backend is running at " + apiBase);
      }
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-ink/10 pb-4">
        <div>
          <h2 className="font-display text-lg font-semibold text-neem">1. Diagnostic Sample Input</h2>
          <p className="text-xs text-ink/60">Digitize photographic samples and verify measured physical parameters</p>
        </div>
        <button
          onClick={() => setForm(DEFAULTS)}
          className="text-xs text-neem hover:underline"
        >
          Reset Defaults
        </button>
      </div>

      {/* Dual Upload Section */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Neerkuri Upload */}
        <div className="border border-ink/10 rounded-xl p-4 bg-clay/30 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-turmeric">A. Neerkuri (Urine Photo)</span>
            {neerkuriLoading && <span className="text-xs text-neem animate-pulse">Extracting CV...</span>}
          </div>
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-turmeric/40 rounded-xl p-3 cursor-pointer hover:bg-turmeric/5 transition">
            <input type="file" accept="image/*" className="hidden" onChange={handleNeerkuriUpload} />
            {neerkuriPreview ? (
              <img src={neerkuriPreview} alt="Neerkuri preview" className="w-full h-32 object-contain rounded-lg" />
            ) : (
              <div className="text-center py-4">
                <span className="text-2xl block mb-1">🧪</span>
                <span className="text-xs font-medium text-ink/70">Upload Urine Sample</span>
                <span className="text-[10px] text-ink/40 block mt-0.5">Measures color, turbidity, foam</span>
              </div>
            )}
          </label>
          {neerkuriQuality && (
            <div className="text-[11px] bg-white rounded-lg p-2 border border-ink/5 flex justify-between items-center">
              <span className="text-ink/60">Quality Score:</span>
              <span className={`font-semibold ${neerkuriQuality.is_acceptable ? 'text-neem' : 'text-highRisk'}`}>
                {neerkuriQuality.quality_score}/100 {neerkuriQuality.is_blurry ? '(Blurry)' : ''}
              </span>
            </div>
          )}
        </div>

        {/* Neikuri Upload */}
        <div className="border border-ink/10 rounded-xl p-4 bg-clay/30 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-neem">B. Neikuri (Oil Drop Photo)</span>
            {neikuriLoading && <span className="text-xs text-neem animate-pulse">Segmenting...</span>}
          </div>
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-neem/40 rounded-xl p-3 cursor-pointer hover:bg-neem/5 transition">
            <input type="file" accept="image/*" className="hidden" onChange={handleNeikuriUpload} />
            {neikuriPreview ? (
              <img src={neikuriPreview} alt="Neikuri preview" className="w-full h-32 object-contain rounded-lg" />
            ) : (
              <div className="text-center py-4">
                <span className="text-2xl block mb-1">💧</span>
                <span className="text-xs font-medium text-ink/70">Upload Oil Drop Photo</span>
                <span className="text-[10px] text-ink/40 block mt-0.5">Extracts boundary, circularity, branches</span>
              </div>
            )}
          </label>
          {neikuriQuality && (
            <div className="text-[11px] bg-white rounded-lg p-2 border border-ink/5 flex justify-between items-center">
              <span className="text-ink/60">Quality Score:</span>
              <span className={`font-semibold ${neikuriQuality.is_acceptable ? 'text-neem' : 'text-highRisk'}`}>
                {neikuriQuality.quality_score}/100 {neikuriQuality.is_blurry ? '(Blurry)' : ''}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Structured Parameter Controls */}
      <div className="space-y-4">
        {/* Section: Demographics & Tridosha */}
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink/50 mb-2">Demographics &amp; Tridosha</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <Field label="Age">
              <input type="number" min="1" max="120" value={form.age} onChange={(e) => update("age", +e.target.value)} className="input" />
            </Field>
            <Field label="Gender">
              <select value={form.gender} onChange={(e) => update("gender", e.target.value)} className="input">
                <option>Male</option><option>Female</option><option>Other</option>
              </select>
            </Field>
            <Field label="Predominant Humor">
              <select value={form.predominant_humor} onChange={(e) => update("predominant_humor", e.target.value)} className="input">
                {HUMORS.map((h) => <option key={h}>{h}</option>)}
              </select>
            </Field>
            <Field label="Vatham / Pitham / Kabham">
              <div className="grid grid-cols-3 gap-1">
                <input type="number" value={form.vatham_score} onChange={(e) => update("vatham_score", +e.target.value)} className="input text-center px-1" title="Vatham %" />
                <input type="number" value={form.pitham_score} onChange={(e) => update("pitham_score", +e.target.value)} className="input text-center px-1" title="Pitham %" />
                <input type="number" value={form.kabham_score} onChange={(e) => update("kabham_score", +e.target.value)} className="input text-center px-1" title="Kabham %" />
              </div>
            </Field>
          </div>
        </div>

        {/* Section: Urine Parameters */}
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink/50 mb-2">Neerkuri (Urine Characteristics)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <Field label="Urine Color">
              <select value={form.urine_color} onChange={(e) => update("urine_color", e.target.value)} className="input">
                {COLORS.map((c) => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="HSV (H / S / V)">
              <div className="grid grid-cols-3 gap-1">
                <input type="number" value={form.HSV_H} onChange={(e) => update("HSV_H", +e.target.value)} className="input text-center px-1" title="Hue" />
                <input type="number" value={form.HSV_S} onChange={(e) => update("HSV_S", +e.target.value)} className="input text-center px-1" title="Saturation" />
                <input type="number" value={form.HSV_V} onChange={(e) => update("HSV_V", +e.target.value)} className="input text-center px-1" title="Value" />
              </div>
            </Field>
            <Field label="Transparency (1-10)">
              <input type="number" step="0.5" min="1" max="10" value={form.transparency_score} onChange={(e) => update("transparency_score", +e.target.value)} className="input" />
            </Field>
            <Field label="Foam %">
              <input type="number" min="0" max="100" value={form.foam_percentage} onChange={(e) => update("foam_percentage", +e.target.value)} className="input" />
            </Field>
            <Field label="Bubble Count">
              <input type="number" value={form.foam_bubble_count} onChange={(e) => update("foam_bubble_count", +e.target.value)} className="input" />
            </Field>
            <Field label="Sediment %">
              <input type="number" min="0" max="100" value={form.sediment_percentage} onChange={(e) => update("sediment_percentage", +e.target.value)} className="input" />
            </Field>
            <Field label="Odor Score (1-10)">
              <input type="number" min="1" max="10" value={form.odor_score} onChange={(e) => update("odor_score", +e.target.value)} className="input" />
            </Field>
          </div>
        </div>

        {/* Section: Oil Drop Pattern */}
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink/50 mb-2">Neikuri (Oil Drop Morphology)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <Field label="Oil Shape">
              <select value={form.oil_shape} onChange={(e) => update("oil_shape", e.target.value)} className="input">
                {OIL_SHAPES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </Field>
            <Field label="Spread Diameter (mm)">
              <input type="number" step="0.5" value={form.oil_spread_diameter_mm} onChange={(e) => update("oil_spread_diameter_mm", +e.target.value)} className="input" />
            </Field>
            <Field label="Expansion Speed (1-10)">
              <input type="number" step="0.1" value={form.oil_spread_speed} onChange={(e) => update("oil_spread_speed", +e.target.value)} className="input" />
            </Field>
            <Field label="Circularity (0.0 - 1.0)">
              <input type="number" step="0.05" min="0.01" max="1.0" value={form.circularity} onChange={(e) => update("circularity", +e.target.value)} className="input" />
            </Field>
            <Field label="Branch Count">
              <input type="number" min="0" max="25" value={form.branch_count} onChange={(e) => update("branch_count", +e.target.value)} className="input" />
            </Field>
            <Field label="Symmetry (1-10)">
              <input type="number" step="0.5" min="1" max="10" value={form.symmetry_score} onChange={(e) => update("symmetry_score", +e.target.value)} className="input" />
            </Field>
            <Field label="Edge Roughness (1-10)">
              <input type="number" step="0.5" min="0" max="15" value={form.edge_roughness} onChange={(e) => update("edge_roughness", +e.target.value)} className="input" />
            </Field>
            <Field label="Fractal Dimension">
              <input type="number" step="0.02" min="1.0" max="2.0" value={form.fractal_dimension} onChange={(e) => update("fractal_dimension", +e.target.value)} className="input" />
            </Field>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-highRisk/10 border border-highRisk/30 text-highRisk text-xs rounded-xl p-3">
          {error}
        </div>
      )}

      <button
        onClick={handlePredict}
        disabled={predicting || neerkuriLoading || neikuriLoading}
        className="w-full bg-neem text-white rounded-xl py-3 font-medium hover:bg-neem/90 transition shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {predicting ? (
          <>
            <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <span>Executing ML Inference &amp; Rule Engine...</span>
          </>
        ) : (
          <span>Run Digital Siddha Analysis</span>
        )}
      </button>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="text-[11px] text-ink/60 block mb-0.5">{label}</span>
      {children}
    </label>
  );
}
