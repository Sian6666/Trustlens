import React from "react";
import { createRoot } from "react-dom/client";
import { ShieldCheck } from "lucide-react";

import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import { Dashboard } from "./components/Dashboard.jsx";
import { AuthPanel } from "./components/AuthPanel.jsx";
import "./styles/app.css";

function App() {
  const { user, logout } = useAuth();

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark"><ShieldCheck size={22} /></span>
          <div>
            <strong>TrustLens</strong>
            <small>Scam and misinformation detection</small>
          </div>
        </div>
        {user ? (
          <div className="user-menu">
            <span>{user.name}</span>
            <button className="ghost-button" onClick={logout}>Logout</button>
          </div>
        ) : null}
      </header>
      {user ? <Dashboard /> : <AuthPanel />}
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
