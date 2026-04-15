import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_agent(df: pd.DataFrame, api_key: str = None):
    """
    Initializes the Langchain Pandas Dataframe Agent with Gemini.
    """
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
        
    if not api_key:
        raise ValueError("API Key is missing. Please provide it in the sidebar or .env.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=api_key,
        temperature=0.1
    )

    try:
        with open("prompts/system_prompt.txt", "r") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are an expert Data Analyst Assistant."

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        prefix=system_prompt,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        agent_type="zero-shot-react-description"
    )
    
    return agent

def analyze_query(agent, query: str):
    """
    Runs the user query through the generative AI agent.
    """
    try:
        response = agent.invoke({"input": query})
        return response.get("output", "I couldn't process this query completely.")
    except Exception as e:
        return f"Agent Analysis Error: {str(e)}"
