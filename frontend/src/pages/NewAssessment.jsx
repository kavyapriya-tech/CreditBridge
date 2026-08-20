import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const EMPLOYMENT_TYPES = ["salaried", "self_employed", "gig_worker", "unemployed"];

export default function NewAssessment() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    monthly_income: "",
    income_stability_score: "",
    employment_type: "salaried",
    avg_monthly_txn_volatility: "",
    credit_history_months: "",
    utility_payment_consistency: "",
    existing_monthly_debt: "",
    savings_to_income_ratio: "",
    num_dependents: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const payload = {
      ...form,
      monthly_income: parseFloat(form.monthly_income),
      income_stability_score: parseFloat(form.income_stability_score),
      avg_monthly_txn_volatility: parseFloat(form.avg_monthly_txn_volatility),
      credit_history_months: parseInt(form.credit_history_months, 10),
      utility_payment_consistency: parseFloat(form.utility_payment_consistency),
      existing_monthly_debt: parseFloat(form.existing_monthly_debt),
      savings_to_income_ratio: parseFloat(form.savings_to_income_ratio),
      num_dependents: parseInt(form.num_dependents, 10),
    };

    try {
      const res = await api.post("/api/assessments", payload);
      navigate(`/result`, { state: { result: res.data } });
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Check backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>New Applicant Assessment</h2>
      <form onSubmit={handleSubmit}>
        <label>Name / Reference</label>
        <input name="name" value={form.name} onChange={handleChange} required style={inputStyle} />

        <label>Monthly Income (₹)</label>
        <input name="monthly_income" type="number" value={form.monthly_income} onChange={handleChange} required style={inputStyle} />

        <label>Income Stability Score (0–1)</label>
        <input name="income_stability_score" type="number" step="0.01" min="0" max="1" value={form.income_stability_score} onChange={handleChange} required style={inputStyle} />

        <label>Employment Type</label>
        <select name="employment_type" value={form.employment_type} onChange={handleChange} style={inputStyle}>
          {EMPLOYMENT_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <label>Spending Volatility (0–1)</label>
        <input name="avg_monthly_txn_volatility" type="number" step="0.01" min="0" max="1" value={form.avg_monthly_txn_volatility} onChange={handleChange} required style={inputStyle} />

        <label>Credit History (months)</label>
        <input name="credit_history_months" type="number" value={form.credit_history_months} onChange={handleChange} required style={inputStyle} />

        <label>Utility/Rent Payment Consistency (0–1)</label>
        <input name="utility_payment_consistency" type="number" step="0.01" min="0" max="1" value={form.utility_payment_consistency} onChange={handleChange} required style={inputStyle} />

        <label>Existing Monthly Debt (₹)</label>
        <input name="existing_monthly_debt" type="number" value={form.existing_monthly_debt} onChange={handleChange} required style={inputStyle} />

        <label>Savings-to-Income Ratio (0–1)</label>
        <input name="savings_to_income_ratio" type="number" step="0.01" min="0" max="1" value={form.savings_to_income_ratio} onChange={handleChange} required style={inputStyle} />

        <label>Number of Dependents</label>
        <input name="num_dependents" type="number" value={form.num_dependents} onChange={handleChange} required style={inputStyle} />

        {error && <p style={{ color: "red" }}>{error}</p>}

        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? "Assessing..." : "Submit Assessment"}
        </button>
      </form>
    </div>
  );
}

const inputStyle = {
  display: "block",
  width: "100%",
  marginBottom: 12,
  padding: 8,
  boxSizing: "border-box",
};

const buttonStyle = {
  padding: "10px 20px",
  background: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: 6,
  cursor: "pointer",
};