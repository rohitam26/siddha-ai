import React, { useState } from "react";

export default function SettingsView({ apiBase, onSaveApiBase }) {
  const [endpoint, setEndpoint] = useState(apiBase);
  const [practitioner, setPractitioner] = useState(localStorage.getItem("siddha_practitioner") || "Dr. S. Ramaswamy, B.S.M.S.");
  const [institution, setInstitution] = useState(localStorage.getItem("siddha_institution") || "Siddha Clinical AI Research Lab");
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem("siddha_practitioner", practitioner);
    localStorage.setItem("siddha_institution", institution);
    onSaveApiBase(endpoint);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-8 shadow-sm max-w-2xl mx-auto space-y-6">
      <div className="border-b border-ink/10 pb-4">
        <h2 className="font-display text-2xl font-bold text-neem">User Profile &amp; Settings</h2>
        <p className="text-xs text-ink/60 mt-1">Configure clinical practitioner details, institution header, and API endpoints.</p>
      </div>

      <form onSubmit={handleSave} className="space-y-4 text-xs">
        <div>
          <label className="block text-ink/70 font-semibold mb-1">Practitioner Name</label>
          <input
            type="text"
            value={practitioner}
            onChange={(e) => setPractitioner(e.target.value)}
            className="input"
            placeholder="e.g. Dr. A. Kumar"
          />
        </div>

        <div>
          <label className="block text-ink/70 font-semibold mb-1">Clinic / Institution Name</label>
          <input
            type="text"
            value={institution}
            onChange={(e) => setInstitution(e.target.value)}
            className="input"
            placeholder="e.g. National Institute of Siddha"
          />
        </div>

        <div>
          <label className="block text-ink/70 font-semibold mb-1">FastAPI Backend API Base URL</label>
          <input
            type="text"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            className="input"
            placeholder="http://localhost:8000"
          />
          <span className="text-[10px] text-ink/40 mt-1 block">Default: http://localhost:8000</span>
        </div>

        {saved && (
          <div className="bg-neemLight text-neem border border-neem/20 rounded-lg p-2.5 text-center">
            Settings saved successfully!
          </div>
        )}

        <button
          type="submit"
          className="bg-neem text-white rounded-xl py-2.5 px-6 font-medium hover:bg-neem/90 transition shadow-sm"
        >
          Save Configuration
        </button>
      </form>
    </div>
  );
}
