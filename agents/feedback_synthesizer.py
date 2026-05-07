import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = """You are an expert at synthesizing user feedback and finding patterns.
Given a product idea and existing market research, simulate what user feedback would look like
and identify the key themes, pain points and desires.

Output exactly:
## Top 5 Pain Themes
Each with frequency (High/Medium/Low) and example user quote.

## Top 3 Desire Themes
What users wish existed.

## Surprising Insights
2-3 things that would not be obvious from surface research.

## Sentiment Summary
Overall positive/negative/mixed with reasoning.

## Implications for Product
3 specific product decisions this feedback suggests."""

def run_feedback_synthesizer(phase1_output: dict) -> str:
    context = "PROBLEM: " + str(phase1_output.get("refined_problem","")) + " MARKET: " + str(phase1_output.get("market_research","")) + " USERS: " + str(phase1_output.get("user_profile",""))
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content":"Synthesize user feedback for: " + context}]
    )
    return message.content[0].text
