import os
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = """You are an expert user researcher with 10 years experience running product discovery interviews.
Your job is to create a tailored interview script based on the product idea and user profile provided.

Output exactly:
## Interview Goal
One sentence on what we want to learn.

## Screener Questions (3 questions to qualify participants)

## Warm Up Questions (2 questions to make them comfortable)

## Core Questions (8 questions about the problem and current behaviour)

## Deep Dive Questions (4 questions to uncover hidden insights)

## Closing Questions (2 questions to wrap up)

## What to Listen For
3 specific signals that would validate or invalidate the idea.

Make questions open-ended, never leading. Focus on past behaviour not hypothetical."""

def run_interview_generator(phase1_output: dict) -> str:
    context = "PROBLEM: " + str(phase1_output.get("refined_problem","")) + " USER: " + str(phase1_output.get("user_profile",""))
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content":"Create interview script for: " + context}]
    )
    return message.content[0].text
