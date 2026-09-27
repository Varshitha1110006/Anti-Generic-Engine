import { useEffect, useState } from "react";

const defaults = { projectName: "Anti Generic Engine", teamName: "Untitled Signal", links: { repo: "", live: "", demo: "" }, checks: [false, false, false, false, false] };
const runOfShow = ["State the user and the genericity problem", "Enter a realistic idea with audience + constraint", "Walk through all six structured stages", "Highlight the Challenge Generic stage", "Show the launch-ready output and decision value"];

export function SubmissionKit({ userId }) {
  const storageKey = `age_kit_${userId}`;
  const [kit, setKit] = useState(() => { try { return { ...defaults, ...JSON.parse(localStorage.getItem(storageKey) || "{}") }; } catch { return defaults; } });
  useEffect(() => { localStorage.setItem(storageKey, JSON.stringify(kit)); }, [kit, storageKey]);
  const ready = Object.values(kit.links).filter(Boolean).length;

  return <section className="submission-kit" data-testid="submission-kit">
    <div className="section-heading"><div><span className="eyebrow">HACKATHON SUBMISSION KIT</span><h2>Make the work easy to judge.</h2></div><span className="kit-status" data-testid="submission-kit-status">{ready} / 3 LINKS READY</span></div>
    <div className="kit-grid">
      <div className="kit-card glass"><span className="index">PROJECT IDENTITY</span>
        <label>PROJECT NAME<input data-testid="project-name-input" value={kit.projectName} onChange={(e) => setKit({ ...kit, projectName: e.target.value })} /></label>
        <label>TEAM NAME<input data-testid="team-name-input" value={kit.teamName} onChange={(e) => setKit({ ...kit, teamName: e.target.value })} /></label>
        <p className="kit-description">{kit.projectName} — a six-stage AI brand intelligence workflow that challenges generic thinking before it ships.</p></div>
      <div className="kit-card glass"><span className="index">REQUIRED LINKS</span>
        {[["repo", "PUBLIC REPOSITORY"], ["live", "LIVE PRODUCT"], ["demo", "2–4 MINUTE DEMO VIDEO"]].map(([key, label]) => <label key={key}>{label}<input data-testid={`${key}-link-input`} placeholder="Paste link when ready" value={kit.links[key]} onChange={(e) => setKit({ ...kit, links: { ...kit.links, [key]: e.target.value } })} /></label>)}</div>
      <div className="kit-card checklist-card"><span className="index">DEMO RUN OF SHOW</span>
        {runOfShow.map((item, index) => <label className="check-row" key={item}><input type="checkbox" checked={kit.checks[index]} onChange={(e) => setKit({ ...kit, checks: kit.checks.map((c, i) => i === index ? e.target.checked : c) })} data-testid={`demo-check-${index + 1}`} /> <span>{item}</span></label>)}
        <p className="inkloom-note">INKLOOM / EARLY ACCESS CODE <strong>INKLOOM-WCC</strong> · inkloom.art</p></div>
    </div>
  </section>;
}
