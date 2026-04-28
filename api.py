from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import run_query
from src.data_store import load, reload as reload_store
from src.mcp_handlers import handle_single

# Warm the in-memory dataset at startup
load()

app = FastAPI(
    title="Contacts Analysis API",
    description="Filter, search and validate a 15K-row contacts dataset via natural language queries (REST + MCP)",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    result: str


@app.get("/")
def root():
    return {"status": "ok", "message": "Contacts Analysis API is running"}


@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    """
    Example queries:
    - "show dataset summary"
    - "top job titles"
    - "top companies"
    - "search for engineer"
    - "show invalid contacts"
    """
    try:
        result = run_query(req.query)
        return QueryResponse(query=req.query, result=str(result))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload")
def trigger_reload():
    info = reload_store()
    return {"status": "reloaded", **info}


@app.post("/mcp")
async def mcp_handler(request: Request):
    """JSON-RPC 2.0 MCP endpoint exposing 7 contacts-dataset tools."""
    body = await request.json()
    if isinstance(body, list):
        return JSONResponse([handle_single(req) for req in body])
    return JSONResponse(handle_single(body))
