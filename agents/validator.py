import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a brutally honest product critic.
Your job is to stress-test a startup idea and find every 
weakness, assumption, and risk before the founder wastes time.

You must identify:
1. The 3 biggest assumptions the founder is making
2. The top 3 risks that could kill this idea
3. Who the real competitors are
4. A final verdict: GO / REFINE / KILL with one sentence reason

Be direct. Be honest. Do not sugarcoat."""

def run_validator(idea: str, research: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Idea: {idea}\n\nResearch findings: {research}"
            }
        ]
    )
    return message.content[0].text
