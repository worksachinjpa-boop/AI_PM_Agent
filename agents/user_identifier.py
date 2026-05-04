import os
import anthropic
from dotenv import load_dotenv
from tools.web_search import search_web

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a user research specialist.
Your job is to find real people who have the problem 
described in the product idea, using evidence from the web.

From the search results provided, extract:
1. Who specifically has this pain (job title, situation, context)
2. Real quotes or complaints from actual users if found
3. How often this pain occurs
4. What they currently do to solve it
5. How much this pain costs them (time or money)

Be specific. Use real evidence from search results.
If you find actual user quotes, include them."""

def run_user_identifier(refined_idea: str) -> str:
    """
    Searches Reddit, forums and reviews to find
    real people experiencing the problem.
    """
    
    # Search Reddit and forums for real user pain
    print("   Searching for user pain on Reddit...")
    reddit_query = f"reddit {refined_idea[:80]} problem frustration"
    reddit_results = search_web(reddit_query)
    
    # Search for reviews mentioning the problem
    print("   Searching reviews and forums...")
    review_query = f"users complain about {refined_idea[:80]} pain point"
    review_results = search_web(review_query)
    
    # Claude analyses who the real users are
    print("   Building user profile...")
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""
Product idea: {refined_idea}

REDDIT AND FORUM RESULTS:
{reddit_results}

REVIEW AND COMPLAINT RESULTS:
{review_results}

Who are the real users experiencing this pain?
"""
            }
        ]
    )
    
    return message.content[0].text
