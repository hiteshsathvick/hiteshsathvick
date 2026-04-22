def call_llm(query):
    print("⚠️ Using MOCK LLM (no API)")

    query = query.lower()

    # Prediction case
    if "predict" in query or "prediction" in query:
        return {
            "action": "predict",
            "experience": 5,
            "performance": 4
        }

    # Default stats case
    instruction = {
        "action": "stats",
        "filter": {},
        "target": "Salary"
    }

    if "it" in query:
        instruction["filter"]["Department"] = "IT"
    elif "hr" in query:
        instruction["filter"]["Department"] = "HR"
    elif "finance" in query:
        instruction["filter"]["Department"] = "Finance"

    if "active" in query:
        instruction["filter"]["Status"] = "Active"
    elif "inactive" in query:
        instruction["filter"]["Status"] = "Inactive"

    return instruction