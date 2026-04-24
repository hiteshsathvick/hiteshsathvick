from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional
import sys
import os
import uvicorn
import json
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.model import train_model, predict_salary

# Load data once
df = pd.read_csv("data/dataset.csv")
trained_model = train_model(df)

app = FastAPI(title="MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Tool Definitions ───
TOOLS = [
    {
        "name": "get_salary_stats",
        "description": "Get salary statistics for employees. Filter by department (IT, HR, Finance) and/or status (Active, Inactive).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department": {"type": "string", "description": "Department name: IT, HR, or Finance"},
                "status": {"type": "string", "description": "Employee status: Active or Inactive"}
            }
        }
    },
    {
        "name": "predict_employee_salary",
        "description": "Predict salary for an employee based on experience years and performance score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "experience_years": {"type": "integer", "description": "Years of experience"},
                "performance_score": {"type": "integer", "description": "Performance score from 1 to 5"}
            },
            "required": ["experience_years", "performance_score"]
        }
    },
    {
        "name": "list_employees",
        "description": "List all employees, optionally filtered by department or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department": {"type": "string", "description": "Department name: IT, HR, or Finance"},
                "status": {"type": "string", "description": "Employee status: Active or Inactive"}
            }
        }
    },
    {
        "name": "get_department_summary",
        "description": "Get a complete salary summary for all departments.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


# ─── Tool Execution ───
def execute_tool(name: str, args: dict) -> dict:
    if name == "get_salary_stats":
        department = args.get("department")
        status = args.get("status")
        filtered_df = df.copy()
        if department:
            filtered_df = filtered_df[filtered_df["Department"] == department]
        if status:
            filtered_df = filtered_df[filtered_df["Status"] == status]
        if filtered_df.empty:
            return {"error": "No employees found"}
        return {
            "department": department or "All",
            "status": status or "All",
            "count": int(len(filtered_df)),
            "mean_salary": round(float(filtered_df["Salary"].mean()), 2),
            "max_salary": int(filtered_df["Salary"].max()),
            "min_salary": int(filtered_df["Salary"].min()),
        }

    elif name == "predict_employee_salary":
        exp = args.get("experience_years", 5)
        perf = args.get("performance_score", 3)
        predicted = predict_salary(trained_model, exp, perf)
        return {
            "experience_years": exp,
            "performance_score": perf,
            "predicted_salary": round(predicted, 2),
            "interpretation": f"Estimated salary: Rs.{round(predicted, 2):,.0f}"
        }

    elif name == "list_employees":
        department = args.get("department")
        status = args.get("status")
        filtered_df = df.copy()
        if department:
            filtered_df = filtered_df[filtered_df["Department"] == department]
        if status:
            filtered_df = filtered_df[filtered_df["Status"] == status]
        employees = filtered_df[[
            "EmployeeName", "Department", "Status",
            "ExperienceYears", "PerformanceScore", "Salary"
        ]].to_dict(orient="records")
        return {"count": len(employees), "employees": employees}

    elif name == "get_department_summary":
        summary = {}
        for dept in df["Department"].unique():
            dept_df = df[df["Department"] == dept]
            summary[dept] = {
                "employee_count": int(len(dept_df)),
                "avg_salary": round(float(dept_df["Salary"].mean()), 2),
                "max_salary": int(dept_df["Salary"].max()),
                "min_salary": int(dept_df["Salary"].min()),
            }
        return {"department_summary": summary}

    return {"error": f"Unknown tool: {name}"}


# ─── Health Check ───
@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok", "message": "MCP Server is running"}


# ─── MCP Endpoint ───
@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()

    # Handle list (array of requests)
    if isinstance(body, list):
        responses = []
        for req in body:
            responses.append(handle_single(req))
        return JSONResponse(responses)

    return JSONResponse(handle_single(body))


def handle_single(req: dict) -> dict:
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "LLM Data Analysis MCP",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        result = execute_tool(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}]
            }
        }

    elif method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }


# ─── Run ───
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)