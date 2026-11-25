import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function FeatureImportanceChart({ importances, shapContributions }) {
  const globalData = Object.entries(importances || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const shapData = Object.entries(shapContributions || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-6 shadow-sm space-y-6">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-display text-lg font-semibold text-neem">
            3. Model Explainability &amp; Attributions
          </h2>
          <span className="text-[10px] bg-neemLight text-neem px-2 py-0.5 rounded font-mono">
            SHAP Engine
          </span>
        </div>
        <p className="text-xs text-ink/60">
          Decomposition of model decision boundary: local per-patient contributions and global Gini feature weightings.
        </p>
      </div>

      {/* Local SHAP Section */}
      {shapContributions ? (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-ink/70">Local Patient Attributions (SHAP Values)</span>
            <div className="flex items-center gap-3 text-[10px]">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 bg-highRisk rounded-sm inline-block"></span>
                <span>Pushes Higher Risk</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 bg-neem rounded-sm inline-block"></span>
                <span>Pushes Lower Risk</span>
              </span>
            </div>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shapData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${val > 0 ? "+" : ""}${val.toFixed(4)}`, "SHAP Impact"]}
                  contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "#E5E7EB" }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {shapData.map((d, i) => (
                    <Cell key={i} fill={d.value >= 0 ? "#B3432B" : "#3F6E52"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-ink/50 italic">
            Positive values shift model confidence toward the predicted risk category; negative values dampen the risk category score.
          </p>
        </div>
      ) : (
        <div className="bg-clay/40 rounded-xl p-4 text-center text-xs text-ink/50">
          Local per-patient SHAP attributions not computed for this sample.
        </div>
      )}

      {/* Global Feature Importance Section */}
      <div className="border-t border-ink/10 pt-4 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="font-semibold text-ink/70">Global Model Feature Importance (Random Forest Gini)</span>
          <span className="text-[10px] text-ink/40">Trained on synthetic distribution</span>
        </div>
        <div className="h-52 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={globalData} layout="vertical" margin={{ left: 10, right: 20 }}>
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(val) => [val.toFixed(4), "Gini Weight"]}
                contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "#E5E7EB" }}
              />
              <Bar dataKey="value" fill="#C98A2C" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
