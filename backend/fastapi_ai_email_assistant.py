from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import csv, io, re, os
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = "ai_email_assistant"
COLLECTION = "emails"

app = FastAPI(title="AI Email Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# --- Simple NLP ---
NEG = {"angry","upset","problem","issue","broken","urgent"}
POS = {"thanks","great","love","good","amazing"}
URGENT = {"urgent","immediately","critical","asap"}

def sentiment_score(text: str):
    t = text.lower()
    pos = sum(t.count(w) for w in POS)
    neg = sum(t.count(w) for w in NEG)
    if pos > neg: return "Positive", pos-neg
    elif neg > pos: return "Negative", pos-neg
    return "Neutral", 0

def detect_urgency(text: str):
    return "Urgent" if any(w in text.lower() for w in URGENT) else "Not urgent"

def build_reply(sender, subject, sentiment):
    name = sender.split("@")[0].title()
    if sentiment == "Negative":
        tone = "I’m sorry for the trouble."
    elif sentiment == "Positive":
        tone = "Thanks for the kind words."
    else:
        tone = "Thanks for reaching out."
    return f"Hi {name},\n\n{tone} We reviewed your email about '{subject}'.\n\nBest,\nSupport Team"

class EmailOut(BaseModel):
    id: str
    sender: str
    subject: Optional[str]
    sentiment: Optional[str]
    priority: Optional[str]
    draft_reply: Optional[str]
    status: Optional[str]

@app.post("/ingest_csv")
async def ingest_csv(file: UploadFile = File(...)):
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contents))
    added = 0
    for row in reader:
        doc = {
            "sender": row.get("sender") or "unknown@example.com",
            "subject": row.get("subject") or "",
            "body": row.get("body") or "",
            "received_at": datetime.utcnow(),
            "processed": False,
            "status": "Pending"
        }
        await db[COLLECTION].insert_one(doc)
        added += 1
    return {"status": "ok", "added": added}

@app.post("/process_all")
async def process_all():
    cursor = db[COLLECTION].find({"processed": False})
    count = 0
    async for e in cursor:
        subj, body = e.get("subject",""), e.get("body","")
        sentiment, score = sentiment_score(subj+" "+body)
        priority = detect_urgency(subj+" "+body)
        draft = build_reply(e.get("sender"), subj, sentiment)
        await db[COLLECTION].update_one({"_id": e["_id"]},{
            "$set": {
                "processed": True,
                "sentiment": sentiment,
                "sentiment_score": score,
                "priority": priority,
                "draft_reply": draft
            }
        })
        count += 1
    return {"status": "ok", "processed": count}

@app.get("/emails", response_model=List[EmailOut])
async def list_emails(limit: int = 100):
    cursor = db[COLLECTION].find({"processed": True}).limit(limit)
    results = []
    async for e in cursor:
        results.append(EmailOut(
            id=str(e["_id"]),
            sender=e.get("sender"),
            subject=e.get("subject"),
            sentiment=e.get("sentiment"),
            priority=e.get("priority"),
            draft_reply=e.get("draft_reply"),
            status=e.get("status")
        ))
    return results

@app.post("/emails/{email_id}/send")
async def send_email(email_id: str):
    e = await db[COLLECTION].find_one({"_id": ObjectId(email_id)})
    if not e:
        raise HTTPException(status_code=404, detail="Email not found")
    await db[COLLECTION].update_one({"_id": ObjectId(email_id)}, {"$set": {"status": "Responded"}})
    return {"status": "ok", "id": email_id}
