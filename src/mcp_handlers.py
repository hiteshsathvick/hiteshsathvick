"""Shared MCP tool handlers used by both api.py and mcp_server.py."""

import json
import re

from src.data_store import get_df
from src.filters import apply_filters, search_text, paginate
from src.stats import dataset_summary, job_title_distribution, company_distribution


# User-facing columns only (drops internal helpers like phone_normalised, phone_valid)
PUBLIC_COLUMNS = ["name", "email", "phone", "address", "company", "job_title", "text", "description"]


def _public_record(record: dict) -> dict:
    return {k: (str(record[k]) if record.get(k) is not None else None)
            for k in PUBLIC_COLUMNS if k in record}


TOOLS = [
    {
        "name": "search_contacts",
        "description": "Substring search across name, company, job_title and email. Returns paginated results with name, email, phone, address, company, job_title.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term (a name, company, or keyword)"},
                "page": {"type": "integer", "description": "Page number (1-based)", "default": 1},
                "page_size": {"type": "integer", "description": "Records per page (max 100)", "default": 25},
                "include_text": {"type": "boolean", "description": "Include text and description fields", "default": False},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_contact_by_email",
        "description": "Look up a single contact by exact email match. Returns the FULL record with all eight visible fields: name, email, phone, address, company, job_title, text, description. ALWAYS display all eight fields to the user when answering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Email address (case-insensitive)"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "get_contact_by_phone",
        "description": "Look up a single contact by phone number. Accepts any format (+, dashes, parentheses, spaces). Returns the FULL record with all eight visible fields: name, email, phone, address, company, job_title, text, description. ALWAYS display all eight fields to the user when answering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number in any format, e.g. '+1-878-455-2831' or '8784552831'"},
            },
            "required": ["phone"],
        },
    },
    {
        "name": "filter_contacts",
        "description": "Filter contacts by any combination of company, job_title, name_contains, email_contains, has_valid_email, has_valid_phone. Paginated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "job_title": {"type": "string"},
                "name_contains": {"type": "string"},
                "email_contains": {"type": "string"},
                "has_valid_email": {"type": "boolean"},
                "has_valid_phone": {"type": "boolean"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 25},
                "include_text": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "get_job_title_distribution",
        "description": "Return the top-N job titles with counts and percentages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "description": "Number of top job titles to return", "default": 20},
            },
        },
    },
    {
        "name": "get_company_distribution",
        "description": "Return the top-N companies by contact count with percentages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "description": "Number of top companies to return", "default": 20},
            },
        },
    },
    {
        "name": "get_dataset_summary",
        "description": "Aggregate statistics about the dataset: total rows, unique counts per column, valid email/phone counts, duplicate emails, average text/description lengths.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "validate_contacts",
        "description": "Return contacts with invalid email format or non-normalisable phone. Paginated.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 25},
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> dict:
    df = get_df()

    if name == "search_contacts":
        query = args.get("query", "")
        result = search_text(df, query)
        return paginate(
            result,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
            include_text=bool(args.get("include_text", False)),
        )

    if name == "get_contact_by_email":
        email = str(args.get("email", "")).strip().lower()
        if not email:
            return {"error": "email is required"}
        match = df[df["email"] == email]
        if match.empty:
            return {"found": False, "email": email}
        return {"found": True, "record": _public_record(match.iloc[0].to_dict())}

    if name == "get_contact_by_phone":
        raw = str(args.get("phone", ""))
        digits = re.sub(r"\D", "", raw)
        if not digits:
            return {"error": "phone is required"}
        match = df[df["phone_normalised"] == digits]
        if match.empty:
            return {"found": False, "phone": raw, "phone_normalised": digits}
        return {"found": True, "record": _public_record(match.iloc[0].to_dict())}

    if name == "filter_contacts":
        filters = {
            "company": args.get("company"),
            "job_title": args.get("job_title"),
            "name_contains": args.get("name_contains"),
            "email_contains": args.get("email_contains"),
            "has_valid_email": args.get("has_valid_email"),
            "has_valid_phone": args.get("has_valid_phone"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        result = apply_filters(df, filters)
        return paginate(
            result,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
            include_text=bool(args.get("include_text", False)),
        )

    if name == "get_job_title_distribution":
        return job_title_distribution(df, top_n=args.get("top_n", 20))

    if name == "get_company_distribution":
        return company_distribution(df, top_n=args.get("top_n", 20))

    if name == "get_dataset_summary":
        return dataset_summary(df)

    if name == "validate_contacts":
        invalid = df[(~df["email_valid"]) | (~df["phone_valid"])]
        return paginate(
            invalid,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
        )

    return {"error": f"Unknown tool: {name}"}


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
                "serverInfo": {"name": "Contacts MCP", "version": "2.1.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {}) or {}
        result = execute_tool(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result, default=str)}]},
        }

    if method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }
