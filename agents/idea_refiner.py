import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert product thinking assistant.
Your single job is to take a rough, vague idea and turn it 
into a crisp structured problem statement.

You must extract and clearly define:
1. The core problem being solved
2. Who specifically has this problem
3. The context when this problem occurs
4. What the user currently does as a workaround
5. Why existing solutions fall short

Be concise. Use plain language. No jargon.
Output a clean structured brief only."""

def run_idea_refiner(raw_idea: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here is my rough idea: {raw_idea}"
            }
        ]
    )
    return message.content[0].text
