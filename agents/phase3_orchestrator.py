import os
from dotenv import load_dotenv
from agents.prd_writer import run_prd_writer
from agents.prd_reviewer import run_prd_reviewer
from database import save_prd

load_dotenv()

def run_phase3(phase1_output: dict) -> dict:
    print("\nStarting Phase 3: PRD Writer")
    print("=" * 50)

    print("\n[Agent 1/2] PRD Writer running...")
    prd = run_prd_writer(phase1_output)
    print("Done.")

    print("\n[Agent 2/2] Quality Reviewer running...")
    review = run_prd_reviewer(prd)
    print("Done.")

    print("\nSaving PRD to file...")
    filename = f"/root/ai-pm-agent/outputs/prd_{phase1_output.get('analysis_id', 'draft')}.txt"
    with open(filename, "w") as f:
        f.write("PRODUCT REQUIREMENTS DOCUMENT\n")
        f.write("=" * 50 + "\n\n")
        f.write(prd)
        f.write("\n\n" + "=" * 50 + "\n")
        f.write("QUALITY REVIEW\n")
        f.write("=" * 50 + "\n\n")
        f.write(review)
    print(f"Saved to {filename}")

    return {
        "prd": prd,
        "review": review,
        "filename": filename
    }
