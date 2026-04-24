from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import Optional
import sys
import os
import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.model import train_model, predict_salary

# Initialize MCP server with stateless mode for Copilot Studio
mcp = FastMCP(
    "LLM Data Analysis MCP",
    stateless_http=True
)

# Load data once at startup
df = pd.read_csv("data/dataset.csv")
trained_model = train_model(df)


@mcp.tool()
def get_salary_stats(
    department: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """
    Get salary statistics for employees.
    Filter by department: IT, HR, Finance.
    Filter by status: Active, Inactive.
    """
    filtered_df = df.copy()
    if department:
        filtered_df = filtered_df[filtered_df["Department"] == department]
    if status:
        filtered_df = filtered_df[filtered_df["Status"] == status]
    if filtered_df.empty:
        return {"error": "No employees found with given filters"}
    return {
        "department": department or "All",
        "status": status or "All",
        "count": int(len(filtered_df)),
        "mean_salary": round(float(filtered_df["Salary"].mean()), 2),
        "max_salary": int(filtered_df["Salary"].max()),
        "min_salary": int(filtered_df["Salary"].min()),
    }


@mcp.tool()
def predict_employee_salary(
    experience_years: int,
    performance_score: int
) -> dict:
    """
    Predict salary for an employee.
    experience_years: number of years of experience.
    performance_score: rating from 1 to 5.
    """
    predicted = predict_salary(trained_model, experience_years, performance_score)
    return {
        "experience_years": experience_years,
        "performance_score": performance_score,
        "predicted_salary": round(predicted, 2),
        "interpretation": (
            f"An employee with {experience_years} years experience "
            f"and performance score {performance_score}/5 "
            f"is estimated to earn Rs.{round(predicted, 2):,.0f}"
        )
    }


@mcp.tool()
def list_employees(
    department: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """
    List all employees optionally filtered by department or status.
    """
    filtered_df = df.copy()
    if department:
        filtered_df = filtered_df[filtered_df["Department"] == department]
    if status:
        filtered_df = filtered_df[filtered_df["Status"] == status]
    employees = filtered_df[[
        "EmployeeName", "Department", "Status",
        "ExperienceYears", "PerformanceScore", "Salary"
    ]].to_dict(orient="records")
    return {"count": len(employees), "employees": employees}


@mcp.tool()
def get_department_summary() -> dict:
    """
    Get a complete summary of all departments with salary stats.
    """
    summary = {}
    for dept in df["Department"].unique():
        dept_df = df[df["Department"] == dept]
        summary[dept] = {
            "employee_count": int(len(dept_df)),
            "avg_salary": round(float(dept_df["Salary"].mean()), 2),
            "max_salary": int(dept_df["Salary"].max()),
            "min_salary": int(dept_df["Salary"].min()),
        }
    return {"department_summary": summary}


# ─── Run standalone ───
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(
        mcp.streamable_http_app(),
        host="0.0.0.0",
        port=port
    )