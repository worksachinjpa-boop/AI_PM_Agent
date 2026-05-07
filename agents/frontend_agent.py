import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior frontend engineer who creates precise frontend specifications.
Given a backlog and design brief, create a complete frontend spec.

Output exactly:

# Frontend Technical Specification

## Tech Stack Recommendation
- Framework and why
- State management approach
- Key libraries needed

## Component Architecture
### Component: [ComponentName]
**Type:** Page / Layout / Feature / UI
**Props:** List key props
**State:** Local state needed
**API Calls:** Which endpoints it calls
**Used By:** Parent components

## State Management Plan
- Global state structure
- Local state per page
- API caching strategy

## Routing Structure
List all routes with their purpose and auth requirements.

## API Integration Points
For each backend endpoint, how frontend consumes it.

## Responsive Design Requirements
- Breakpoints
- Mobile-first considerations
- Key layout changes per breakpoint

## Performance Considerations
- Code splitting strategy
- Lazy loading
- Bundle size targets

## Accessibility Requirements
- WCAG level target
- Key accessibility features needed"""

def run_frontend_agent(backlog: str, design_brief: str) -> str:
    context = "BACKLOG:\n" + backlog + "\n\nDESIGN BRIEF:\n" + design_brief
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create frontend spec based on:\n\n" + context}]
    )
    return message.content[0].text
