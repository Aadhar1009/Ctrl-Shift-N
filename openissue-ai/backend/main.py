"""FastAPI backend for OpenIssue AI - GitHub Issue Triage."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import aiosqlite
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analyzer import analyze_issue
from seed_data import seed_vector_store
from vector_store import get_vector_store

# Database path
DB_PATH = "data/history.db"

# Request/Response models
class IssueRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=10000)

class SimilarIssue(BaseModel):
    id: str
    title: str
    body: str
    type: str
    priority: str
    similarity: float

class AnalysisResponse(BaseModel):
    type: str
    type_confidence: float
    priority: str
    priority_score: float
    confidence: float
    similar_issues: list[SimilarIssue]
    explanation: list[str]
    suggested_reply: str

class HistoryItem(BaseModel):
    id: int
    title: str
    body: str
    type: str
    priority: str
    confidence: float
    analyzed_at: str

# Database setup
async def init_db():
    """Initialize SQLite database for history."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                confidence REAL NOT NULL,
                result_json TEXT NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def save_to_history(title: str, body: str, result: dict):
    """Save analysis result to history."""
    import json
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO analysis_history (title, body, type, priority, confidence, result_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, body, result["type"], result["priority"], 
             result["confidence"], json.dumps(result))
        )
        await db.commit()

async def get_history(limit: int = 5) -> list[dict]:
    """Get recent analysis history."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT id, title, body, type, priority, confidence, analyzed_at
               FROM analysis_history ORDER BY analyzed_at DESC LIMIT ?""",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_history_item(item_id: int) -> Optional[dict]:
    """Get a specific history item with full results."""
    import json
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analysis_history WHERE id = ?", (item_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                data["result"] = json.loads(data["result_json"])
                return data
            return None

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    print("🚀 Starting OpenIssue AI...")
    
    # Ensure data directory exists
    import os
    os.makedirs("data", exist_ok=True)
    
    # Initialize database
    await init_db()
    
    # Seed vector store with sample issues
    # Run in thread pool to not block startup
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, seed_vector_store)
    
    print("✅ OpenIssue AI ready!")
    yield
    print("👋 Shutting down OpenIssue AI...")

# Create FastAPI app
app = FastAPI(
    title="OpenIssue AI",
    description="Intelligent GitHub Issue Triage API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OpenIssue AI",
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """Get vector store statistics."""
    store = get_vector_store()
    return store.get_stats()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_issue_endpoint(request: IssueRequest):
    """Analyze a GitHub issue and return triage results."""
    try:
        # Run analysis
        result = await analyze_issue(request.title, request.body)
        
        # Save to history (fire and forget)
        asyncio.create_task(save_to_history(request.title, request.body, result))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_analysis_history(limit: int = 5):
    """Get recent analysis history."""
    history = await get_history(limit)
    return {"history": history}

@app.get("/history/{item_id}")
async def get_history_item_endpoint(item_id: int):
    """Get a specific history item with full results."""
    item = await get_history_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
