import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior DevOps engineer who sets up production-grade infrastructure.
Given a system architecture, create complete DevOps setup documentation.

Output exactly:

# DevOps Setup Guide

## Infrastructure Overview
What gets deployed where and why.

## Docker Setup
### Dockerfile for each service
Provide actual Dockerfile content for each service.

### docker-compose.yml
Provide complete docker-compose.yml for local development.

## CI/CD Pipeline
### GitHub Actions Workflow
Provide actual .github/workflows/deploy.yml content.

Pipeline stages:
1. Test stage
2. Build stage
3. Deploy to staging stage
4. Deploy to production stage

## Environment Variables
Complete list of all env vars needed per environment.
### Development
### Staging
### Production

## Database Setup
- Migration strategy
- Backup schedule
- Recovery procedure

## Monitoring Setup
- Health check endpoints needed
- Metrics to track
- Alert thresholds
- Recommended monitoring stack

## Deployment Checklist
Step by step checklist before every production deployment.

## Rollback Plan
Exact steps to rollback if deployment fails.

## Security Setup
- SSL/TLS configuration
- Firewall rules
- Secret management
- Access control

## Scaling Playbook
Step by step instructions for scaling each component when needed."""

def run_devops_agent(architecture: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Create complete DevOps setup for this architecture:\n\n" + architecture}]
    )
    return message.content[0].text
