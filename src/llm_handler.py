def call_llm(query: str) -> dict:
    """Mock intent parser. Maps a natural-language query to one of the new
    contact-dataset tool calls. Returns {"action": <name>, "args": {...}}."""
    print("Using MOCK LLM (no API)")

    q = (query or "").lower().strip()

    if not q:
        return {"action": "summary", "args": {}}

    if "summary" in q or "overview" in q or "how many" in q:
        return {"action": "summary", "args": {}}

    if "job title" in q or "job-title" in q or "roles" in q or "titles" in q:
        return {"action": "job_distribution", "args": {"top_n": 10}}

    if "company" in q or "companies" in q or "employer" in q:
        return {"action": "company_distribution", "args": {"top_n": 10}}

    if "invalid" in q or "validate" in q or "bad email" in q or "bad phone" in q:
        return {"action": "validate", "args": {"page": 1, "page_size": 25}}

    if "search" in q or "find" in q or "look" in q:
        term = q
        for kw in ("search for", "search", "find", "look for", "look up"):
            if kw in term:
                term = term.split(kw, 1)[1].strip(" .?!:'\"")
                break
        return {"action": "search", "args": {"query": term, "page": 1, "page_size": 25}}

    return {"action": "search", "args": {"query": q, "page": 1, "page_size": 25}}
