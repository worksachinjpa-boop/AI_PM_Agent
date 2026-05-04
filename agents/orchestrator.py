import os
from dotenv import load_dotenv
from agents.idea_refiner import run_idea_refiner
from agents.market_researcher import run_market_researcher
from agents.user_identifier import run_user_identifier
from agents.validator import run_validator

load_dotenv()

def run_phase1(raw_idea: str) -> dict:
    """
    Full Phase 1 orchestrator - all 4 agents running in sequence.
    """
    
    print("\nStarting Phase 1: Idea & Discovery")
    print("=" * 50)

    # Agent 1: Refine the idea first
    print("\n[Agent 1/4] Idea Refiner running...")
    refined_idea = run_idea_refiner(raw_idea)
    print("Done.")

    # Agent 2: Research the market
    print("\n[Agent 2/4] Market Researcher running...")
    market_research = run_market_researcher(refined_idea)
    print("Done.")

    # Agent 3: Identify real users
    print("\n[Agent 3/4] User Identifier running...")
    user_profile = run_user_identifier(refined_idea)
    print("Done.")

    # Agent 4: Validate everything
    print("\n[Agent 4/4] Validator running...")
    combined_research = f"""
MARKET RESEARCH:
{market_research}

USER PROFILE:
{user_profile}
"""
    validation = run_validator(refined_idea, combined_research)
    print("Done.")

    return {
        "raw_idea": raw_idea,
        "refined_problem": refined_idea,
        "market_research": market_research,
        "user_profile": user_profile,
        "validation": validation
    }
