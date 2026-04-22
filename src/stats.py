def compute_stats(df, target):
    return {
        "mean": float(df[target].mean()),
        "max": int(df[target].max()),
        "min": int(df[target].min())
    }