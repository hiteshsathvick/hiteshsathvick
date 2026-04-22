def apply_filters(df, filters):
    for col, val in filters.items():
        df = df[df[col] == val]
    return df