from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from typing import Any, Dict
import uuid
import json
import re
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage, TextDelta


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class AnalyzeRequest(BaseModel):
    idea: str

class Signal(BaseModel):
    label: str
    value: int
    note: str

class AnalyzeResponse(BaseModel):
    score: int
    verdict: str
    diagnosis: str
    signals: List[Signal]
    unlocks: List[str]
    distinct_concept: str

class WorkflowRequest(BaseModel):
    idea: str
    audience: str = ""
    constraints: str = ""

class WorkflowResponse(BaseModel):
    id: str
    idea: str
    audience: str
    constraints: str
    stages: List[Dict[str, Any]]
    created_at: str

STAGES = [
    ("understand", "UNDERSTAND", "Extract the core problem, true target user, context, constraints, value and open questions."),
    ("personality", "PERSONALITY", "Choose 3 to 5 brand traits, justify each for the audience, and name traits to avoid."),
    ("challenge", "CHALLENGE GENERIC", "Detect cliches, overused startup patterns and weak assumptions. Replace them with sharper alternatives and explain why."),
    ("visualize", "VISUALIZE", "Translate the strategy into typography, color mood, composition, symbols, imagery and concepts to avoid."),
    ("test", "TEST CONSISTENCY", "Check whether the name, tagline, voice, visuals and launch message behave like one brand. Flag conflicts and revise."),
    ("launch", "LAUNCH", "Create a landing headline, one-line pitch, social launch post and a concise launch checklist without breaking the personality."),
]

async def run_ai_stage(stage_key: str, stage_name: str, brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    system = """You are the Anti Generic Engine, a rigorous brand strategist. You help a founder make better decisions, not receive vague inspiration. Never use filler phrases. Be specific, challenge assumptions, and preserve context from earlier stages. Return ONLY valid JSON with exactly these keys: summary (string), decisions (array of objects with label and value strings), tensions (array of strings), next_question (string)."""
    prompt = f"""STAGE: {stage_name}\nJOB: {brief}\nORIGINAL IDEA: {context.get('idea', '')}\nAUDIENCE: {context.get('audience', '') or 'unknown — infer carefully and mark assumptions'}\nCONSTRAINTS: {context.get('constraints', '') or 'none stated'}\nEARLIER STRUCTURED OUTPUTS: {json.dumps(context.get('stages', []), ensure_ascii=False)}\n\nMake this stage useful enough to guide the next decision. Keep summary under 90 words, decisions to 3-5 items, tensions to 2-4 items. Return JSON only."""
    chat = LlmChat(api_key=os.environ["EMERGENT_LLM_KEY"], session_id=f"anti-generic-{uuid.uuid4()}", system_message=system).with_model("openai", "gpt-5.4")
    chunks = []
    async for event in chat.stream_message(UserMessage(text=prompt)):
        if isinstance(event, TextDelta):
            chunks.append(event.content)
    raw = "".join(chunks).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"summary": raw[:800], "decisions": [], "tensions": ["The model returned an unstructured signal; revisit this stage."], "next_question": "What would make this decision more specific?"}
    return {"key": stage_key, "name": stage_name, **parsed}

@api_router.post("/workflow", response_model=WorkflowResponse)
async def run_workflow(input: WorkflowRequest):
    workflow_id = str(uuid.uuid4())
    context: Dict[str, Any] = {"idea": input.idea.strip(), "audience": input.audience.strip(), "constraints": input.constraints.strip(), "stages": []}
    stages = []
    try:
        for stage_key, stage_name, brief in STAGES:
            stage = await run_ai_stage(stage_key, stage_name, brief, context)
            stages.append(stage)
            context["stages"] = stages
    except Exception as exc:
        logging.exception("AI workflow failed at stage %s", len(stages) + 1)
        raise HTTPException(status_code=503, detail="The reasoning engine could not complete every stage. No partial brand system was saved.") from exc
    created_at = datetime.now(timezone.utc).isoformat()
    doc = {"id": workflow_id, "idea": input.idea, "audience": input.audience, "constraints": input.constraints, "stages": stages, "created_at": created_at}
    await db.workflows.insert_one({**doc})
    return doc

@api_router.get("/workflows", response_model=List[WorkflowResponse])
async def get_workflows():
    docs = await db.workflows.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return docs

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Anti Generic Engine online"}

@api_router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_idea(input: AnalyzeRequest):
    idea = input.idea.strip()
    if not idea:
        return AnalyzeResponse(
            score=0, verdict="Awaiting a signal", diagnosis="Give the engine a raw idea to inspect.",
            signals=[], unlocks=[], distinct_concept=""
        )
    words = idea.lower().split()
    generic_terms = {"platform", "innovative", "seamless", "empower", "revolutionary", "community", "ai", "future"}
    overlap = len(set(words) & generic_terms)
    score = max(18, min(94, 38 + overlap * 9 + min(len(words), 18)))
    verdict = "High signal / low distinction" if score > 62 else "Promising, but familiar"
    signals = [
        Signal(label="Language residue", value=min(96, 42 + overlap * 12), note="Familiar phrasing is doing too much of the explaining."),
        Signal(label="Point of view", value=max(18, 78 - overlap * 10), note="There is a sharper opinion hiding underneath the category words."),
        Signal(label="Tension", value=min(91, 31 + len(words) * 3), note="The most interesting contradiction has not been named yet."),
    ]
    return AnalyzeResponse(
        score=score,
        verdict=verdict,
        diagnosis=f"The idea currently leans on {overlap or 'a few'} familiar category cues. Strip those away and the raw instinct becomes more interesting.",
        signals=signals,
        unlocks=["Name the enemy, not the audience", "Trade features for a ritual", "Make the constraint visible"],
        distinct_concept=f"A sharper version of “{idea[:72]}” built around a visible constraint, a memorable ritual, and one opinion nobody else in the category would claim."
    )

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()