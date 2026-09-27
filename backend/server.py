from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pydantic import BaseModel, Field
from typing import List, Optional
from typing import Any, Dict
import uuid
import json
import re
from datetime import datetime, timezone
from groq import Groq
from auth import build_auth_router, ensure_auth_indexes, seed_demo_user

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")
auth_router, get_current_user = build_auth_router(db)
api_router.include_router(auth_router)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LLM_MODEL = ("openai", "gpt-5.4")


# ---------- Models ----------
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
    idea: str = Field(min_length=3, max_length=1200)
    audience: str = ""
    constraints: str = ""

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str

class WorkflowResponse(BaseModel):
    id: str
    title: str
    idea: str
    audience: str
    constraints: str
    stages: List[Dict[str, Any]]
    messages: List[ChatMessage] = []
    created_at: str
    updated_at: str

class WorkflowSummary(BaseModel):
    id: str
    title: str
    idea: str
    created_at: str
    updated_at: str
    message_count: int
    shared: bool = False

class RenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=80)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


STAGES = [
    ("understand", "UNDERSTAND", "Extract the core problem, true target user, context, constraints, value and open questions."),
    ("personality", "PERSONALITY", "Choose 3 to 5 brand traits, justify each for the audience, and name traits to avoid."),
    ("challenge", "CHALLENGE GENERIC", "Detect cliches, overused startup patterns and weak assumptions. Replace them with sharper alternatives and explain why."),
    ("visualize", "VISUALIZE", "Translate the strategy into typography, color mood, composition, symbols, imagery and concepts to avoid."),
    ("test", "TEST CONSISTENCY", "Check whether the name, tagline, voice, visuals and launch message behave like one brand. Flag conflicts and revise."),
    ("launch", "LAUNCH", "Create a landing headline, one-line pitch, social launch post and a concise launch checklist without breaking the personality."),
]

ENGINE_SYSTEM = "You are the Anti Generic Engine, a rigorous brand strategist. You help a founder make better decisions, not receive vague inspiration. Never use filler phrases. Be specific, challenge assumptions, and preserve context from earlier stages."


async def stream_llm(system: str, prompt: str) -> str:
    client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Map your model to Groq's supported models (e.g., llama-3.3-70b-versatile)
    response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    
    chunks = []
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            chunks.append(delta)
    return "".join(chunks).strip()


async def run_ai_stage(stage_key: str, stage_name: str, brief: str, context: Dict[str, Any]) -> Dict[str, Any]:
    system = ENGINE_SYSTEM + " Return ONLY valid JSON with exactly these keys: summary (string), decisions (array of objects with label and value strings), tensions (array of strings), next_question (string)."
    prompt = f"""STAGE: {stage_name}\nJOB: {brief}\nORIGINAL IDEA: {context.get('idea', '')}\nAUDIENCE: {context.get('audience', '') or 'unknown — infer carefully and mark assumptions'}\nCONSTRAINTS: {context.get('constraints', '') or 'none stated'}\nEARLIER STRUCTURED OUTPUTS: {json.dumps(context.get('stages', []), ensure_ascii=False)}\n\nMake this stage useful enough to guide the next decision. Keep summary under 90 words, decisions to 3-5 items, tensions to 2-4 items. Return JSON only."""
    raw = await stream_llm(system, prompt)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"summary": raw[:800], "decisions": [], "tensions": ["The model returned an unstructured signal; revisit this stage."], "next_question": "What would make this decision more specific?"}
    return {"key": stage_key, "name": stage_name, **parsed}


def make_title(idea: str) -> str:
    words = re.sub(r"\s+", " ", idea.strip()).split(" ")
    title = " ".join(words[:7])
    return (title[:56] + "…") if len(title) > 56 else title


async def visible_user_ids(user: dict) -> List[str]:
    """Judges also see every project prepared by owner accounts (the hackathon showcase)."""
    ids = [user["id"]]
    if user["role"] == "judge":
        owners = await db.users.find({"role": "owner"}, {"_id": 0, "id": 1}).to_list(10)
        ids += [o["id"] for o in owners]
    return ids


