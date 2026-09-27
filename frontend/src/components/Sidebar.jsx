import { BookOpen, ClipboardList, FlaskConical, LogOut, MessageSquare, Plus, Trash2, X } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const views = [["studio", "Studio", FlaskConical], ["kit", "Submission Kit", ClipboardList], ["guide", "How it works", BookOpen]];

const relative = (iso) => {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

export function Sidebar({ open, onClose, view, onView, history, activeId, onOpenProject, onNewProject, onDeleteProject, canEdit }) {
  const { user, logout } = useAuth();
  const initials = user.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();

  return <aside className={open ? "sidebar open" : "sidebar"} data-testid="navigation-sidebar">
    <div className="brand"><span className="brand-mark"><span /></span><span>ANTI<br /><em>GENERIC</em></span></div>
    <button className="close-menu" onClick={onClose} data-testid="close-menu-button"><X size={18} /></button>
    <button className="new-project" onClick={onNewProject} data-testid="new-project-button"><Plus size={15} /> NEW PROJECT</button>
    <nav className="nav-list">
      {views.map(([key, label, Icon], i) => <button key={key} className={view === key ? "nav-item active" : "nav-item"} onClick={() => onView(key)} data-testid={`nav-${key}`}><Icon size={17} /> {label} <span>0{i + 1}</span></button>)}
    </nav>
    <div className="side-label">Recent projects / {history.length}</div>
    <div className="history-list" data-testid="history-list">
      {history.length === 0 && <p className="history-empty" data-testid="history-empty">Your saved brand systems will appear here. Build one in the Studio.</p>}
      {history.map((item) => <div key={item.id} className={activeId === item.id ? "history-item active" : "history-item"} data-testid={`history-item-${item.id}`}>
        <button className="history-open" onClick={() => onOpenProject(item.id)} data-testid={`history-open-${item.id}`}>
          <strong>{item.title}</strong>
          <span>{item.shared && <em className="shared-tag" data-testid="shared-tag">SHOWCASE</em>}{relative(item.updated_at)}{item.message_count > 0 && <> · <MessageSquare size={9} /> {item.message_count / 2}</>}</span>
        </button>
        {canEdit && !item.shared && <button className="history-delete" onClick={() => onDeleteProject(item.id)} aria-label="Delete project" data-testid={`history-delete-${item.id}`}><Trash2 size={13} /></button>}
      </div>)}
    </div>
    <div className="sidebar-user" data-testid="sidebar-user">
      <div className="avatar">{initials}</div>
      <div className="sidebar-user-copy"><strong data-testid="sidebar-user-name">{user.name}</strong><span data-testid="sidebar-user-role">{user.role === "owner" ? "OWNER · UNLIMITED" : user.role === "judge" ? "JUDGE · VIEW + TRY" : user.email}</span></div>
      <button className="icon-button" onClick={logout} aria-label="Sign out" data-testid="logout-button"><LogOut size={15} /></button>
    </div>
  </aside>;
}
