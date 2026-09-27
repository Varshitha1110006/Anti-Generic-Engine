import { motion } from "framer-motion";
import { ArrowUpRight, Eye } from "lucide-react";

export function IdeaPanel({ draft, onChange, loading, onQuickRead, onBuild, result, locked }) {
  const set = (key) => (e) => onChange({ ...draft, [key]: e.target.value });
  return <div className="workspace-grid">
    <motion.section className="input-panel glass" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .12 }}>
      <div className="panel-head"><div><span className="index">01</span><h2>Place your idea<br /><em>under the lens.</em></h2></div><Eye size={21} className="muted-icon" /></div>
      <label htmlFor="idea-input">RAW MATERIAL / THE UNEDITED THOUGHT</label>
      <textarea id="idea-input" data-testid="idea-input" value={draft.idea} onChange={set("idea")} maxLength={1200} readOnly={locked} placeholder="Write the idea as it exists in your head..." />
      <label htmlFor="audience-input">WHO IS IT FOR / THE HUMAN ON THE OTHER SIDE</label><input id="audience-input" data-testid="audience-input" value={draft.audience} onChange={set("audience")} readOnly={locked} />
      <label htmlFor="constraints-input">NON-NEGOTIABLE / THE SHARP EDGE</label><input id="constraints-input" data-testid="constraints-input" value={draft.constraints} onChange={set("constraints")} readOnly={locked} />
      <div className="input-footer"><span>{draft.idea.length} / 1200</span>
        <div className="action-pair">
          {locked ? <span className="locked-note" data-testid="project-locked-note">SAVED PROJECT · START A NEW ONE TO EDIT</span> : <>
            <button className="secondary-button" onClick={onQuickRead} disabled={loading} data-testid="analyze-idea-button">QUICK READ</button>
            <button className="analyze-button" onClick={onBuild} disabled={loading || draft.idea.trim().length < 3} data-testid="build-brand-system-button">{loading ? "BUILDING..." : "BUILD BRAND SYSTEM"}<ArrowUpRight size={17} /></button></>}
        </div>
      </div>
    </motion.section>
    <motion.section className="signal-panel" initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: .25 }}>
      <div className="orb-wrap"><div className="orb"><div className="orb-core" /><div className="orbit orbit-a" /><div className="orbit orbit-b" /></div><span className="orb-tag">SIGNAL<br />FIELD</span></div>
      <div className="signal-copy"><span className="index">LIVE MODEL</span><h3>{result ? "Your idea has a pulse." : <>Your idea is<br /><em>waiting for a pulse.</em></>}</h3><p>{result ? result.verdict : "Quick Read gives an instant diagnostic. Build Brand System runs all six AI stages and saves the project to your account."}</p></div>
    </motion.section>
  </div>;
}
