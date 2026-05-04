# AI Product Manager Agent

A multi-agent AI system that analyses product ideas using the orchestrator pattern.

## What it does
Takes a rough product idea and runs 4 specialist AI agents in sequence:
1. **Idea Refiner** - Structures the raw idea into a clear problem statement
2. **Market Researcher** - Searches the web for competitors and market size
3. **User Identifier** - Finds real people with this pain on Reddit and forums
4. **Validator** - Stress-tests the idea and gives GO/REFINE/KILL verdict

## Tech Stack
- **Claude API** (Anthropic) - Powers all 4 agents
- **Tavily API** - Real-time web search for market research
- **FastAPI** - Backend web server with Server-Sent Events streaming
- **SQLite** - Saves all analyses with shareable URLs
- **Python** - Core language
- **Systemd** - Auto-restart on server reboot

## Architecture
Uses the orchestrator pattern where a central agent coordinates specialist sub-agents.
Each sub-agent has a focused system prompt and only the tools it needs.
Results stream to the browser in real time as each agent completes.

## Features
- Password protected
- Results saved permanently with unique shareable URLs
- Analysis history page
- Runs on Linux VPS as a systemd service

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app:app --host 0.0.0.0 --port 8000
```
