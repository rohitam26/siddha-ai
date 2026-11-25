import React, { useState } from "react";
import Navbar from "./components/Navbar.jsx";
import UploadPanel from "./components/UploadPanel.jsx";
import RiskCard from "./components/RiskCard.jsx";
import FeatureImportanceChart from "./components/FeatureImportanceChart.jsx";
import PatientReport from "./components/PatientReport.jsx";
import ReportsHistory from "./components/ReportsHistory.jsx";
import ModelInsights from "./components/ModelInsights.jsx";
import SettingsView from "./components/SettingsView.jsx";

const DEFAULT_API_BASE = "http://localhost:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState("console");
  const [apiBase, setApiBase] = useState(
    localStorage.getItem("siddha_api_base") || DEFAULT_API_BASE
  );
  const [result, setResult] = useState(null);
  const [selectedHistoricalReport, setSelectedHistoricalReport] = useState(null);

  const handleSaveApiBase = (url) => {
    setApiBase(url);
    localStorage.setItem("siddha_api_base", url);
  };

  const handleSelectReport = (rep) => {
    setSelectedHistoricalReport(rep);
  };

  return (
    <div className="min-h-screen bg-clay text-ink font-body flex flex-col justify-between">
      <div>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Clinical Research Disclaimer Banner */}
        <div className="bg-turmeric/10 border-b border-turmeric/25 text-turmeric text-xs text-center py-2 px-4 font-medium">
          ⚠️ <strong>Academic Research Platform:</strong> Trained on synthetic baseline distributions. Not certified as a primary medical diagnostic device.
        </div>

        <main className="max-w-6xl mx-auto px-6 py-8">
          {/* TAB 1: CONSOLE */}
          {activeTab === "console" && (
            <div className="space-y-8">
              <div className="grid md:grid-cols-2 gap-8 items-start">
                <section>
                  <UploadPanel apiBase={apiBase} onResult={setResult} />
                </section>

                <section className="space-y-6">
                  {result ? (
                    <>
                      <RiskCard result={result} />
                      <FeatureImportanceChart
                        importances={result.top_feature_importances}
                        shapContributions={result.shap_contributions}
                      />
                    </>
                  ) : (
                    <div className="border-2 border-dashed border-ink/15 rounded-2xl p-12 text-center text-ink/50 space-y-3 bg-white/40">
                      <span className="text-4xl block">🌿</span>
                      <p className="font-display font-medium text-ink/80 text-base">
                        Awaiting Diagnostic Measurements
                      </p>
                      <p className="text-xs text-ink/50 max-w-sm mx-auto">
                        Upload urine or oil-drop photographs, or verify clinical parameters and click 
                        <strong className="text-neem"> Run Digital Siddha Analysis</strong> to evaluate risk patterns and view SHAP local attributions.
                      </p>
                    </div>
                  )}
                </section>
              </div>

              {result && (
                <section className="pt-4">
                  <PatientReport result={result} />
                </section>
              )}
            </div>
          )}

          {/* TAB 2: HISTORY */}
          {activeTab === "history" && (
            <div className="space-y-6">
              <ReportsHistory
                apiBase={apiBase}
                onSelectReport={handleSelectReport}
              />
              {selectedHistoricalReport && (
                <div className="pt-4">
                  <PatientReport
                    result={selectedHistoricalReport}
                    onClose={() => setSelectedHistoricalReport(null)}
                  />
                </div>
              )}
            </div>
          )}

          {/* TAB 3: MODEL INSIGHTS */}
          {activeTab === "insights" && (
            <ModelInsights apiBase={apiBase} />
          )}

          {/* TAB 4: SETTINGS */}
          {activeTab === "settings" && (
            <SettingsView
              apiBase={apiBase}
              onSaveApiBase={handleSaveApiBase}
            />
          )}
        </main>
      </div>

      <footer className="border-t border-ink/10 bg-white/40 text-center text-xs text-ink/40 py-6">
        <p>Siddha AI Research &middot; Digital Neerkuri &amp; Neikuri Diagnostic System &middot; Academic Demonstration</p>
      </footer>
    </div>
  );
}
