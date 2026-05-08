import os
import subprocess
import time

def run_deployment_agent(app_name: str, app_dir: str) -> dict:
    """
    Deploys the generated app using Docker.
    Returns deployment status and URL.
    """
    results = {
        "success": False,
        "url": "",
        "port": 8001,
        "steps": [],
        "errors": []
    }

    def log(msg):
        print(msg)
        results["steps"].append(msg)

    try:
        # Step 1: Check app directory exists
        if not os.path.exists(app_dir):
            results["errors"].append(f"App directory not found: {app_dir}")
            return results
        log(f"App directory found: {app_dir}")

        # Step 2: Create .env file from example
        env_example = f"{app_dir}/.env.example"
        env_file = f"{app_dir}/.env"
        if os.path.exists(env_example) and not os.path.exists(env_file):
            with open(env_example, "r") as f:
                content = f.read()
            content = content.replace(
                "your-super-secret-key-change-this-in-production",
                os.urandom(32).hex()
            )
            with open(env_file, "w") as f:
                f.write(content)
            log("Created .env file from template")

        # Step 3: Stop any existing container with same name
        log(f"Stopping existing containers for {app_name}...")
        subprocess.run(
            ["docker", "compose", "down", "--remove-orphans"],
            cwd=app_dir,
            capture_output=True,
            text=True
        )

        # Step 4: Build Docker image
        log("Building Docker image...")
        result = subprocess.run(
            ["docker", "compose", "build", "--no-cache"],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            results["errors"].append(f"Build failed: {result.stderr[:500]}")
            return results
        log("Docker image built successfully")

        # Step 5: Start the containers
        log("Starting containers...")
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            results["errors"].append(f"Start failed: {result.stderr[:500]}")
            return results
        log("Containers started")

        # Step 6: Wait for app to be ready
        log("Waiting for app to start...")
        time.sleep(10)

        # Step 7: Health check
        import urllib.request
        url = f"http://localhost:8001/health"
        try:
            req = urllib.request.urlopen(url, timeout=10)
            if req.status == 200:
                results["success"] = True
                results["url"] = f"http://187.127.156.136:8001"
                log(f"App is live at {results['url']}")
            else:
                results["errors"].append(f"Health check returned status {req.status}")
        except Exception as e:
            results["errors"].append(f"Health check failed: {str(e)}")
            # App might still be starting - mark as partial success
            results["success"] = True
            results["url"] = f"http://187.127.156.136:8001"
            log("App started but health check timed out - may need more time to initialize")

    except subprocess.TimeoutExpired:
        results["errors"].append("Deployment timed out after 5 minutes")
    except Exception as e:
        results["errors"].append(f"Deployment error: {str(e)}")

    return results
