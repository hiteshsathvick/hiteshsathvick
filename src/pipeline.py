import pandas as pd

from src.llm_handler import call_llm
from src.filters import apply_filters
from src.stats import compute_stats
from src.model import train_model, predict_salary


def run_query(query):
    # Load data
    df = pd.read_csv("data/dataset.csv")

    # Call LLM (mock)
    instruction = call_llm(query)
    print("LLM Output:", instruction)

    if not instruction:
        return "Error in LLM response"

    # 🔮 Prediction
    if instruction["action"] == "predict":
        trained_model = train_model(df)
        return predict_salary(
            trained_model,
            instruction["experience"],
            instruction["performance"]
        )

    # 🔍 Filtering
    if "filter" in instruction:
        df = apply_filters(df, instruction["filter"])

    # 📊 Stats
    if instruction["action"] == "stats":
        return compute_stats(df, instruction["target"])

    return df.head()