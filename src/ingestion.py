import os
import pandas as pd

from src.validators import is_valid_email, normalise_phone, is_valid_phone

XLSX_PATH = os.path.join("data", "Third_Excel_15K_Single.xlsx")
PARQUET_PATH = os.path.join("data", "contacts.parquet")

COLUMN_RENAME = {
    "Name": "name",
    "Email": "email",
    "Phone": "phone",
    "Address": "address",
    "Company": "company",
    "Text": "text",
    "Description": "description",
    "Job Title": "job_title",
}


def load_raw(xlsx_path: str = XLSX_PATH) -> pd.DataFrame:
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"Excel file not found: {xlsx_path}")
    return pd.read_excel(xlsx_path)


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_RENAME).copy()

    for col in ["name", "email", "company", "job_title"]:
        df[col] = df[col].astype(str).str.strip()

    df["address"] = df["address"].astype(str).str.replace("\n", ", ", regex=False).str.strip()
    df["email"] = df["email"].str.lower()

    df["phone"] = df["phone"].astype(str)
    df["phone_raw"] = df["phone"]
    df["phone_normalised"] = df["phone_raw"].apply(normalise_phone)
    df["phone_valid"] = df["phone_normalised"].apply(is_valid_phone)
    df["email_valid"] = df["email"].apply(is_valid_email)

    return df


def build_parquet(xlsx_path: str = XLSX_PATH, parquet_path: str = PARQUET_PATH) -> dict:
    df = load_raw(xlsx_path)
    df = normalise(df)
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "valid_emails": int(df["email_valid"].sum()),
        "valid_phones": int(df["phone_valid"].sum()),
        "parquet_path": parquet_path,
    }


if __name__ == "__main__":
    info = build_parquet()
    print(info)
