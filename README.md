# GuardRail

A secure CI/CD pipeline for deploying AWS infrastructure, combining policy-as-code security scanning, least-privilege IAM design, and an AI-assisted review layer for pull requests.

## Overview

GuardRail automates the deployment of AWS infrastructure via Terraform, but every change must pass through automated security checks before it can be merged or applied. The goal is to make "secure by default" the easy path, not an afterthought.

This project was built to explore how security, automation, and AI can work together in a real DevOps pipeline — inspired by conversations with engineers working on similar problems in production.

## Architecture

*(Diagram coming soon — will show Terraform modules, CI/CD flow, and where scanning/AI steps sit in the pipeline)*

## Tech Stack

- **Infrastructure as Code:** Terraform
- **CI/CD:** GitHub Actions
- **Policy-as-Code Scanning:** tfsec / Checkov
- **Secrets Management:** AWS Secrets Manager / SSM Parameter Store
- **Cloud Provider:** AWS
- **AI Layer:** LLM-based summarization of scan results (planned)

The AI summary step retries transient Gemini API failures and falls back to a raw findings notice so external service interruptions do not fail the entire CI pipeline.

## Features

- [ ] Terraform modules for core infra (networking, compute, IAM)
- [ ] Remote state management (S3 + DynamoDB lock table)
- [ ] Automated `terraform plan` on every pull request
- [ ] Policy-as-code scanning gate (blocks merge on high-severity findings)
- [ ] Least-privilege IAM roles scoped per environment (dev/prod)
- [ ] Secrets pulled from Secrets Manager, never hardcoded
- [ ] AI-generated plain-English summary of scan results posted as a PR comment
- [ ] Architecture diagram and full documentation

## Getting Started

### Prerequisites

- AWS account (free tier is fine for testing)
- Terraform installed locally
- GitHub account with Actions enabled

### Setup

```bash
git clone https://github.com/<your-username>/guardrail.git
cd guardrail
```

*(More detailed setup instructions will be added as the pipeline is built out.)*

## Project Structure

guardrail/
├── terraform/
│ ├── modules/
│ └── environments/
│ ├── dev/
│ └── prod/
├── .github/
│ └── workflows/
└── docs/


## Roadmap

1. Set up base Terraform modules and remote state
2. Build the base GitHub Actions pipeline (fmt, validate, plan)
3. Integrate tfsec/Checkov as a required check
4. Add least-privilege IAM roles per environment
5. Move all secrets to Secrets Manager
6. Add the AI-powered PR summary step
7. Write full documentation and architecture diagram

## Why This Project

Most portfolio projects stop at "infrastructure that deploys." GuardRail is an attempt to go a step further — infrastructure that deploys *safely*, with security checks and clear visibility baked into the pipeline itself, rather than bolted on afterward.

## License

MIT (to be added)
