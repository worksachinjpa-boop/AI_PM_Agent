import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior backend engineer who creates precise technical specifications.
Given a product backlog, create a complete backend spec that engineers can start immediately.

Output exactly:

# Backend Technical Specification

## Database Schema
For each table:
### Table: [table_name]
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|

## API Endpoints
For each endpoint:
### [METHOD] /api/[endpoint]
**Purpose:** What this endpoint does
**Auth Required:** Yes/No
**Request Body:**
```json
**Response:**
```json
**Error Cases:** List possible errors

## Authentication & Security
- Auth strategy (JWT/Session/OAuth)
- Permission levels
- Security requirements

## Third Party Integrations
- Service name, purpose, API used

## Performance Requirements
- Expected load
- Caching strategy
- Database indexing recommendations

## Environment Variables Needed
List all required env vars with descriptions."""

def run_backend_agent(backlog: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create backend spec for this backlog:\n\n" + backlog}]
    )
    return message.content[0].text
