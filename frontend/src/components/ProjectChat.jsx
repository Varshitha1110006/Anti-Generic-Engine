import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { ArrowUp, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";

const suggestions = ["Give me three name options that respect the constraint.", "Rewrite the launch headline in a colder, more precise voice.", "Which decision here is the weakest, and how would you fix it?"];

export function ProjectChat({ project, onUpdate }) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef(null);
  const messages = project.messages || [];

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }); }, [messages.length, busy]);

  const send = async (text) => {
    const content = (text ?? message).trim();
    if (!content || busy) return;
    setBusy(true); setMessage("");
    try { const { data } = await api.post(`/workflows/${project.id}/chat`, { message: content }); onUpdate(data); }
    catch (err) { toast.error(apiError(err)); setMessage(content); }
    finally { setBusy(false); }
  };

  return <section className="project-chat" data-testid="project-chat">
    <div className="section-heading"><div><span className="eyebrow"><MessageSquare size={11} /> 03 / REFINE WITH THE ENGINE</span><h2>Keep the conversation going. It remembers everything.</h2></div><span className="kit-status" data-testid="chat-memory-status">{messages.length / 2} EXCHANGES SAVED</span></div>
    <div className="chat-thread glass" data-testid="chat-thread">
      {messages.length === 0 && <div className="chat-empty" data-testid="chat-empty"><p>The six stages are the starting point. Ask the engine to push, rename, rewrite or defend any decision — every reply builds on the full project memory.</p>
        <div className="chat-suggestions">{suggestions.map((s) => <button key={s} onClick={() => send(s)} disabled={busy} data-testid="chat-suggestion">{s}</button>)}</div></div>}
      {messages.map((m, i) => <motion.div key={i} className={`chat-bubble ${m.role}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} data-testid={`chat-message-${m.role}`}><span className="index">{m.role === "user" ? "YOU" : "ENGINE"}</span><p>{m.content}</p></motion.div>)}
      {busy && <div className="chat-bubble assistant thinking" data-testid="chat-thinking"><span className="index">ENGINE</span><p><i /><i /><i /></p></div>}
      <div ref={endRef} />
    </div>
    <form className="chat-composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
      <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask the engine to refine, rename, or defend a decision..." maxLength={2000} disabled={busy} data-testid="chat-input" />
      <button type="submit" className="analyze-button" disabled={busy || !message.trim()} data-testid="chat-send-button"><ArrowUp size={16} /></button>
    </form>
  </section>;
}
