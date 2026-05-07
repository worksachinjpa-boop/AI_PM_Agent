import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = """You are an expert at building detailed, realistic user personas for product teams.
Create 2 detailed personas based on the research provided.

For each persona output:
## Persona [Number]: [Name]
**Role:** Job title and company size
**Age:** Specific age
**Location:** City and country
**Quote:** One sentence that captures their mindset

### Background
2-3 sentences about their professional life.

### Goals
3 specific professional goals.

### Frustrations
3 specific pain points related to the product space.

### Current Behaviour
How they currently solve the problem (tools, workarounds).

### Decision Factors
What would make them buy/adopt a new solution.

### A Day in Their Life
3-4 sentences describing a typical day showing where the problem occurs.

Make personas feel like real people, not stereotypes."""

def run_persona_builder(phase1_output: dict) -> str:
    context = "PROBLEM: " + str(phase1_output.get("refined_problem","")) + " USERS: " + str(phase1_output.get("user_profile","")) + " MARKET: " + str(phase1_output.get("market_research",""))
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content":"Build user personas for: " + context}]
    )
    return message.content[0].text
