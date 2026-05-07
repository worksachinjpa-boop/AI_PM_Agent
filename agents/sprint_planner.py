import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an experienced scrum master who creates realistic sprint plans.
Given a product backlog, create a 3-sprint release plan.

Output exactly:

# Sprint Plan — MVP Release

## Team Assumptions
- Team size, velocity, sprint length assumptions

## Sprint 1: Foundation
**Goal:** One sentence sprint goal
**Total Points:** X points
**Tickets:**
- Ticket X.X: [Title] (X pts) — reason for inclusion
- ...

## Sprint 2: Core Features
**Goal:** One sentence sprint goal
**Total Points:** X points
**Tickets:**
- Ticket X.X: [Title] (X pts) — reason for inclusion
- ...

## Sprint 3: Polish & Launch
**Goal:** One sentence sprint goal
**Total Points:** X points
**Tickets:**
- Ticket X.X: [Title] (X pts) — reason for inclusion
- ...

## What's NOT in MVP
List of P2 tickets deferred to post-launch.

## Risk Flags
2-3 tickets that could derail the sprint plan and why.

## Definition of Done
5 criteria that must be true before shipping."""

def run_sprint_planner(backlog: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create a sprint plan for this backlog:\n\n" + backlog}]
    )
    return message.content[0].text
