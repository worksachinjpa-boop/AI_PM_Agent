import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior engineering manager who creates precise, actionable product backlogs.
Given a PRD, create a complete sprint-ready backlog.

Output exactly in this format:

# Product Backlog

## Epic 1: [Epic Name]
*Goal: One sentence on what this epic achieves*

### Ticket 1.1: [Ticket Title]
**Type:** Feature / Bug / Chore / Spike
**Priority:** P0 / P1 / P2
**Story Points:** 1 / 2 / 3 / 5 / 8
**Dependencies:** None / Ticket X.X
**Description:** 2-3 sentences on what needs to be built.
**Acceptance Criteria:**
- [ ] Specific testable criterion 1
- [ ] Specific testable criterion 2
- [ ] Specific testable criterion 3

### Ticket 1.2: [Ticket Title]
[same format]

## Epic 2: [Epic Name]
[same format]

Rules:
- Create 3-4 epics
- Each epic has 3-5 tickets
- Total 12-18 tickets
- Story points use fibonacci: 1,2,3,5,8 only
- P0 = must have for launch, P1 = should have, P2 = nice to have
- Acceptance criteria must be testable by a QA engineer
- Be specific — no vague tickets like "implement backend" """

def run_backlog_creator(prd: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create a complete backlog for this PRD:\n\n" + prd}]
    )
    return message.content[0].text
