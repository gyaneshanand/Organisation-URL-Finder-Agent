import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Load environment
load_dotenv()

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please add it to your .env file.")

# Define a validator tool (checks page content for keywords)
@tool
def validate_url(url: str) -> str:
    """Fetches the URL and returns text if 'grant' or 'foundation' is found."""
    try:
        import requests
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        r = requests.get(url, timeout=5)
        r.raise_for_status()  # Raise an exception for bad status codes
        txt = r.text.lower()
        return url if ("grant" in txt or "foundation" in txt) else ""
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error validating URL {url}: {e}")
        return ""

# Set up model and tools with enhanced search
llm = ChatOpenAI(temperature=0.1, model="gpt-4")
search_tool = DuckDuckGoSearchRun(max_results=15)  # Increase search results from default 4
tools = [search_tool, validate_url]  # Add validator tool to the tools list

# Custom prompt to guide the agent with multiple search strategies
SYSTEM_PROMPT = """
You are a grant assistant that finds official foundation websites. Given an organization name, you must:

SEARCH STRATEGY (try multiple approaches):
1. Start with search: "[Foundation Name]"
2. First search: "[Foundation Name] official website"
3. If no clear result, try: "[Foundation Name] .org"
4. If still unclear, try: "[Foundation Name] foundation grants"
5. If needed, try variations of the name (e.g., with/without "The", abbreviations)

ANALYSIS CRITERIA:
- Look for URLs that end with .org, .com, or similar domains
- Prioritize results that clearly match the foundation name
- Use the validate_url tool to check if URLs contain foundation/grant content
- Try at least 2-3 different search variations before concluding

OUTPUT: Return ONLY the most reliable URL you find, nothing else.

Focus on finding the main official website, not news articles or other pages about the foundation.
"""

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create agent with increased iterations
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    max_iterations=10,  # Increase from default 15 iterations
    max_execution_time=60  # Set timeout to 60 seconds
)

def find_foundation_url(name: str) -> str:
    # Try multiple search strategies
    search_variations = [
        f"I am looking for the homepage URL of the organization: '{name}'. Please search for the official website and return only the URL.",
        f"Find the official website URL for '{name}' organization. Try multiple search terms if needed.",
        f"Search for '{name}' official site .org domain. Use the validate_url tool to verify any URLs you find."
    ]
    
    for i, prompt_text in enumerate(search_variations):
        try:
            print(f"🔍 Attempt {i+1}: Searching for {name}")
            response = agent_executor.invoke({"input": prompt_text})
            result = response["output"].strip()
            
            # Check if we got a valid URL
            if result.startswith("http") and not ("sorry" in result.lower() or "unable" in result.lower()):
                print(f"✅ Found URL on attempt {i+1}: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Attempt {i+1} failed: {e}")
            continue
    
    return f"Unable to find URL for {name} after multiple attempts"

if __name__ == "__main__":
    name = "The william Penn Foundation"
    url = find_foundation_url(name)
    print(f"✅ Found URL: {url}")
 