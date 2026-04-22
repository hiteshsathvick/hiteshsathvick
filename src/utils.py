import json

def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        print("Invalid JSON from LLM")
        return {}