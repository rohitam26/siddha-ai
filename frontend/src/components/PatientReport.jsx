import React from "react";

export default function PatientReport({ result, onClose }) {
  const s = result.input_summary || {};

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Siddha_Report_${result.patient_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="bg-white rounded-2xl border border-ink/15 p-8 shadow-sm space-y-6 print:border-none print:shadow-none print:p-0">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-ink/10 pb-5 gap-4">
        <div>
          <span className="text-xs uppercase tracking-widest text-neem font-bold">Ayurvedic &amp; Siddha Examination</span>
          <h2 className="font-display text-2xl font-bold text-ink mt-0.5">Digital Patient Analysis Summary</h2>
          <p className="text-xs text-ink/50 mt-1">
            Standardized physical observations, quantitative proxies, and machine learning risk classification.
          </p>
        </div>
        <div className="flex items-center gap-2 print:hidden">
          <button
            onClick={handleDownloadJSON}
            className="text-xs bg-clay hover:bg-clay/80 text-ink px-3 py-2 rounded-lg font-medium border border-ink/10 transition"
          >
            Export JSON
          </button>
          <button
            onClick={handlePrint}
            className="text-xs bg-neem hover:bg-neem/90 text-white px-4 py-2 rounded-lg font-medium shadow-sm transition"
          >
            Print Report
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-xs text-ink/40 hover:text-ink px-2 py-2"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Patient & Report Metadata */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-clay/30 rounded-xl p-4 text-xs">
        <div>
          <span className="text-ink/50 block">Report Identifier</span>
          <span className="font-mono font-semibold text-ink">{result.patient_id}</span>
        </div>
        <div>
          <span className="text-ink/50 block">Analysis Timestamp</span>
          <span className="font-medium text-ink">{new Date(result.timestamp).toLocaleString()}</span>
        </div>
        <div>
          <span className="text-ink/50 block">Demographics</span>
          <span className="font-medium text-ink">{s.age || "N/A"} yrs / {s.gender || "N/A"}</span>
        </div>
        <div>
          <span className="text-ink/50 block">Predominant Humor</span>
          <span className="font-semibold text-neem">{result.predominant_humor_input}</span>
        </div>
      </div>

      {/* Observation Columns */}
      <div className="grid md:grid-cols-3 gap-6 text-xs">
        <ReportBlock title="Neerkuri (Urine Physicals)">
          <Row k="Visual Color" v={s.urine_color} />
          <Row k="HSV Coordinates" v={`H:${s.HSV_H} · S:${s.HSV_S} · V:${s.HSV_V}`} />
          <Row k="Transparency" v={`${s.transparency_score} / 10`} />
          <Row k="Foam Coverage" v={`${s.foam_percentage}%`} />
          <Row k="Foam Bubble Count" v={s.foam_bubble_count} />
          <Row k="Sediment Level" v={`${s.sediment_percentage}%`} />
          <Row k="Odour Proxy" v={`${s.odor_score} / 10`} />
        </ReportBlock>

        <ReportBlock title="Neikuri (Oil Drop Morphology)">
          <Row k="Classified Shape" v={s.oil_shape} />
          <Row k="Spread Diameter" v={`${s.oil_spread_diameter_mm} mm`} />
          <Row k="Spread Speed Proxy" v={`${s.oil_spread_speed} / 10`} />
          <Row k="Circularity Index" v={s.circularity} />
          <Row k="Convex Branch Count" v={s.branch_count} />
          <Row k="Edge Roughness" v={s.edge_roughness} />
          <Row k="Fractal Dimension" v={s.fractal_dimension} />
        </ReportBlock>

        <ReportBlock title="Tridosha & Risk Profile">
          <Row k="Vatham Humor" v={`${s.vatham_score}%`} />
          <Row k="Pitham Humor" v={`${s.pitham_score}%`} />
          <Row k="Kabham Humor" v={`${s.kabham_score}%`} />
          <Row k="Prototype Risk" v={
            <span className={`font-bold ${result.prototype_risk === "High" ? "text-highRisk" : result.prototype_risk === "Low" ? "text-neem" : "text-turmeric"}`}>
              {result.prototype_risk}
            </span>
          } />
          <Row k="Model Confidence" v={`${(result.confidence * 100).toFixed(1)}%`} />
        </ReportBlock>
      </div>

      {/* Rule Observations List */}
      <div className="border-t border-ink/10 pt-4">
        <p className="text-xs uppercase tracking-wider text-ink/50 font-bold mb-2">
          Deterministic Observation Synthesis
        </p>
        <ul className="text-xs space-y-1.5 bg-clay/20 p-4 rounded-xl border border-ink/5">
          {result.digitized_observations?.map((obs, idx) => (
            <li key={idx} className="flex gap-2">
              <span className="text-neem font-bold">•</span>
              <span className="text-ink/80">{obs}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Disclaimer */}
      <div className="border-t border-ink/10 pt-4 text-[11px] text-highRisk/80">
        <strong>Academic Disclaimer: </strong>
        {result.disclaimer}
      </div>
    </div>
  );
}

function ReportBlock({ title, children }) {
  return (
    <div className="border border-ink/10 rounded-xl p-4 bg-white">
      <p className="text-xs uppercase tracking-wider font-bold text-neem mb-3 border-b border-ink/5 pb-1">
        {title}
      </p>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function Row({ k, v }) {
  return (
    <div className="flex justify-between py-1 border-b border-ink/5">
      <span className="text-ink/60">{k}</span>
      <span className="font-medium text-ink">{v}</span>
    </div>
  );
}
