import pandas as pd

LIST_PROJECTION = ["name", "email", "phone", "address", "company", "job_title"]
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df
    company = filters.get("company")
    job_title = filters.get("job_title")
    name_contains = filters.get("name_contains")
    email_contains = filters.get("email_contains")
    has_valid_email = filters.get("has_valid_email")
    has_valid_phone = filters.get("has_valid_phone")

    if company:
        out = out[out["company"].str.casefold() == str(company).casefold()]
    if job_title:
        out = out[out["job_title"].str.casefold() == str(job_title).casefold()]
    if name_contains:
        out = out[out["name"].str.contains(str(name_contains), case=False, na=False)]
    if email_contains:
        out = out[out["email"].str.contains(str(email_contains), case=False, na=False)]
    if has_valid_email is not None:
        out = out[out["email_valid"] == bool(has_valid_email)]
    if has_valid_phone is not None:
        out = out[out["phone_valid"] == bool(has_valid_phone)]
    return out


def search_text(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df.iloc[0:0]
    q = str(query).strip()
    if not q:
        return df.iloc[0:0]

    tokens = q.split()
    # Basic plural handling: strip trailing 's' from words longer than 3 chars
    tokens = [t[:-1] if len(t) > 3 and t.endswith("s") else t for t in tokens]
    tokens = [t for t in tokens if t]
    if not tokens:
        return df.iloc[0:0]

    mask = pd.Series(True, index=df.index)
    for token in tokens:
        token_mask = (
            df["name"].str.contains(token, case=False, na=False, regex=False)
            | df["company"].str.contains(token, case=False, na=False, regex=False)
            | df["job_title"].str.contains(token, case=False, na=False, regex=False)
            | df["email"].str.contains(token, case=False, na=False, regex=False)
        )
        mask &= token_mask
    return df[mask]


def paginate(
    df: pd.DataFrame,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    include_text: bool = False,
) -> dict:
    page = max(1, int(page))
    page_size = max(1, min(int(page_size), MAX_PAGE_SIZE))
    total = int(len(df))
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    slice_df = df.iloc[start:end]

    cols = list(LIST_PROJECTION)
    if include_text:
        cols = cols + ["text", "description"]

    available_cols = [c for c in cols if c in slice_df.columns]
    records = slice_df[available_cols].to_dict(orient="records")
    return {
        "total_count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "records": records,
    }
