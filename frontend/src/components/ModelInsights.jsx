import React, { useState, useEffect } from "react";
import axios from "axios";

export default function ModelInsights({ apiBase }) {
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const res = await axios.get(`${apiBase}/api/v1/model/metadata`);
        setMetadata(res.data.metadata);
      } catch (err) {
        console.warn("Could not fetch model metadata:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetadata();
  }, [apiBase]);

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-8 shadow-sm space-y-6">
      <div className="border-b border-ink/10 pb-4">
        <span className="text-xs uppercase tracking-widest text-turmeric font-bold">Model Engineering Architecture</span>
        <h2 className="font-display text-2xl font-bold text-neem mt-1">Machine Learning Evaluation &amp; Benchmarks</h2>
        <p className="text-xs text-ink/60 mt-1">
          Detailed metrics, stratified cross-validation comparisons, and dataset provenance for internship review.
        </p>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-ink/40 animate-pulse">Loading model artifacts...</div>
      ) : metadata ? (
        <div className="space-y-6">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard label="Test Accuracy" value={`${(metadata.metrics?.test_accuracy * 100).toFixed(1)}%`} sub="Held-out 20% test split" />
            <MetricCard label="Balanced Accuracy" value={`${(metadata.metrics?.test_balanced_accuracy * 100).toFixed(1)}%`} sub="Class-imbalance adjusted" />
            <MetricCard label="Macro F1-Score" value={`${metadata.metrics?.test_f1_macro?.toFixed(3)}`} sub="Unweighted mean across classes" />
            <MetricCard label="Multi-Class ROC-AUC" value={`${metadata.metrics?.test_roc_auc_ovr?.toFixed(3)}`} sub="One-vs-Rest area under curve" />
          </div>

          {/* Model Comparison Table */}
          <div className="border border-ink/10 rounded-xl p-5 bg-clay/20 space-y-3">
            <h3 className="font-semibold text-sm text-ink">5-Fold Stratified Cross-Validation Benchmark</h3>
            <p className="text-xs text-ink/60">
              Evaluated during model selection across three algorithmic families with identical preprocessing pipelines:
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-ink/10 text-ink/50 uppercase">
                    <th className="py-2">Algorithm Family</th>
                    <th className="py-2">CV Accuracy (Mean ± Std)</th>
                    <th className="py-2">CV Balanced Acc</th>
                    <th className="py-2">CV Macro F1</th>
                    <th className="py-2">Selected Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink/5">
                  {metadata.cv_benchmark && Object.entries(metadata.cv_benchmark).map(([name, scores]) => (
                    <tr key={name} className={name === metadata.model_type ? "bg-neemLight/40 font-medium" : ""}>
                      <td className="py-2.5 font-semibold text-ink">{name}</td>
                      <td className="py-2.5">{scores.cv_accuracy_mean?.toFixed(3)} ± {scores.cv_accuracy_std?.toFixed(3)}</td>
                      <td className="py-2.5">{scores.cv_balanced_acc_mean?.toFixed(3)}</td>
                      <td className="py-2.5">{scores.cv_f1_macro_mean?.toFixed(3)} ± {scores.cv_f1_macro_std?.toFixed(3)}</td>
                      <td className="py-2.5">
                        {name === metadata.model_type ? (
                          <span className="bg-neem text-white px-2 py-0.5 rounded text-[10px]">Selected &amp; Tuned</span>
                        ) : (
                          <span className="text-ink/40 text-[10px]">Baseline Benchmark</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Dataset Provenance */}
          <div className="grid md:grid-cols-2 gap-4 text-xs">
            <div className="border border-ink/10 rounded-xl p-4 bg-white space-y-2">
              <h4 className="font-semibold text-turmeric uppercase tracking-wider text-[11px]">Dataset &amp; Provenance</h4>
              <ul className="space-y-1 text-ink/70">
                <li>• <strong>Dataset Size:</strong> {metadata.dataset_rows} samples ({metadata.train_rows} train / {metadata.test_rows} test)</li>
                <li>• <strong>SHA-256 Hash:</strong> <code className="bg-clay px-1.5 py-0.5 rounded text-[10px]">{metadata.dataset_hash}</code></li>
                <li>• <strong>Data Modality:</strong> 100% Synthetic research distribution</li>
                <li>• <strong>Leakage Prevention:</strong> StandardScaler &amp; OneHotEncoder fit strictly on CV folds</li>
              </ul>
            </div>
            <div className="border border-ink/10 rounded-xl p-4 bg-white space-y-2">
              <h4 className="font-semibold text-neem uppercase tracking-wider text-[11px]">Tuned Hyperparameters</h4>
              <pre className="bg-clay/50 p-2.5 rounded-lg text-[10px] overflow-x-auto text-ink/80">
                {JSON.stringify(metadata.best_hyperparameters || {}, null, 2)}
              </pre>
            </div>
          </div>

          <div className="text-[11px] text-highRisk/80 bg-highRisk/5 border border-highRisk/20 p-3 rounded-xl">
            <strong>Clinical Integrity Notice: </strong>
            {metadata.disclaimer}
          </div>
        </div>
      ) : (
        <div className="text-xs text-ink/60">Metadata could not be loaded from backend.</div>
      )}
    </div>
  );
}

function MetricCard({ label, value, sub }) {
  return (
    <div className="bg-clay/30 rounded-xl p-4 border border-ink/10 text-center">
      <span className="text-[11px] text-ink/50 uppercase tracking-wider block mb-1 font-semibold">{label}</span>
      <span className="font-display text-2xl font-bold text-neem block">{value}</span>
      <span className="text-[10px] text-ink/40 block mt-0.5">{sub}</span>
    </div>
  );
}
