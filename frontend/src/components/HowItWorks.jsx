import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";

const features = [
  ["01", "Quick Read", "An instant diagnostic. Paste a raw idea and get a distinction index, the language residue it leans on, and three unlocks — no waiting, no account data changed."],
  ["02", "Build Brand System", "The core engine. Six AI stages run in sequence, each reading the outputs before it: Understand → Personality → Challenge Generic → Visualize → Test Consistency → Launch."],
  ["03", "Refine with the Engine", "Once a system exists, chat with it. Ask for names, rewrites, or a defence of any decision. The engine keeps the full project memory, exactly like a conversation thread."],
  ["04", "Recent Projects", "Every brand system is saved to your account. Reopen any project from the sidebar to see its stages and the full conversation, rename it, or delete it."],
  ["05", "Submission Kit", "A judge-ready surface for the Inkloom hackathon: project identity, the three required links, and a demo run-of-show checklist that stays filled in on this device."],
];

export function HowItWorks({ onStart }) {
  return <section className="guide" data-testid="how-it-works">
    <div className="section-heading"><div><span className="eyebrow">HOW IT WORKS</span><h2>Five features. One clear path from raw idea to launch.</h2></div></div>
    <div className="guide-grid">
      {features.map(([n, title, body], i) => <motion.article key={n} className="guide-card glass" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * .08 }} data-testid={`guide-card-${n}`}><span className="index">{n}</span><h3>{title}</h3><p>{body}</p></motion.article>)}
      <article className="guide-card demo-card">
        <span className="index">TRY IT IN 90 SECONDS</span>
        <ol><li>Open the Studio and press <b>Build Brand System</b> with the sample idea.</li><li>Click through the six stage tabs while it saves to Recent Projects.</li><li>Ask the engine a follow-up in <b>Refine</b> — then reload the page. Everything is still there.</li></ol>
        <button className="analyze-button" onClick={onStart} data-testid="guide-start-button">GO TO THE STUDIO <ArrowUpRight size={16} /></button>
      </article>
    </div>
  </section>;
}
