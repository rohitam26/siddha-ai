import React from "react";

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "console", label: "Analysis Console", icon: "🔬" },
    { id: "history", label: "Patient History", icon: "📋" },
    { id: "insights", label: "Model Architecture", icon: "📊" },
    { id: "settings", label: "Profile & Settings", icon: "⚙️" },
  ];

  return (
    <header className="border-b border-ink/10 bg-clay/90 backdrop-blur sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-neem text-white flex items-center justify-center font-display text-xl font-bold shadow-sm">
            சி
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-neem leading-tight">
              Siddha AI — Digital Neerkuri &amp; Neikuri
            </h1>
            <p className="text-[11px] text-ink/60">
              Computational Siddha Urine &amp; Oil-Drop Diagnostic Platform
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center gap-1 bg-ink/5 p-1 rounded-xl">
          {tabs.map((t) => {
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  isActive
                    ? "bg-white text-neem shadow-sm font-semibold"
                    : "text-ink/60 hover:text-ink hover:bg-white/50"
                }`}
              >
                <span>{t.icon}</span>
                <span>{t.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
