from src.pipeline import run_query


def main():
    print("Starting Contacts Analysis System...\n")

    queries = [
        "show dataset summary",
        "top job titles",
        "top companies",
        "search for engineer",
        "show invalid contacts",
    ]

    for query in queries:
        print(f"\n--- Query: {query} ---")
        result = run_query(query)
        preview = str(result)
        print(preview[:500] + ("..." if len(preview) > 500 else ""))


if __name__ == "__main__":
    main()
