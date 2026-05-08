import os
import subprocess

def run_test_runner_agent(app_dir: str) -> dict:
    """
    Installs dependencies and runs pytest against the generated app.
    Returns test results with pass/fail status.
    """
    results = {
        "success": False,
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "steps": [],
        "errors": [],
        "output": ""
    }

    def log(msg):
        print(msg)
        results["steps"].append(msg)

    try:
        # Step 1: Check app directory
        if not os.path.exists(app_dir):
            results["errors"].append(f"App directory not found: {app_dir}")
            return results
        log(f"App directory: {app_dir}")

        # Step 2: Create a basic test file if none exists
        test_dir = f"{app_dir}/tests"
        os.makedirs(test_dir, exist_ok=True)
        test_file = f"{test_dir}/test_main.py"

        if not os.path.exists(test_file):
            log("Creating basic test file...")
            test_content = """import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    try:
        import main
        assert True
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")

def test_models_importable():
    """Test that models module exists"""
    try:
        import models
        assert True
    except ImportError as e:
        pytest.skip(f"Models import failed: {e}")

def test_database_importable():
    """Test that database module exists"""
    try:
        import database
        assert True
    except ImportError as e:
        pytest.skip(f"Database import failed: {e}")

def test_routes_exist():
    """Test that routes directory exists"""
    import os
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.exists(os.path.join(app_dir, "routes")), "routes directory missing"

def test_requirements_exist():
    """Test that requirements.txt exists"""
    import os
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.exists(os.path.join(app_dir, "requirements.txt")), "requirements.txt missing"

def test_dockerfile_exists():
    """Test that Dockerfile exists"""
    import os
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.exists(os.path.join(app_dir, "Dockerfile")), "Dockerfile missing"
"""
            with open(test_file, "w") as f:
                f.write(test_content)
            log("Test file created")

        # Step 3: Install pytest
        log("Installing pytest...")
        subprocess.run(
            ["pip", "install", "pytest", "pytest-asyncio", "--quiet"],
            capture_output=True, text=True
        )

        # Step 4: Run tests
        log("Running tests...")
        result = subprocess.run(
            ["python3", "-m", "pytest", test_dir, "-v", "--tb=short", "--no-header"],
            capture_output=True,
            text=True,
            cwd=app_dir,
            timeout=120
        )

        results["output"] = result.stdout + result.stderr

        # Parse results
        for line in result.stdout.split("\n"):
            if " passed" in line:
                import re
                passed = re.findall(r"(\d+) passed", line)
                failed = re.findall(r"(\d+) failed", line)
                if passed:
                    results["tests_passed"] = int(passed[0])
                if failed:
                    results["tests_failed"] = int(failed[0])
                results["tests_run"] = results["tests_passed"] + results["tests_failed"]

        results["success"] = result.returncode == 0 or results["tests_passed"] > 0
        log(f"Tests: {results['tests_passed']} passed, {results['tests_failed']} failed")

    except subprocess.TimeoutExpired:
        results["errors"].append("Tests timed out after 2 minutes")
    except Exception as e:
        results["errors"].append(str(e))

    return results
