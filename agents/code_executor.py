import os
import subprocess
import json

def run_code_executor(app_dir: str) -> dict:
    """
    Attempts to install dependencies and syntax-check the generated code.
    Returns success status and any errors found.
    """
    results = {
        "success": True,
        "errors": [],
        "warnings": [],
        "files_checked": []
    }
    
    # Step 1: Check all Python files for syntax errors
    print("Checking Python syntax...")
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                result = subprocess.run(
                    ["python3", "-m", "py_compile", filepath],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    results["success"] = False
                    results["errors"].append({
                        "file": filepath.replace(app_dir + "/", ""),
                        "error": result.stderr.strip()
                    })
                else:
                    results["files_checked"].append(filepath.replace(app_dir + "/", ""))
    
    # Step 2: Check requirements.txt exists
    req_file = f"{app_dir}/requirements.txt"
    if not os.path.exists(req_file):
        results["warnings"].append("requirements.txt not found")
    
    # Step 3: Check Dockerfile exists
    dockerfile = f"{app_dir}/Dockerfile"
    if not os.path.exists(dockerfile):
        results["warnings"].append("Dockerfile not found")
    
    # Step 4: Try installing requirements in a temp venv
    if os.path.exists(req_file):
        print("Checking requirements installability...")
        result = subprocess.run(
            ["pip", "install", "--dry-run", "-r", req_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            results["warnings"].append(f"Some requirements may not install: {result.stderr[:200]}")
    
    return results
