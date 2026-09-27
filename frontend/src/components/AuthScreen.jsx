import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, Lock } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { apiError } from "@/lib/api";

const steps = ["Drop a raw idea under the lens", "Six AI stages build the brand system", "Keep refining — the engine remembers", "Every project saved to your account"];

export function AuthScreen() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const quickLogin = async (email, password) => {
    setMode("login"); setForm({ ...form, email, password }); setError(""); setBusy(true);
    try { await login(email, password); }
    catch (err) { setError(apiError(err)); }
    finally { setBusy(false); }
  };

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try { mode === "login" ? await login(form.email, form.password) : await register(form.name, form.email, form.password); }
    catch (err) { setError(apiError(err)); }
    finally { setBusy(false); }
  };

  return <main className="auth-shell" data-testid="auth-screen">
    <div className="grain" />
    <motion.section className="auth-hero" initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: .8 }}>
      <div className="brand"><span className="brand-mark"><span /></span><span>ANTI<br /><em>GENERIC</em></span></div>
      <div className="auth-hero-copy">
        <div className="eyebrow"><span className="eyebrow-line" /> BRAND INTELLIGENCE / SIX STAGES</div>
        <h1>Nothing generic<br /><span>survives the lens.</span></h1>
        <ol className="auth-steps">{steps.map((step, i) => <motion.li key={step} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .35 + i * .12 }}><span>0{i + 1}</span>{step}</motion.li>)}</ol>
      </div>
      <div className="orb-wrap auth-orb"><div className="orb"><div className="orb-core" /><div className="orbit orbit-a" /><div className="orbit orbit-b" /></div></div>
    </motion.section>
    <motion.section className="auth-panel" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .2, duration: .7 }}>
      <div className="auth-switch" role="tablist">
        <button className={mode === "login" ? "active" : ""} onClick={() => { setMode("login"); setError(""); }} data-testid="auth-tab-login">SIGN IN</button>
        <button className={mode === "register" ? "active" : ""} onClick={() => { setMode("register"); setError(""); }} data-testid="auth-tab-register">CREATE ACCOUNT</button>
      </div>
      <h2>{mode === "login" ? <>Welcome back.<br /><em>Your projects are waiting.</em></> : <>Start your first<br /><em>brand system.</em></>}</h2>
      <form className="auth-form" onSubmit={submit}>
        {mode === "register" && <label>YOUR NAME<input data-testid="auth-name-input" value={form.name} onChange={set("name")} placeholder="Ada Lovelace" required maxLength={60} /></label>}
        <label>EMAIL<input data-testid="auth-email-input" type="email" value={form.email} onChange={set("email")} placeholder="you@studio.com" required autoComplete="email" /></label>
        <label>PASSWORD<input data-testid="auth-password-input" type="password" value={form.password} onChange={set("password")} placeholder={mode === "register" ? "At least 6 characters" : "••••••••"} required minLength={6} autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
        {error && <p className="auth-error" role="alert" data-testid="auth-error">{error}</p>}
        <button className="analyze-button auth-submit" type="submit" disabled={busy} data-testid="auth-submit-button">{busy ? "OPENING THE LENS..." : mode === "login" ? "ENTER THE STUDIO" : "CREATE MY ACCOUNT"}<ArrowUpRight size={17} /></button>
      </form>
      <div className="judge-access" data-testid="judge-access-card">
        <span className="index">FOR HACKATHON JUDGES / SHARED ACCESS</span>
        <p>No personal account needed. Use the shared judge login to open the saved projects and conversations prepared for review, and try the engine live with a daily allowance.</p>
        <div className="judge-creds"><code data-testid="judge-email">judge@antigeneric.app</code><code data-testid="judge-password">Inkloom-Judge-2026</code></div>
        <button type="button" className="secondary-button judge-button" disabled={busy} onClick={() => quickLogin("judge@antigeneric.app", "Inkloom-Judge-2026")} data-testid="judge-login-button"><Lock size={12} /> ENTER AS JUDGE</button>
      </div>
    </motion.section>
  </main>;
}
