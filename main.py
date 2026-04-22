from src.pipeline import run_query
 
def main():
    print("🚀 Starting LLM Data Analysis System...\n")
 
    # 🔁 Change this query to test different cases
    query = "Predict salary for an employee"
    # query = "Show average salary in IT department"
    # query = "Show salary stats for active HR employees"
 
    print("Query:", query)
 
    result = run_query(query)
 
    print("\nFinal Result:")
    print(result)
 
 
if __name__ == "__main__":
    main()
 