import { useLocation, useNavigate, Link } from "react-router-dom";

const RISK_COLORS = {
  Low: "#16a34a",
  Medium: "#d97706",
  High: "#dc2626",
};

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  if (!result) {
    return (
      <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
        <p>No result to show.</p>
        <Link to="/">Start a new assessment</Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Assessment Result</h2>
      <p><strong>Applicant:</strong> {result.applicant_name}</p>

      <div
        style={{
          padding: 16,
          borderRadius: 8,
          background: RISK_COLORS[result.risk_category] + "20",
          border: `2px solid ${RISK_COLORS[result.risk_category]}`,
          marginBottom: 20,
        }}
      >
        <h3 style={{ color: RISK_COLORS[result.risk_category], margin: 0 }}>
          {result.risk_category} Risk
        </h3>
        <p style={{ margin: "8px 0 0" }}>
          Probabilities — Low: {(result.probabilities.Low * 100).toFixed(1)}% |
          {" "}Medium: {(result.probabilities.Medium * 100).toFixed(1)}% |
          {" "}High: {(result.probabilities.High * 100).toFixed(1)}%
        </p>
      </div>

      <h4>Top Contributing Factors</h4>
      <ul>
        {result.top_factors.map((f, i) => (
          <li key={i}>
            <strong>{f.factor}</strong> — {f.direction}
          </li>
        ))}
      </ul>

      <p style={{ fontStyle: "italic", color: "#555", marginTop: 20 }}>
        This is a decision-support prototype, not an automated lending decision.
        A human reviewer should evaluate this applicant using this assessment as one input among others.
      </p>

      <button onClick={() => navigate("/")} style={{ marginTop: 12, padding: "8px 16px" }}>
        Assess Another Applicant
      </button>
      {" "}
      <Link to="/history">View History</Link>
    </div>
  );
}