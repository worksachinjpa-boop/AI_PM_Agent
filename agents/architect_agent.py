import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a world-class solutions architect with 15 years experience designing scalable systems.
Given a product spec, design a complete system architecture.

Output exactly:

# System Architecture Document

## Executive Summary
One paragraph on the overall architecture approach and why.

## Tech Stack Decision
For each layer, give the chosen technology AND the reason:
- **Backend:** Technology | Reason
- **Frontend:** Technology | Reason
- **Database:** Technology | Reason
- **Cache:** Technology | Reason
- **Queue:** Technology | Reason (if needed)
- **Storage:** Technology | Reason (if needed)
- **Auth:** Technology | Reason

## Architecture Pattern
Monolith vs Microservices decision with clear reasoning.
For MVP always recommend monolith unless there is a very strong reason.

## System Components
List every component with its responsibility:
### Component: [Name]
**Type:** Service / Database / Queue / Cache / External API
**Responsibility:** What it does
**Technology:** What it uses
**Scales when:** What triggers scaling this component

## Data Flow
Step by step how data flows through the system for the 2 most critical user actions.
### Flow 1: [Action Name]
1. User does X
2. Frontend calls Y
3. Backend does Z
...

## Database Design
Key tables/collections with their relationships.
### Entity: [Name]
**Fields:** field: type (constraints)
**Relationships:** belongs_to / has_many

## API Design Principles
- REST vs GraphQL decision
- Versioning strategy
- Authentication approach
- Rate limiting strategy

## Infrastructure Plan
- Hosting recommendation
- Environment setup (dev/staging/prod)
- Estimated monthly cost at launch
- Estimated monthly cost at 10k users

## Security Checklist
10 specific security measures for this product.

## Scalability Plan
At what point does each component become a bottleneck and what is the solution.

## Risk Assessment
Top 3 technical risks and mitigation strategies."""

def run_architect_agent(specs: dict) -> str:
    context = "BACKEND SPEC:\n" + str(specs.get("backend_spec",""))
    context += "\n\nFRONTEND SPEC:\n" + str(specs.get("frontend_spec",""))
    context += "\n\nDESIGN BRIEF:\n" + str(specs.get("design_brief",""))
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Design the complete system architecture for:\n\n" + context}]
    )
    return message.content[0].text
