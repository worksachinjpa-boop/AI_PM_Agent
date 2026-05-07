import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def run_phase5(backlog: str) -> dict:
    print("\nStarting Phase 5: Parallel Execution")
    print("=" * 50)
    print("\n[Parallel] Design Agent + Backend Agent running simultaneously...")

    from agents.design_agent import run_design_agent
    from agents.backend_agent import run_backend_agent

    # Run design and backend IN PARALLEL
    design, backend = await asyncio.gather(
        asyncio.to_thread(run_design_agent, backlog),
        asyncio.to_thread(run_backend_agent, backlog)
    )
    print("Both done!")

    print("\n[Sequential] Frontend Agent running (needs design output)...")
    from agents.frontend_agent import run_frontend_agent
    frontend = await asyncio.to_thread(run_frontend_agent, backlog, design)
    print("Done.")

    return {
        "design_brief": design,
        "backend_spec": backend,
        "frontend_spec": frontend
    }
