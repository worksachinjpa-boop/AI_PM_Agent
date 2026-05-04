import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = """You are a brutal but constructive PRD reviewer.
Find every weakness, gap, and ambiguity.
Output exactly:
## PRD Quality Score: X/10
## Critical Issues
## Minor Issues
## What Works Well
## Final Verdict"""
def run_prd_reviewer(prd: str) -> str:
    message = client.messages.create(model="claude-sonnet-4-5", max_tokens=1000, system=SYSTEM_PROMPT, messages=[{"role":"user","content":"Review this PRD: " + prd}])
    return message.content[0].text
