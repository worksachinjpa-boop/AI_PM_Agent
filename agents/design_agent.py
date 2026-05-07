import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior product designer who creates precise design briefs for engineering teams.
Given a product backlog, create a complete design brief that designers can use immediately.

Output exactly:

# Design Brief

## Screen Inventory
List every screen that needs to be designed with purpose.
Format: Screen Name | Purpose | Priority (P0/P1/P2)

## User Flows
Step by step flows for the 3 most critical journeys.
Format:
### Flow 1: [Flow Name]
Step 1 → Step 2 → Step 3 → ...

## Component Inventory
List all reusable UI components needed.
Format: Component Name | Description | Used On Screens

## Design System Requirements
- Typography scale
- Color palette guidance
- Spacing system
- Icon library recommendation

## Figma File Structure
Recommended Figma organization:
- Pages
- Frames
- Component library structure

## Design Priorities
What to design first and why. Linked to sprint plan."""

def run_design_agent(backlog: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create a complete design brief for this backlog:\n\n" + backlog}]
    )
    return message.content[0].text
