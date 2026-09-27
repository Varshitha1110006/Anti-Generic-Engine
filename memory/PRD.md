# Anti Generic Engine — Product Record

## Original problem statement
“I hope you can understand what I am building.. the Anti Generic Engine.. I am not able to move further because.. That Gemini.. is completely doing mistakes.. I want a beautiful and Extradordinary front end.. the animation.. the 3d.. the alignment.. and Literally everything...Please help me to sort this out”

## Product direction
One guided originality journey: submit a raw idea, understand the generic residue and hidden tension, then move toward a distinctive concept and an originality playground. The visual language is a cinematic dark editorial laboratory with luminous signal fields, tactile glass panels, asymmetric composition, and restrained motion.

## Architecture decisions
- React frontend with Framer Motion, Lucide icons, responsive CSS, and the existing API environment variable.
- FastAPI backend with a deterministic analysis endpoint at `POST /api/analyze`.
- MongoDB connection remains available through the existing configured environment, but analysis does not require persistence yet.
- No authentication or external AI credentials are required for this first product slice.

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

## Prioritized backlog
- P0: Add a submission kit screen with project metadata, contribution details, demo script, and required link checklist.
- P1: Build the Transform and Playground sections as interactive guided stages.
- P1: Add editable signal cards and concept branching so users can compare multiple directions.
- P1: Add a shareable/exportable final brand kit assembled from the six stage outputs.
- P2: Add project history browsing and compare multiple workflow runs.