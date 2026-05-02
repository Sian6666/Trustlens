import { useState } from "react";
import { LockKeyhole, LogIn, RadioTower, ShieldCheck, UserPlus } from "lucide-react";

import { useAuth } from "../context/AuthContext.jsx";

export function AuthPanel() {
  const [mode, setMode] = useState("signup");
  const [name, setName] = useState("TrustLens Analyst");
  const [email, setEmail] = useState("demo@trustlens.local");
  const [password, setPassword] = useState("trustlens-demo");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, signup } = useAuth();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await signup(name || "TrustLens Analyst", email, password);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="auth-layout">
      <div className="auth-copy">
        <h1>TrustLens</h1>
        <p>Real-time scam intelligence for suspicious messages, community validation, and explainable risk scoring.</p>
        <div className="feature-strip">
          <span><ShieldCheck size={16} /> Explainable detection</span>
          <span><RadioTower size={16} /> Live threat feed</span>
          <span><LockKeyhole size={16} /> Authenticated workflow</span>
        </div>
      </div>
      <form className="panel auth-panel" onSubmit={handleSubmit}>
        <div className="segmented">
          <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
            <LogIn size={16} /> Login
          </button>
          <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>
            <UserPlus size={16} /> Signup
          </button>
        </div>
        {mode === "signup" ? (
          <label>Name<input value={name} onChange={(event) => setName(event.target.value)} /></label>
        ) : null}
        <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" disabled={loading}>{loading ? "Working..." : mode === "login" ? "Login" : "Create account"}</button>
      </form>
    </section>
  );
}
