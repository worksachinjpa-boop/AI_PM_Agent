from agents.orchestrator import run_phase1
import json

if __name__ == "__main__":
    
    raw_idea = """
    I want to build an AI product manager that helps 
    solo founders and small teams manage their product 
    development process from idea to launch automatically
    """
    
    result = run_phase1(raw_idea)
    
    print("\n" + "=" * 50)
    print("DISCOVERY BRIEF")
    print("=" * 50)
    
    print("\n1. REFINED PROBLEM:")
    print(result["refined_problem"])
    
    print("\n2. MARKET RESEARCH:")
    print(result["market_research"])
    
    print("\n3. USER PROFILE:")
    print(result["user_profile"])
    
    print("\n4. VALIDATION:")
    print(result["validation"])
    
    print("\n" + "=" * 50)
    print("Phase 1 Complete!")
    
    # Save output to file
    with open("outputs/discovery_brief.txt", "w") as f:
        f.write("DISCOVERY BRIEF\n")
        f.write("=" * 50 + "\n\n")
        f.write("REFINED PROBLEM:\n" + result["refined_problem"] + "\n\n")
        f.write("MARKET RESEARCH:\n" + result["market_research"] + "\n\n")
        f.write("USER PROFILE:\n" + result["user_profile"] + "\n\n")
        f.write("VALIDATION:\n" + result["validation"] + "\n")
    
    print("Output saved to outputs/discovery_brief.txt")
