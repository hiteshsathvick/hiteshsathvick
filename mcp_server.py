"""Standalone MCP-only server. Optional — api.py also exposes /mcp now."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_store import load, get_df, reload as reload_store
from src.mcp_handlers import handle_single

# Load data once at startup
load()

app = FastAPI(title="Contacts MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/health")
async def health():
    df = get_df()
    return {"status": "ok", "rows": int(len(df)), "message": "Contacts MCP Server is running"}


@app.post("/reload")
async def trigger_reload():
    info = reload_store()
    return {"status": "reloaded", **info}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    if isinstance(body, list):
        return JSONResponse([handle_single(req) for req in body])
    return JSONResponse(handle_single(body))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
