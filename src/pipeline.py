from src.llm_handler import call_llm
from src.data_store import get_df
from src.filters import apply_filters, search_text, paginate
from src.stats import dataset_summary, job_title_distribution, company_distribution


def run_query(query: str):
    df = get_df()
    instruction = call_llm(query)
    print("LLM Output:", instruction)

    action = instruction.get("action")
    args = instruction.get("args", {}) or {}

    if action == "summary":
        return dataset_summary(df)

    if action == "job_distribution":
        return job_title_distribution(df, top_n=args.get("top_n", 10))

    if action == "company_distribution":
        return company_distribution(df, top_n=args.get("top_n", 10))

    if action == "validate":
        invalid = df[(~df["email_valid"]) | (~df["phone_valid"])]
        return paginate(
            invalid,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
        )

    if action == "search":
        result = search_text(df, args.get("query", ""))
        return paginate(
            result,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
        )

    if action == "filter":
        result = apply_filters(df, args.get("filters", {}))
        return paginate(
            result,
            page=args.get("page", 1),
            page_size=args.get("page_size", 25),
        )

    return dataset_summary(df)