async def owned_workflow(workflow_id: str, user: dict) -> dict:
    doc = await db.workflows.find_one({"id": workflow_id, "user_id": {"$in": await visible_user_ids(user)}}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return doc


# ---------- Daily AI allowance (protects the owner's Universal Key balance) ----------
QUOTAS = {"owner": None, "judge": {"build": 3, "chat": 15}, "user": {"build": 1, "chat": 5}}


def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def usage_snapshot(user: dict) -> dict:
    limits = QUOTAS.get(user["role"], QUOTAS["user"])
    record = await db.usage.find_one({"user_id": user["id"], "day": today_key()}, {"_id": 0}) or {}
    return {"role": user["role"], "unlimited": limits is None,
            "builds_used": record.get("build", 0), "builds_limit": None if limits is None else limits["build"],
            "chats_used": record.get("chat", 0), "chats_limit": None if limits is None else limits["chat"],
            "can_edit": user["role"] != "judge"}


async def assert_allowance(user: dict, kind: str):
    limits = QUOTAS.get(user["role"], QUOTAS["user"])
    if limits is None:
        return
    record = await db.usage.find_one({"user_id": user["id"], "day": today_key()}) or {}
    if record.get(kind, 0) >= limits[kind]:
        label = "brand system builds" if kind == "build" else "chat messages"
        raise HTTPException(status_code=429, detail=f"Daily allowance reached: {limits[kind]} {label} per day on this account. Saved projects stay fully viewable; the allowance resets at midnight UTC.")


async def record_usage(user: dict, kind: str):
    if QUOTAS.get(user["role"], QUOTAS["user"]) is None:
        return
    await db.usage.update_one({"user_id": user["id"], "day": today_key()}, {"$inc": {kind: 1}}, upsert=True)


def assert_can_edit(user: dict):
    if user["role"] == "judge":
        raise HTTPException(status_code=403, detail="The judge account is view-only for renaming and deleting projects.")


@api_router.get("/usage")
async def get_usage(user: dict = Depends(get_current_user)):
    return await usage_snapshot(user)


# ---------- Projects ----------
@api_router.post("/workflow", response_model=WorkflowResponse)
async def run_workflow(input: WorkflowRequest, user: dict = Depends(get_current_user)):
    await assert_allowance(user, "build")
    context: Dict[str, Any] = {"idea": input.idea.strip(), "audience": input.audience.strip(), "constraints": input.constraints.strip(), "stages": []}
    stages: List[Dict[str, Any]] = []
    try:
        for stage_key, stage_name, brief in STAGES:
            stage = await run_ai_stage(stage_key, stage_name, brief, context)
            stages.append(stage)
            context["stages"] = stages
    except Exception as exc:
        logging.exception("AI workflow failed at stage %s", len(stages) + 1)
        raise HTTPException(status_code=503, detail="The reasoning engine could not complete every stage. No partial brand system was saved.") from exc
    now = datetime.now(timezone.utc).isoformat()
    doc = {"id": str(uuid.uuid4()), "user_id": user["id"], "title": make_title(input.idea), "idea": input.idea.strip(), "audience": input.audience.strip(), "constraints": input.constraints.strip(), "stages": stages, "messages": [], "created_at": now, "updated_at": now}
    await db.workflows.insert_one({**doc})
    await record_usage(user, "build")
    return doc


@api_router.get("/workflows", response_model=List[WorkflowSummary])
async def list_workflows(user: dict = Depends(get_current_user)):
    docs = await db.workflows.find({"user_id": {"$in": await visible_user_ids(user)}}, {"_id": 0, "id": 1, "user_id": 1, "title": 1, "idea": 1, "created_at": 1, "updated_at": 1, "messages": 1}).sort("updated_at", -1).to_list(100)
    return [{"id": d["id"], "title": d.get("title") or make_title(d["idea"]), "idea": d["idea"], "created_at": d["created_at"], "updated_at": d.get("updated_at", d["created_at"]), "message_count": len(d.get("messages", [])), "shared": d["user_id"] != user["id"]} for d in docs]


@api_router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, user: dict = Depends(get_current_user)):
    doc = await owned_workflow(workflow_id, user)
    doc.setdefault("title", make_title(doc["idea"]))
    doc.setdefault("messages", [])
    doc.setdefault("updated_at", doc["created_at"])
    return doc


