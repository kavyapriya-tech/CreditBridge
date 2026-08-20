import { useState } from "react";
import { useNavigate } from "react-router-dom";

const DEMO_USERNAME = "reviewer";
const DEMO_PASSWORD = "creditbridge2026";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (username === DEMO_USERNAME && password === DEMO_PASSWORD) {
      sessionStorage.setItem("cb_logged_in", "true");
      navigate("/");
    } else {
      setError("Invalid username or password.");
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "80px auto", fontFamily: "sans-serif" }}>
      <h2>CreditBridge — Reviewer Login</h2>
      <form onSubmit={handleSubmit}>
        <label>Username</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
          required
        />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
          required
        />
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit" style={buttonStyle}>Log In</button>
      </form>
      <p style={{ fontSize: 12, color: "#777", marginTop: 12 }}>
        Demo credentials: reviewer / creditbridge2026
      </p>
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