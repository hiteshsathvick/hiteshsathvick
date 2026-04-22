from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# This ensures src/ is found correctly on Render too
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import run_query

app = FastAPI(
    title="LLM Data Analysis API",
    description="Salary filtering, statistics and prediction via natural language queries",
    version="1.0.0"
)

# ✅ Required for Copilot Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request & Response Models ───

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    result: str


# ─── Routes ───

@app.get("/")
def root():
    return {"status": "ok", "message": "LLM Data Analysis API is running"}


@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    """
    Send a natural language query and get analysis results.

    Example queries:
    - "Predict salary for an employee"
    - "Show average salary in IT department"
    - "Show salary stats for active HR employees"
    """
    try:
        result = run_query(req.query)
        return QueryResponse(
            query=req.query,
            result=str(result)
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="dataset.csv not found. Make sure data/dataset.csv exists."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))