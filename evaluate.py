import pandas as pd
import os
from dotenv import load_dotenv
from core.agent import get_agent, analyze_query

# Assume API key is in environment, or we can't test without it.
# Let's check.
load_dotenv()

# We need to make sure GOOGLE_API_KEY is correctly set for this test.
def test():
    if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
        print("No GOOGLE_API_KEY set.")
        return
    
    df = pd.read_csv("sample_sales_data.csv")
    try:
        agent = get_agent(df)
        res = analyze_query(agent, "What is the total revenue?")
        print("Response:", res)
    except Exception as e:
        print("Error constructing agent:", e)

if __name__ == "__main__":
    test()
