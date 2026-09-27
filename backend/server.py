from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone


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