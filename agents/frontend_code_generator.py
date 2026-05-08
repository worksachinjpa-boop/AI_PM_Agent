import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert frontend developer.
Generate a complete, working, single-file HTML frontend application.

CRITICAL RULES:
1. Single file only — all CSS and JS inside one HTML file
2. No external dependencies except CDN links
3. Use fetch() to call the backend API
4. Must be fully functional — no placeholders
5. Include proper error handling
6. Mobile responsive using CSS flexbox/grid
7. Dark theme UI matching modern SaaS apps
8. All API calls go to /api/ endpoints
9. Store JWT token in localStorage
10. Show loading states during API calls

Output format — use exactly this marker:

===FILE: index.html===
[complete single file HTML content]

Generate clean, working code. No explanations outside file markers."""

def run_frontend_code_generator(frontend_spec: str, app_name: str, backend_spec: str) -> str:
    context = f"APP NAME: {app_name}\n\nFRONTEND SPEC:\n{frontend_spec}\n\nBACKEND API SPEC:\n{backend_spec}"
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Generate complete frontend for:\n\n{context}"
        }]
    )
    return message.content[0].text

def parse_frontend_files(raw_output: str) -> dict:
    files = {}
    current_file = None
    current_content = []
    for line in raw_output.split("\n"):
        if line.startswith("===FILE:") and line.endswith("==="):
            if current_file and current_content:
                files[current_file] = "\n".join(current_content).strip()
            current_file = line[8:-3].strip()
            current_content = []
        elif current_file:
            current_content.append(line)
    if current_file and current_content:
        files[current_file] = "\n".join(current_content).strip()
    return files

def save_frontend_files(files: dict, app_name: str) -> str:
    app_dir = f"/root/ai-pm-agent/generated_apps/{app_name}/frontend"
    os.makedirs(app_dir, exist_ok=True)
    for filename, content in files.items():
        filepath = f"{app_dir}/{filename}"
        with open(filepath, "w") as f:
            f.write(content)
    return app_dir
