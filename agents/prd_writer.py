import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = """You are a senior product manager with 10 years experience.
Write a complete professional PRD with these exact sections:
## 1. Executive Summary
## 2. Problem Statement
## 3. Target Users and Personas
## 4. Market Context
## 5. Goals and Success Metrics
## 6. User Stories
## 7. Functional Requirements
## 8. Non-Functional Requirements
## 9. Edge Cases and Risks
## 10. Out of Scope
Be specific and thorough. 800-1200 words total."""
def run_prd_writer(phase1_output: dict) -> str:
    context = "REFINED PROBLEM: " + str(phase1_output.get("refined_problem","")) + " MARKET: " + str(phase1_output.get("market_research","")) + " USERS: " + str(phase1_output.get("user_profile","")) + " VALIDATION: " + str(phase1_output.get("validation",""))
    message = client.messages.create(model="claude-sonnet-4-5", max_tokens=3000, system=SYSTEM_PROMPT, messages=[{"role":"user","content":"Write a complete PRD based on: " + context}])
    return message.content[0].text
