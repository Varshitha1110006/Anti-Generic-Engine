# Anti Generic Engine — Product Record

## Original problem statement
“I hope you can understand what I am building.. the Anti Generic Engine.. I am not able to move further because.. That Gemini.. is completely doing mistakes.. I want a beautiful and Extradordinary front end.. the animation.. the 3d.. the alignment.. and Literally everything...Please help me to sort this out”

## Product direction
One guided originality journey: submit a raw idea, understand the generic residue and hidden tension, then move toward a distinctive concept and an originality playground. The visual language is a cinematic dark editorial laboratory with luminous signal fields, tactile glass panels, asymmetric composition, and restrained motion.

## Architecture decisions
- React frontend with Framer Motion, Lucide icons, responsive CSS, and the existing API environment variable.
- FastAPI backend with JWT auth (`/api/auth/*`), user-scoped projects (`/api/workflows*`), per-project chat with memory, and a deterministic quick read at `POST /api/analyze`.
- MongoDB collections: `users`, `workflows` (user_id, title, idea, audience, constraints, stages[], messages[], created_at, updated_at), `login_attempts`.
- LLM: Emergent universal key, OpenAI gpt-5.4 via emergentintegrations.

## Implemented
- Replaced the starter splash screen with a complete Anti Generic Engine workspace.
- Added responsive navigation for Analyze, Transform, and Playground directions.
- Added idea input, diagnostics submission, loading state, score, verdict, signal bars, unlocks, and generated distinctive concept.
- Added reset behavior, mobile drawer navigation, motion-safe animation, grain texture, 3D-style signal orb, and responsive layouts.
- Added `data-testid` coverage for core interaction and report elements.
- Added a real six-stage AI workflow using the Emergent universal key and streamed LLM calls: Understand, Personality, Challenge Generic, Visualize, Test Consistency, and Launch.
- Added audience and constraint inputs, structured stage tabs, decisions, tensions, next questions, workflow persistence, and public workflow retrieval.
- Partial AI workflows fail safely with HTTP 503 and are never persisted as complete brand systems.
- Added a hackathon submission kit with project/team identity, repository/live/demo link tracking, demo run-of-show checklist, and Inkloom credit reference.

### 2026-09-27 — Accounts, history and chat memory
- JWT email/password auth (`/app/backend/auth.py`): register, login, me, logout; bcrypt hashing, 5-attempt lockout, idempotent demo user seed (`demo@antigeneric.app / Demo1234!`).
- Projects are scoped to the signed-in user: list (newest first), open, rename, delete. Sidebar shows "Recent projects" like a chat history rail.
- Follow-up chat per project (`POST /api/workflows/{id}/chat`): the engine receives all six stage outputs plus prior messages, replies are persisted, and reload restores the thread.
- Frontend split into components: AuthScreen, Sidebar, IdeaPanel, StageReport (+BuildProgress), QuickRead, ProjectChat, SubmissionKit, HowItWorks; AuthContext + axios client with Bearer token.
- New "How it works" view listing the five features with a 90-second demo path; Submission Kit persists on-device per user.
- Shared judge account `judge@antigeneric.app / Inkloom-Judge-2026` seeded on startup, with a one-click 'Enter as judge' card on the sign-in screen so judges see the prepared projects and chats.
- Roles + daily AI allowance (protects the owner's Universal Key balance): owner unlimited; judge 3 builds + 15 chats/day; registered users 1 build + 5 chats/day; HTTP 429 when exhausted, UI disables the buttons with a clear note. `GET /api/usage` powers the topbar allowance badge.
- Judge account is view-only for rename/delete (403) and sees every owner project as a "SHOWCASE" item in its Recent Projects, so judges land directly on the prepared brand systems and conversations. Owner credentials removed from the sign-in screen.
- Testing: iteration_5 — 13/13 backend, 100% frontend (roles, quotas, showcase, read-only, regression).
- Testing: iteration_4 — 12/12 backend pytest, all frontend flows pass (auth, persistence, history, chat memory, isolation, nav, mobile).

## Prioritized backlog
- P1: Export/share a final brand kit (PDF or public link) assembled from the six stages + chat decisions.
- P1: Editable signal cards and concept branching so users can compare multiple directions.
- P2: Compare two saved projects side by side.
- P2: Password reset via email.