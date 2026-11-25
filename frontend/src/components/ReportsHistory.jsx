import React, { useState, useEffect } from "react";
import axios from "axios";

export default function ReportsHistory({ apiBase, onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [riskFilter, setRiskFilter] = useState("All");

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = riskFilter === "All"
        ? `${apiBase}/api/v1/reports?limit=50`
        : `${apiBase}/api/v1/reports?limit=50&risk_filter=${riskFilter}`;
      const res = await axios.get(url);
      setReports(res.data);
    } catch (err) {
      console.warn("Could not fetch reports history:", err);
      setError("Unable to connect to database. Ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [riskFilter]);

  const handleDelete = async (patientId, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete report ${patientId}?`)) return;
    try {
      await axios.delete(`${apiBase}/api/v1/reports/${patientId}`);
      setReports((prev) => prev.filter((r) => r.patient_id !== patientId));
    } catch (err) {
      alert("Failed to delete report: " + err.message);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-ink/10 p-6 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-ink/10 pb-4 gap-3">
        <div>
          <h2 className="font-display text-lg font-semibold text-neem">Persistent Examination History</h2>
          <p className="text-xs text-ink/60">Search, filter, and inspect previous patient analyses stored in SQLite</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="text-xs rounded-lg border border-ink/15 bg-white px-3 py-1.5 focus:outline-none"
          >
            <option value="All">All Risk Levels</option>
            <option value="Low">Low Risk</option>
            <option value="Moderate">Moderate Risk</option>
            <option value="High">High Risk</option>
          </select>
          <button
            onClick={fetchReports}
            className="text-xs bg-clay hover:bg-clay/80 text-ink px-3 py-1.5 rounded-lg border border-ink/10 transition"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-xs text-ink/50 animate-pulse">
          Loading historical reports from database...
        </div>
      ) : error ? (
        <div className="text-center py-8 text-xs text-highRisk">
          {error}
        </div>
      ) : reports.length === 0 ? (
        <div className="text-center py-12 text-ink/50 text-xs border border-dashed border-ink/15 rounded-xl">
          No records found in database. Run an analysis from the Console to populate history.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-ink/10 text-ink/50 uppercase tracking-wider">
                <th className="py-2.5 px-3">Report ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Demographics</th>
                <th className="py-2.5 px-3">Predominant Humor</th>
                <th className="py-2.5 px-3">Prototype Risk</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink/5">
              {reports.map((r) => {
                const s = r.input_summary || {};
                const badgeColor =
                  r.prototype_risk === "High"
                    ? "bg-highRisk/10 text-highRisk border-highRisk/30"
                    : r.prototype_risk === "Low"
                    ? "bg-lowRisk/10 text-lowRisk border-lowRisk/30"
                    : "bg-modRisk/10 text-modRisk border-modRisk/30";

                return (
                  <tr
                    key={r.patient_id}
                    onClick={() => onSelectReport(r)}
                    className="hover:bg-neemLight/30 cursor-pointer transition"
                  >
                    <td className="py-3 px-3 font-mono font-semibold text-neem">
                      {r.patient_id}
                    </td>
                    <td className="py-3 px-3 text-ink/60">
                      {new Date(r.timestamp).toLocaleDateString()} {new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-3 text-ink/80">
                      {s.age || "N/A"} yrs / {s.gender || "N/A"}
                    </td>
                    <td className="py-3 px-3 font-medium text-ink">
                      {r.predominant_humor_input}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] border font-medium ${badgeColor}`}>
                        {r.prototype_risk}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-ink">
                      {(r.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={(e) => handleDelete(r.patient_id, e)}
                        className="text-ink/30 hover:text-highRisk p-1 text-sm transition"
                        title="Delete report"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
