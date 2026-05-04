import os
import anthropic
from dotenv import load_dotenv
from tools.web_search import search_web

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert market research analyst.
Your job is to research a product idea and return a clear, 
structured competitive analysis.

Given raw search results, you must identify:
1. Top 3 existing competitors with their strengths and weaknesses
2. Gaps in the market nobody is filling well
3. Estimated market size (rough is fine)
4. Pricing landscape - what do competitors charge?
5. Your recommendation on market opportunity

Be specific. Use data from the search results provided.
Do not make things up - only use what you find."""

def run_market_researcher(refined_idea: str) -> str:
    """
    Searches the web for market data and competitors,
    then analyses findings using Claude.
    """
    
    # Step 1: Search the web for competitors
    print("   Searching for competitors...")
    search_query = f"competitors alternatives {refined_idea[:100]}"
    competitor_results = search_web(search_query)
    
    # Step 2: Search for market size
    print("   Searching for market size...")
    market_query = f"market size {refined_idea[:80]} industry 2024 2025"
    market_results = search_web(market_query)
    
    # Step 3: Claude analyses the search results
    print("   Analysing findings...")
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Product idea: {refined_idea}

COMPETITOR SEARCH RESULTS:
{competitor_results}

MARKET SIZE SEARCH RESULTS:
{market_results}

Please provide a structured market analysis based on these findings.
"""
            }
        ]
    )
    
    return message.content[0].text
