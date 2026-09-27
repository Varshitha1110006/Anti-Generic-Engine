import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { ArrowUpRight, BrainCircuit, Compass, Eye, Gauge, Menu, RotateCcw, Sparkles, Target, X } from "lucide-react";
import "@/App.css";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const starter = "A space for independent makers to find the right tools without getting lost in the noise.";

function App() {
  const [idea, setIdea] = useState(starter);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const analyze = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    try { const { data } = await axios.post(`${API}/analyze`, { idea }); setResult(data); }
    catch (error) { setResult({ score: 0, verdict: "Engine paused", diagnosis: "The signal could not be reached. Try again in a moment.", signals: [], unlocks: [], distinct_concept: "" }); }
    finally { setLoading(false); }
  };

  return <main className="shell">
    <div className="grain" />
    <aside className={menuOpen ? "sidebar open" : "sidebar"} data-testid="navigation-sidebar">
      <div className="brand"><span className="brand-mark"><span /></span><span>ANTI<br /><em>GENERIC</em></span></div>
      <button className="close-menu" onClick={() => setMenuOpen(false)} data-testid="close-menu-button"><X size={18} /></button>
      <div className="side-label">Workspace / 01</div>
      <nav className="nav-list">
        <button className="nav-item active" data-testid="nav-analyze"><BrainCircuit size={17} /> Analyze <span>01</span></button>
        <button className="nav-item" data-testid="nav-transform"><Sparkles size={17} /> Transform <span>02</span></button>
        <button className="nav-item" data-testid="nav-playground"><Compass size={17} /> Playground <span>03</span></button>
      </nav>
      <div className="sidebar-footer"><div className="status-dot" /> ENGINE ONLINE <span>v0.8</span></div>
    </aside>
    <section className="content">
      <header className="topbar"><button className="menu-button" onClick={() => setMenuOpen(true)} data-testid="open-menu-button"><Menu size={20} /></button><div className="crumb">PROJECT / <strong>UNTITLED SIGNAL</strong></div><div className="top-actions"><span className="save-status">AUTO-SAVED</span><button className="icon-button" data-testid="settings-button"><Gauge size={18} /></button><div className="avatar" data-testid="user-avatar">AG</div></div></header>
      <div className="page-wrap">
        <motion.div className="intro" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7 }}>
          <div className="eyebrow"><span className="eyebrow-line" /> ORIGINALITY / DIAGNOSTICS</div>
          <h1>Make the <i>familiar</i><br /><span>impossible to ignore.</span></h1>
          <p className="lede">A thinking instrument for finding the signal inside an idea —<br className="desktop" /> before the category smooths it out.</p>
        </motion.div>
        <div className="workspace-grid">
          <motion.section className="input-panel glass" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .12 }}>
            <div className="panel-head"><div><span className="index">01</span><h2>Place your idea<br /><em>under the lens.</em></h2></div><Eye size={21} className="muted-icon" /></div>
            <label htmlFor="idea-input">RAW MATERIAL / THE UNEDITED THOUGHT</label>
            <textarea id="idea-input" data-testid="idea-input" value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Write the idea as it exists in your head..." />
            <div className="input-footer"><span>{idea.length} / 500</span><button className="analyze-button" onClick={analyze} disabled={loading} data-testid="analyze-idea-button">{loading ? "READING SIGNAL..." : "RUN DIAGNOSTICS"}<ArrowUpRight size={17} /></button></div>
          </motion.section>
          <motion.section className="signal-panel" initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: .25 }}>
            <div className="orb-wrap"><div className="orb"><div className="orb-core" /><div className="orbit orbit-a" /><div className="orbit orbit-b" /></div><span className="orb-tag">SIGNAL<br />FIELD</span></div>
            <div className="signal-copy"><span className="index">LIVE MODEL</span><h3>{result ? "Your idea has a pulse." : <>Your idea is<br /><em>waiting for a pulse.</em></>}</h3><p>{result ? result.verdict : "Submit a raw thought to map its tension, residue, and point of view."}</p></div>
          </motion.section>
        </div>
        <motion.section className="results-area" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .4 }}>
          <div className="section-heading"><div><span className="eyebrow">{result ? "02 / DIAGNOSTIC REPORT" : "02 / THE DIAGNOSTIC REPORT"}</span><h2>{result ? "Here is what the engine sees." : "Nothing generic survives a closer look."}</h2></div>{result && <button className="reset-button" onClick={() => setResult(null)} data-testid="reset-analysis-button"><RotateCcw size={15} /> RESET</button>}</div>
          {!result ? <div className="empty-report" data-testid="empty-report"><Target size={24} /><span>Run diagnostics to surface the hidden structure of your idea.</span></div> : <div className="report-grid" data-testid="analysis-report"><div className="score-card glass"><span className="index">DISTINCTION INDEX</span><div className="score">{result.score}<small>/100</small></div><div className="score-bar"><span style={{ width: `${result.score}%` }} /></div><p>{result.verdict}</p></div><div className="diagnosis-card glass"><span className="index">THE READ</span><p className="diagnosis">{result.diagnosis}</p><div className="signal-list">{result.signals.map((signal) => <div className="signal-row" key={signal.label}><span>{signal.label}</span><div className="mini-bar"><i style={{ width: `${signal.value}%` }} /></div><b>{signal.value}</b></div>)}</div></div><div className="unlock-card"><span className="index">NEXT UNLOCKS</span>{result.unlocks.map((unlock, i) => <div className="unlock" key={unlock}><span>0{i + 1}</span>{unlock}<ArrowUpRight size={15} /></div>)}</div><div className="concept-card"><span className="index">DISTINCTIVE CONCEPT / GENERATED</span><p>{result.distinct_concept}</p><button data-testid="save-concept-button">SAVE TO PLAYGROUND <ArrowUpRight size={16} /></button></div></div>}
        </motion.section>
      </div>
    </section>
  </main>;
}

export default App;
