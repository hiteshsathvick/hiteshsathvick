import pandas as pd


def dataset_summary(df: pd.DataFrame) -> dict:
    return {
        "total_rows": int(len(df)),
        "unique_names": int(df["name"].nunique()),
        "unique_emails": int(df["email"].nunique()),
        "unique_companies": int(df["company"].nunique()),
        "unique_job_titles": int(df["job_title"].nunique()),
        "valid_emails": int(df["email_valid"].sum()),
        "valid_phones": int(df["phone_valid"].sum()),
        "duplicate_emails": int(len(df) - df["email"].nunique()),
        "avg_text_length": round(float(df["text"].str.len().mean()), 1),
        "avg_description_length": round(float(df["description"].str.len().mean()), 1),
    }


def job_title_distribution(df: pd.DataFrame, top_n: int = 20) -> dict:
    counts = df["job_title"].value_counts().head(int(top_n))
    total = int(len(df))
    items = [
        {
            "job_title": str(jt),
            "count": int(c),
            "percentage": round(100.0 * int(c) / total, 2),
        }
        for jt, c in counts.items()
    ]
    return {"total_rows": total, "top_n": int(top_n), "distribution": items}


def company_distribution(df: pd.DataFrame, top_n: int = 20) -> dict:
    counts = df["company"].value_counts().head(int(top_n))
    total = int(len(df))
    items = [
        {
            "company": str(c),
            "count": int(n),
            "percentage": round(100.0 * int(n) / total, 2),
        }
        for c, n in counts.items()
    ]
    return {"total_rows": total, "top_n": int(top_n), "distribution": items}
