import urllib.request
import json
import subprocess

def run_monitoring_agent(url: str, app_name: str) -> dict:
    """
    Checks if deployed app is running and healthy.
    Returns monitoring report.
    """
    results = {
        "is_live": False,
        "response_time_ms": None,
        "health_status": None,
        "docker_status": None,
        "issues": [],
        "report": ""
    }

    # Check 1: HTTP health check
    import time
    try:
        start = time.time()
        req = urllib.request.urlopen(f"{url}/health", timeout=10)
        elapsed = round((time.time() - start) * 1000)
        results["is_live"] = True
        results["response_time_ms"] = elapsed
        results["health_status"] = "healthy"
        if elapsed > 2000:
            results["issues"].append(f"Slow response: {elapsed}ms (target < 500ms)")
    except Exception as e:
        results["issues"].append(f"Health check failed: {str(e)}")
        results["health_status"] = "unhealthy"

    # Check 2: Docker container status
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True
        )
        results["docker_status"] = result.stdout.strip()
        if app_name not in result.stdout:
            results["issues"].append(f"Container {app_name} not found in running containers")
    except Exception as e:
        results["issues"].append(f"Docker check failed: {str(e)}")

    # Generate report
    status = "LIVE" if results["is_live"] else "DOWN"
    report = f"""# Monitoring Report — {app_name}

## Status: {status}
- Health endpoint: {results["health_status"]}
- Response time: {results["response_time_ms"]}ms
- App URL: {url}

## Docker Status
{results["docker_status"] or "Unable to check"}

## Issues Found
"""
    if results["issues"]:
        for issue in results["issues"]:
            report += f"- {issue}\n"
    else:
        report += "No issues detected. App is running normally."

    results["report"] = report
    return results
