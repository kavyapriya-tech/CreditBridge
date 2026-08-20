import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

const RISK_COLORS = {
  Low: "#16a34a",
  Medium: "#d97706",
  High: "#dc2626",
};

export default function History() {
  const [assessments, setAssessments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [listRes, summaryRes] = await Promise.all([
          api.get("/api/assessments"),
          api.get("/api/dashboard/summary"),
        ]);
        setAssessments(listRes.data);
        setSummary(summaryRes.data);
      } catch (err) {
        setError("Could not load history. Check backend is running.");
      }
    }
    load();
  }, []);

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Dashboard</h2>
      <Link to="/">+ New Assessment</Link>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {summary && (
        <div style={{ display: "flex", gap: 16, margin: "20px 0" }}>
          <SummaryCard label="Total" value={summary.total} color="#374151" />
          <SummaryCard label="Low Risk" value={summary.low_risk} color={RISK_COLORS.Low} />
          <SummaryCard label="Medium Risk" value={summary.medium_risk} color={RISK_COLORS.Medium} />
          <SummaryCard label="High Risk" value={summary.high_risk} color={RISK_COLORS.High} />
        </div>
      )}

      <h4>Applicant History</h4>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "2px solid #ddd" }}>
            <th style={{ padding: 8 }}>Name</th>
            <th style={{ padding: 8 }}>Risk Category</th>
            <th style={{ padding: 8 }}>Date</th>
          </tr>
        </thead>
        <tbody>
          {assessments.map((a) => (
            <tr key={a.assessment_id} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: 8 }}>{a.applicant_name}</td>
              <td style={{ padding: 8, color: RISK_COLORS[a.risk_category], fontWeight: "bold" }}>
                {a.risk_category}
              </td>
              <td style={{ padding: 8 }}>{new Date(a.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  return (
    <div style={{ flex: 1, padding: 12, border: `1px solid ${color}`, borderRadius: 8, textAlign: "center" }}>
      <div style={{ fontSize: 24, fontWeight: "bold", color }}>{value}</div>
      <div style={{ fontSize: 12, color: "#555" }}>{label}</div>
    </div>
  );
}