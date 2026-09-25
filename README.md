# GuardRail

A secure CI/CD pipeline for deploying AWS infrastructure, combining policy-as-code security scanning, least-privilege IAM design, and an AI-assisted review layer for pull requests.

## Overview

GuardRail automates the deployment of AWS infrastructure via Terraform, but every change must pass through automated security checks before it can be merged or applied. The goal is to make "secure by default" the easy path, not an afterthought.

This project was built to explore how security, automation, and AI can work together in a real DevOps pipeline — inspired by conversations with engineers working on similar problems in production.

## Architecture

```text
Developer -> Push / Pull Request

			 |
			 v

	   GitHub Actions

	   +--------+--------+--------+
	   v        v        v
   Terraform  tfsec   Gemini AI
   fmt/init/  security  summary
   validate/  scan
   plan
	   |        |        |
	   +--------+--------+
				|
				v

	 PR Comment 1       PR Comment 2
	 raw tfsec           plain-English
	 findings            AI summary
```

The pipeline never runs `terraform apply` automatically. Every run is plan-only, so a pull request shows what would change and what security issues it introduces without touching real infrastructure until a human explicitly applies it.

## Tech Stack

- **Infrastructure as Code:** Terraform
- **CI/CD:** GitHub Actions
- **Policy-as-Code Scanning:** tfsec
- **Secrets Management:** GitHub Actions Secrets (API keys and AWS credentials); AWS Secrets Manager is documented as a future application-secrets pattern
- **Cloud Provider:** AWS
- **AI Layer:** Google Gemini API, which reads tfsec JSON output and generates a plain-English security summary posted as a pull request comment

The AI summary step queries Gemini's available models at runtime instead of hardcoding one. It falls back across models when the preferred model is unavailable, retries transient `503` and `429` failures with backoff, and degrades gracefully to a raw-findings notice if the AI call fails entirely.

## Security Scan Results

The AI-assisted `tfsec` review for `terraform/modules/networking/main.tf` identified the following items:

### High: Public IP assignment on public subnets (`AVD-AWS-0164`)

The public subnet resource enables `map_public_ip_on_launch`, which automatically assigns public IPv4 addresses to resources launched there. This is intentional because these subnets are designed for public-facing resources such as load balancers. Private services use the separate private subnets, where this is disabled.

**Status:** Accepted by design. The finding is documented rather than suppressed so the reasoning remains visible during review.

### Medium: VPC Flow Logs (`AVD-AWS-0178`)

The initial scan reported that VPC Flow Logs were not enabled, reducing visibility for troubleshooting and security investigations.

**Status:** Fixed. The networking module sends all VPC traffic logs to a private S3 bucket with public access blocked by `aws_s3_bucket_public_access_block`.

## Lessons Learned

- **Hardcoded model names go stale.** The AI summary step originally hardcoded a Gemini model that became unavailable. The client now queries available models at runtime and falls back across them, with separate handling for transient and permanent failures.
- **External APIs fail under load.** Gemini returned `503` errors during testing. The AI step degrades gracefully: raw tfsec findings are always posted, while the AI summary fails safely as an optional enhancement.
- **Least privilege takes iteration.** Adding VPC Flow Logs required extending the CI IAM policy with scoped S3 and flow-log permissions rather than broadening it to administrator access.
- **`force_destroy` is a real trade-off.** It supports fast destroy-and-recreate cycles in development, but would be dangerous in production where accidentally deleting logs matters.

## Features

- [x] Terraform module for core networking (VPC, subnets, IGW, route tables)
- [ ] Additional Terraform modules (compute, IAM)
- [ ] Remote state management (S3 + DynamoDB lock table)
- [x] Automated `terraform plan` on every pull request
- [x] Policy-as-code scanning via tfsec, with findings posted to every pull request
- [x] Least-privilege IAM role scoped to CI, separate from administrator credentials
- [x] VPC Flow Logs to a locked-down S3 bucket
- [ ] Secrets Manager pattern for application-level secrets (CI secrets use GitHub Actions Secrets)
- [x] AI-generated plain-English summary of scan results posted as a PR comment
- [x] Architecture diagram and documentation

## Getting Started

### Prerequisites

- AWS account (always-free tier services are sufficient)
- Terraform installed locally
- GitHub account with Actions enabled
- A free Google Gemini API key for the AI summary step

### Setup

```bash
git clone https://github.com/maneeshaYasinth/guardrail.git
cd guardrail
```

Configure AWS credentials locally:

```bash
aws configure
```

Add these GitHub repository secrets under **Settings -> Secrets and variables -> Actions**:

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: scoped CI IAM credentials
- `GEMINI_API_KEY`: a key from [Google AI Studio](https://aistudio.google.com)

Run locally:

```bash
cd terraform/environments/dev
terraform init
terraform plan
```

## Project Structure

```text
guardrail/
├── terraform/
│   ├── modules/
│   │   └── networking/       # VPC, subnets, IGW, route tables, flow logs
│   └── environments/
│       └── dev/              # Environment configuration and module calls
├── .github/
│   ├── workflows/
│   │   └── terraform.yml     # Plan, scan, and AI summary pipeline
│   └── scripts/
│       └── summarize_findings.py  # Reads tfsec output and calls Gemini
└── docs/                     # Documentation placeholder
```


## Roadmap

1. Base Terraform networking module and dev environment configuration
2. GitHub Actions pipeline with format, validate, plan, and scan steps
3. tfsec integrated with pull-request comments
4. Least-privilege IAM role for CI
5. VPC Flow Logs to close a real tfsec finding
6. AI-powered pull-request summary with retry and fallback logic
7. Additional infrastructure modules for compute and workload IAM
8. Remote state management with S3 and DynamoDB locking
9. Secrets Manager pattern for application-level secrets

## Why This Project

Most portfolio projects stop at "infrastructure that deploys." GuardRail goes a step further: infrastructure that deploys *safely*, with security checks, least-privilege access, and clear visibility baked into the pipeline rather than bolted on afterward. Each design decision, from plan-only CI to accepted versus fixed findings, is documented with the reasoning behind it.

## License

MIT (to be added)
