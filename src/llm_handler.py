import re

STOP_WORDS = {
    "the", "a", "an", "of", "for", "to", "in", "on", "at", "by", "with",
    "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
    "give", "show", "tell", "list", "find", "search", "look", "get", "fetch",
    "me", "us", "my", "our", "i", "we", "you", "your",
    "what", "who", "where", "when", "which", "how", "why",
    "any", "some", "all", "every", "no", "not",
    "this", "that", "these", "those", "it", "its",
    "do", "does", "did", "have", "has", "had",
    "phone", "number", "no", "address", "email", "contact", "contacts",
    "info", "information", "details", "data", "record", "records",
    "person", "people", "many", "much", "there",
    "from", "about", "named", "named",
    "please", "kindly",
}

GENERIC_COUNT_WORDS = {"contacts", "rows", "records", "total", "people", "entries"}


def _tokenise(query: str) -> list[str]:
    """Extract alphanumeric tokens (keeping hyphens within words).
    'no.' -> ['no'], 'amir mccullough' -> ['amir', 'mccullough']
    """
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", query.lower())


def _extract_search_term(query: str) -> str:
    tokens = _tokenise(query)
    tokens = [t for t in tokens if t and t not in STOP_WORDS]
    return " ".join(tokens).strip()


def call_llm(query: str) -> dict:
    """Mock intent parser. Maps a natural-language query to a tool action."""
    print("Using MOCK LLM (no API)")

    q = (query or "").lower().strip()

    if not q:
        return {"action": "summary", "args": {}}

    # Summary: explicit keywords, OR "how many" with a generic noun
    is_how_many_generic = "how many" in q and any(w in q for w in GENERIC_COUNT_WORDS)
    if "summary" in q or "overview" in q or is_how_many_generic:
        return {"action": "summary", "args": {}}

    if "job title" in q or "job-title" in q or "roles" in q or "titles" in q:
        return {"action": "job_distribution", "args": {"top_n": 10}}

    if "company" in q or "companies" in q or "employer" in q:
        return {"action": "company_distribution", "args": {"top_n": 10}}

    if "invalid" in q or "validate" in q or "bad email" in q or "bad phone" in q:
        return {"action": "validate", "args": {"page": 1, "page_size": 25}}

    # Direct email match (e.g. "find foo@bar.com")
    email_match = re.search(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", q)
    if email_match:
        return {"action": "lookup_email", "args": {"email": email_match.group(0)}}

    # Search: extract the meaningful term from longer phrases
    term = _extract_search_term(q)
    if not term:
        return {"action": "summary", "args": {}}

    return {"action": "search", "args": {"query": term, "page": 1, "page_size": 25}}