@api_router.patch("/workflows/{workflow_id}", response_model=WorkflowSummary)
async def rename_workflow(workflow_id: str, input: RenameRequest, user: dict = Depends(get_current_user)):
    assert_can_edit(user)
    doc = await owned_workflow(workflow_id, user)
    await db.workflows.update_one({"id": workflow_id, "user_id": user["id"]}, {"$set": {"title": input.title.strip()}})
    return {"id": doc["id"], "title": input.title.strip(), "idea": doc["idea"], "created_at": doc["created_at"], "updated_at": doc.get("updated_at", doc["created_at"]), "message_count": len(doc.get("messages", []))}


@api_router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, user: dict = Depends(get_current_user)):
    assert_can_edit(user)
    result = await db.workflows.delete_one({"id": workflow_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}


@api_router.post("/workflows/{workflow_id}/chat", response_model=WorkflowResponse)
async def chat_with_project(workflow_id: str, input: ChatRequest, user: dict = Depends(get_current_user)):
    doc = await owned_workflow(workflow_id, user)
    await assert_allowance(user, "chat")
    history = doc.get("messages", [])
    transcript = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-12:])
    system = ENGINE_SYSTEM + " You are continuing a conversation about ONE brand project. You remember every stage output and every earlier message. Answer in plain prose (no JSON, no markdown headers), under 160 words, and end with one sharp follow-up question when useful."
    prompt = f"""PROJECT TITLE: {doc.get('title', '')}\nIDEA: {doc['idea']}\nAUDIENCE: {doc['audience'] or 'unknown'}\nCONSTRAINTS: {doc['constraints'] or 'none'}\nSIX STAGE OUTPUTS: {json.dumps(doc['stages'], ensure_ascii=False)}\n\nCONVERSATION SO FAR:\n{transcript or '(none yet)'}\n\nUSER: {input.message.strip()}\nASSISTANT:"""
    try:
        reply = await stream_llm(system, prompt)
    except Exception as exc:
        logging.exception("Project chat failed")
        raise HTTPException(status_code=503, detail="The engine could not answer right now. Try again shortly.") from exc
    now = datetime.now(timezone.utc).isoformat()
    new_messages = [{"role": "user", "content": input.message.strip(), "created_at": now}, {"role": "assistant", "content": reply, "created_at": now}]
    await db.workflows.update_one({"id": workflow_id}, {"$push": {"messages": {"$each": new_messages}}, "$set": {"updated_at": now}})
    await record_usage(user, "chat")
    doc["messages"] = history + new_messages
    doc["updated_at"] = now
    doc.setdefault("title", make_title(doc["idea"]))
    return doc


# ---------- Quick read (deterministic, no persistence) ----------
@api_router.get("/")
async def root():
    return {"message": "Anti Generic Engine online"}


@api_router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_idea(input: AnalyzeRequest):
    idea = input.idea.strip()
    if not idea:
        return AnalyzeResponse(score=0, verdict="Awaiting a signal", diagnosis="Give the engine a raw idea to inspect.", signals=[], unlocks=[], distinct_concept="")
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
        score=score, verdict=verdict,
        diagnosis=f"The idea currently leans on {overlap or 'a few'} familiar category cues. Strip those away and the raw instinct becomes more interesting.",
        unlocks=["Name the enemy, not the audience", "Trade features for a ritual", "Make the constraint visible"],
        signals=signals,
        distinct_concept=f"A sharper version of “{idea[:72]}” built around a visible constraint, a memorable ritual, and one opinion nobody else in the category would claim.",
    )


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await ensure_auth_indexes(db)
    await seed_demo_user(db)
    await db.workflows.create_index([("user_id", 1), ("updated_at", -1)])
    await db.usage.create_index([("user_id", 1), ("day", 1)], unique=True)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
