import React from "react";

const RISK_STYLES = {
  Low: {
    bg: "bg-lowRisk/10",
    text: "text-lowRisk",
    border: "border-lowRisk/30",
    badge: "bg-lowRisk text-white",
  },
  Moderate: {
    bg: "bg-modRisk/10",
    text: "text-modRisk",
    border: "border-modRisk/30",
    badge: "bg-modRisk text-white",
  },
  High: {
    bg: "bg-highRisk/10",
    text: "text-highRisk",
    border: "border-highRisk/30",
    badge: "bg-highRisk text-white",
  },
};

export default function RiskCard({ result }) {
  const style = RISK_STYLES[result.prototype_risk] || RISK_STYLES.Moderate;
  const confidencePct = (result.confidence * 100).toFixed(1);

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-6 shadow-sm space-y-5">
      <div className="flex items-center justify-between border-b border-ink/10 pb-3">
        <div>
          <h2 className="font-display text-lg font-semibold text-neem">2. Diagnostic Pattern Synthesis</h2>
          <span className="text-xs text-ink/50">ID: {result.patient_id}</span>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${style.badge}`}>
          {result.prototype_risk} Pattern
        </span>
      </div>

      {/* Primary ML Association Card */}
      <div className={`rounded-xl border ${style.border} ${style.bg} p-5 space-y-3`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-wider text-ink/50 font-semibold">Prototype Risk Category</p>
            <p className={`font-display text-3xl font-bold ${style.text}`}>
              {result.prototype_risk}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase tracking-wider text-ink/50 font-semibold">Prediction Confidence</p>
            <p className="text-2xl font-bold text-ink">{confidencePct}%</p>
          </div>
        </div>

        {/* Confidence progress bar */}
        <div className="w-full bg-ink/10 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              result.prototype_risk === "High" ? "bg-highRisk" : result.prototype_risk === "Low" ? "bg-lowRisk" : "bg-modRisk"
            }`}
            style={{ width: `${confidencePct}%` }}
          ></div>
        </div>
      </div>

      {/* Class Probabilities Distribution */}
      <div>
        <p className="text-xs uppercase tracking-wider text-ink/50 font-semibold mb-2">
          Model Class Probabilities
        </p>
        <div className="grid grid-cols-3 gap-2">
          {Object.entries(result.class_probabilities || {}).map(([cls, prob]) => {
            const pct = (prob * 100).toFixed(1);
            return (
              <div key={cls} className="bg-clay/40 rounded-lg p-2.5 text-center border border-ink/5">
                <span className="text-[11px] text-ink/60 block">{cls}</span>
                <span className="font-semibold text-sm text-ink">{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Transparent Rule-Based Observations */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs uppercase tracking-wider text-ink/50 font-semibold">
            Deterministic Observations (Rule Engine)
          </p>
          <span className="text-[10px] bg-neemLight text-neem px-2 py-0.5 rounded font-mono">
            Deterministic
          </span>
        </div>
        <div className="bg-clay/20 rounded-xl p-3 border border-ink/5 space-y-1.5">
          {result.digitized_observations?.map((obs, i) => (
            <div key={i} className="text-xs flex items-start gap-2 text-ink/80">
              <span className="text-neem font-bold mt-0.5">•</span>
              <span>{obs}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Rule Flags */}
      {result.rule_flags && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {Object.entries(result.rule_flags).map(([flag, active]) => (
            <span
              key={flag}
              className={`text-[10px] px-2 py-1 rounded-md border ${
                active
                  ? "bg-turmeric/10 border-turmeric/30 text-turmeric font-medium"
                  : "bg-ink/5 border-ink/10 text-ink/40"
              }`}
            >
              {active ? "⚠️ " : "✓ "}
              {flag.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      )}

      {/* Clinical Disclaimer Alert */}
      <div className="bg-amberRisk/10 border border-amberRisk/20 rounded-xl p-3 text-[11px] text-ink/70 flex gap-2">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="text-turmeric block font-medium">Research &amp; Demonstration Notice</strong>
          <span>{result.disclaimer}</span>
        </div>
      </div>
    </div>
  );
}
