import os
import pandas as pd

from src.ingestion import build_parquet, PARQUET_PATH, XLSX_PATH

_df: pd.DataFrame | None = None


def load(force: bool = False) -> pd.DataFrame:
    global _df
    if _df is not None and not force:
        return _df

    if not os.path.exists(PARQUET_PATH) or force:
        build_parquet(XLSX_PATH, PARQUET_PATH)

    _df = pd.read_parquet(PARQUET_PATH)
    return _df


def get_df() -> pd.DataFrame:
    if _df is None:
        return load()
    return _df


def reload() -> dict:
    info = build_parquet(XLSX_PATH, PARQUET_PATH)
    load(force=True)
    return info
