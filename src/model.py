from sklearn.linear_model import LinearRegression

def train_model(df):
    # Features
    X = df[["ExperienceYears", "PerformanceScore"]]
    y = df["Salary"]

    model = LinearRegression()
    model.fit(X, y)

    return model

def predict_salary(model, experience, performance):
    prediction = model.predict([[experience, performance]])
    return float(prediction[0])