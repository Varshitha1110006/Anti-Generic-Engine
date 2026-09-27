import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Menu, RotateCcw, Target } from "lucide-react";
import { Toaster, toast } from "sonner";
import "@/App.css";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { api, apiError } from "@/lib/api";
import { AuthScreen } from "@/components/AuthScreen";
import { Sidebar } from "@/components/Sidebar";
import { IdeaPanel } from "@/components/IdeaPanel";
import { BuildProgress, StageReport } from "@/components/StageReport";
import { QuickRead } from "@/components/QuickRead";
import { ProjectChat } from "@/components/ProjectChat";
import { SubmissionKit } from "@/components/SubmissionKit";
import { HowItWorks } from "@/components/HowItWorks";

const starterDraft = { idea: "A space for independent makers to find the right tools without getting lost in the noise.", audience: "Independent makers who are tired of same-shaped tools.", constraints: "Must feel opinionated, human, and useful in one sentence." };

function Workspace() {
  const { user } = useAuth();
  const [view, setView] = useState("studio");
  const [menuOpen, setMenuOpen] = useState(false);
  const [draft, setDraft] = useState(starterDraft);
  const [result, setResult] = useState(null);
  const [project, setProject] = useState(null);
  const [activeStage, setActiveStage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [titleDraft, setTitleDraft] = useState("");

  const loadHistory = useCallback(() => api.get("/workflows").then(({ data }) => setHistory(data)).catch(() => {}), []);
  useEffect(() => { loadHistory(); }, [loadHistory]);

  const goStudio = () => { setView("studio"); setMenuOpen(false); };
  const newProject = () => { setProject(null); setResult(null); setDraft(starterDraft); setActiveStage(0); goStudio(); };

  const openProject = async (id) => {
    try { const { data } = await api.get(`/workflows/${id}`); setProject(data); setTitleDraft(data.title); setDraft({ idea: data.idea, audience: data.audience, constraints: data.constraints }); setResult(null); setActiveStage(0); goStudio(); }
    catch (err) { toast.error(apiError(err)); }
  };

  const quickRead = async () => {
    setLoading(true);
    try { const { data } = await api.post("/analyze", { idea: draft.idea }); setResult(data); }
    catch (err) { toast.error(apiError(err)); }
    finally { setLoading(false); }
  };

  const build = async () => {
    setLoading(true); setProject(null); setResult(null);
    try { const { data } = await api.post("/workflow", draft); setProject(data); setTitleDraft(data.title); setActiveStage(0); loadHistory(); toast.success("Brand system saved to your projects."); }
    catch (err) { toast.error(apiError(err, "The six-stage engine is temporarily unavailable. Try again shortly.")); }
    finally { setLoading(false); }
  };

  const deleteProject = async (id) => {
    try { await api.delete(`/workflows/${id}`); if (project?.id === id) newProject(); loadHistory(); toast("Project deleted."); }
    catch (err) { toast.error(apiError(err)); }
  };

  const rename = async () => {
    const title = titleDraft.trim();
    if (!project || !title || title === project.title) { setTitleDraft(project?.title || ""); return; }
    try { await api.patch(`/workflows/${project.id}`, { title }); setProject({ ...project, title }); loadHistory(); }
    catch (err) { toast.error(apiError(err)); }
  };

  const onChatUpdate = (data) => { setProject(data); loadHistory(); };

  return <main className="shell">
    <div className="grain" />
    <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} view={view} onView={(v) => { setView(v); setMenuOpen(false); }} history={history} activeId={project?.id} onOpenProject={openProject} onNewProject={newProject} onDeleteProject={deleteProject} />
    <section className="content">
      <header className="topbar">
        <button className="menu-button" onClick={() => setMenuOpen(true)} data-testid="open-menu-button"><Menu size={20} /></button>
        <div className="crumb">PROJECT / {project ? <input className="title-input" value={titleDraft} onChange={(e) => setTitleDraft(e.target.value)} onBlur={rename} onKeyDown={(e) => e.key === "Enter" && e.target.blur()} maxLength={80} aria-label="Project title" data-testid="project-title-input" /> : <strong data-testid="project-title-draft">NEW DRAFT</strong>}</div>
        <div className="top-actions"><span className="save-status" data-testid="save-status">{project ? "SAVED TO YOUR ACCOUNT" : loading ? "BUILDING..." : "UNSAVED DRAFT"}</span></div>
      </header>
      <div className="page-wrap">
        {view === "guide" && <HowItWorks onStart={goStudio} />}
        {view === "kit" && <SubmissionKit userId={user.id} />}
        {view === "studio" && <>
          <motion.div className="intro" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7 }}>
            <div className="eyebrow"><span className="eyebrow-line" /> ORIGINALITY / DIAGNOSTICS</div>
            <h1>Make the <i>familiar</i><br /><span>impossible to ignore.</span></h1>
            <p className="lede">A thinking instrument for finding the signal inside an idea —<br className="desktop" /> before the category smooths it out.</p>
          </motion.div>
          <IdeaPanel draft={draft} onChange={setDraft} loading={loading} onQuickRead={quickRead} onBuild={build} result={result} locked={Boolean(project)} />
          <motion.section className="results-area" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .4 }}>
            <div className="section-heading"><div><span className="eyebrow">02 / {project ? "SIX-STAGE BRAND SYSTEM" : "THE DIAGNOSTIC REPORT"}</span><h2>{project || result ? "Here is what the engine sees." : "Nothing generic survives a closer look."}</h2></div>{result && !project && <button className="reset-button" onClick={() => setResult(null)} data-testid="reset-analysis-button"><RotateCcw size={15} /> RESET</button>}</div>
            {loading && !result ? <BuildProgress /> : project ? <div className="workflow-report" data-testid="workflow-report"><StageReport stages={project.stages} activeStage={activeStage} onSelect={setActiveStage} /></div> : result ? <QuickRead result={result} onBuild={build} /> : <div className="empty-report" data-testid="empty-report"><Target size={24} /><span>Run a quick read or build the six-stage system to surface the hidden structure of your idea.</span></div>}
          </motion.section>
          {project && <ProjectChat project={project} onUpdate={onChatUpdate} />}
        </>}
      </div>
    </section>
  </main>;
}

function Gate() {
  const { user } = useAuth();
  if (user === null) return <div className="boot" data-testid="boot-screen"><div className="status-dot" /> OPENING THE LENS</div>;
  return user ? <Workspace /> : <AuthScreen />;
}

export default function App() {
  return <AuthProvider><Gate /><Toaster position="bottom-right" theme="dark" toastOptions={{ style: { background: "#101014", border: "1px solid rgba(255,255,255,.11)", color: "#f2f0e9", fontFamily: "DM Mono, monospace", fontSize: 12 } }} /></AuthProvider>;
}
