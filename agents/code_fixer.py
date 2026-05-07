import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert Python debugger.
You are given code files that have errors and the specific errors found.
Fix ONLY the files that have errors. Return the complete fixed file content.

Output format — use exactly these markers for each fixed file:

===FILE: filename.py===
[complete fixed file content]

Only output files that needed fixing. No explanations."""

def run_code_fixer(app_dir: str, errors: list) -> dict:
    """
    Takes files with errors and fixes them using Claude.
    Returns dict of fixed files.
    """
    if not errors:
        return {}
    
    # Read the broken files
    error_context = ""
    for error in errors:
        filepath = f"{app_dir}/{error['file']}"
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            error_context += f"\n===FILE: {error['file']}===\n{content}\n"
            error_context += f"\nERROR IN {error['file']}:\n{error['error']}\n"
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Fix these errors:\n{error_context}"
        }]
    )
    
    # Parse fixed files
    from agents.code_generator import parse_generated_files, save_generated_files
    fixed_files = parse_generated_files(message.content[0].text)
    
    # Save fixed files
    for filename, content in fixed_files.items():
        filepath = f"{app_dir}/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
    
    return fixed_files
