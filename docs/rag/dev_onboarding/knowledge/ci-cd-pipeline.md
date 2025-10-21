# CI/CD Pipeline Guide

## Overview

Our CI/CD pipeline automatically builds, tests, and deploys code changes. Every push triggers automated checks, ensuring code quality and reliability before deployment.

## Pipeline Architecture

```
GitHub Push
    │
    ▼
GitHub Actions (CI)
    │
    ├─► Linting & Formatting
    ├─► Unit Tests
    ├─► Integration Tests
    ├─► Security Scan
    ├─► Build Docker Image
    └─► Push to ECR
        │
        ▼
    Auto Deploy (CD)
        │
        ├─► Development (auto)
        ├─► Staging (auto on staging branch)
        └─► Production (manual approval)
```

## GitHub Actions Workflows

### Main Workflow (.github/workflows/main.yml)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [develop, staging, main]
  pull_request:
    branches: [develop, staging, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run Black
        run: black --check .
      - name: Run Ruff
        run: ruff check .
      - name: Run mypy
        run: mypy .

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-fail-under=80
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit (security linter)
        run: |
          pip install bandit
          bandit -r app/
      - name: Run Safety (dependency checker)
        run: |
          pip install safety
          safety check
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: company-app
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
                     $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to Development
        run: |
          # Trigger ECS deployment
          aws ecs update-service \
            --cluster dev-cluster \
            --service app-service \
            --force-new-deployment

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    steps:
      - name: Deploy to Staging
        run: |
          aws ecs update-service \
            --cluster staging-cluster \
            --service app-service \
            --force-new-deployment
      - name: Run smoke tests
        run: |
          curl -f https://staging.app.company.com/health || exit 1

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://app.company.com
    steps:
      - name: Deploy to Production
        run: |
          aws ecs update-service \
            --cluster prod-cluster \
            --service app-service \
            --force-new-deployment
      - name: Notify team
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Production deployment started for commit ${{ github.sha }}"
            }
```

## Pipeline Stages Explained

### 1. Linting (Code Quality)

Checks code formatting and style:
- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **mypy**: Static type checking

**Why it matters**: Catches style issues and potential bugs before code review.

**Local testing**:
```bash
make lint
# or
black --check .
ruff check .
mypy .
```

### 2. Testing

Runs all test suites:
- Unit tests
- Integration tests  
- Coverage report (must be ≥80%)

**Why it matters**: Ensures code works correctly and doesn't break existing functionality.

**Local testing**:
```bash
make test
# or
pytest --cov=app
```

### 3. Security Scanning

Checks for security vulnerabilities:
- **Bandit**: Scans code for security issues
- **Safety**: Checks dependencies for known vulnerabilities
- **TruffleHog**: Detects accidentally committed secrets

**Why it matters**: Prevents security vulnerabilities from reaching production.

**Common issues**:
- Hardcoded API keys (use environment variables)
- SQL injection vulnerabilities (use ORM)
- Weak password hashing (use bcrypt)

### 4. Build

Creates Docker image:
- Builds container with application code
- Pushes to Amazon ECR (container registry)
- Tags with commit SHA and "latest"

**Why it matters**: Creates deployable artifact that's identical across all environments.

### 5. Deploy

Deploys to appropriate environment:
- **Development**: Automatic on push to `develop`
- **Staging**: Automatic on push to `staging`
- **Production**: Manual approval required

**Why it matters**: Gets code running in target environment.

## CI/CD Dashboard

Monitor pipeline status at:
- **GitHub Actions**: https://github.com/company/app/actions
- **AWS ECS**: https://console.aws.amazon.com/ecs
- **Deployment History**: https://ci.company.com/deployments

## Common CI/CD Issues

### Issue: Tests Failing in CI but Passing Locally

**Possible causes**:
1. Different Python version
2. Missing environment variables
3. Database state differences
4. Timezone differences

**Solutions**:
```bash
# Match CI Python version locally
pyenv install 3.11.0
pyenv local 3.11.0

# Run tests with same env vars as CI
export DATABASE_URL=postgresql://postgres:postgres@localhost/test
pytest
```

### Issue: Build Taking Too Long

**Optimization strategies**:
1. Use Docker layer caching
2. Install only production dependencies in final image
3. Use multi-stage Docker builds
4. Cache pip dependencies

```dockerfile
# Multi-stage build example
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "app/main.py"]
```

### Issue: Deployment Failed

**Check these**:
1. Look at GitHub Actions logs
2. Check ECS task logs in CloudWatch
3. Verify environment variables are set
4. Check database migrations ran successfully
5. Verify health checks are passing

```bash
# Check ECS task status
aws ecs describe-services \
  --cluster prod-cluster \
  --services app-service

# Check task logs
aws logs tail /ecs/app-service --follow
```

### Issue: Security Scan Blocking Merge

**Common causes**:
1. Outdated dependency with CVE
2. Hardcoded secret detected
3. Insecure code pattern

**Solutions**:
```bash
# Update vulnerable dependency
pip install --upgrade vulnerable-package

# Check which dependency is vulnerable
safety check --json

# Remove hardcoded secrets
# Use environment variables instead
```

## Environment Variables in CI

### GitHub Secrets

Store sensitive data as GitHub secrets:
1. Go to Settings → Secrets and variables → Actions
2. Add new secret
3. Reference in workflow: `${{ secrets.SECRET_NAME }}`

**Common secrets**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DOCKER_HUB_TOKEN`
- `SLACK_WEBHOOK`

### Environment-Specific Variables

Set in ECS task definitions:
```json
{
  "environment": [
    {"name": "DATABASE_URL", "value": "..."},
    {"name": "REDIS_URL", "value": "..."},
    {"name": "LOG_LEVEL", "value": "INFO"}
  ],
  "secrets": [
    {
      "name": "API_KEY",
      "valueFrom": "arn:aws:secretsmanager:..."
    }
  ]
}
```

## Manual Pipeline Actions

### Trigger Manual Deployment

```bash
# Via GitHub CLI
gh workflow run deploy.yml -f environment=production

# Via AWS CLI (direct ECS update)
aws ecs update-service \
  --cluster prod-cluster \
  --service app-service \
  --force-new-deployment
```

### Cancel Running Pipeline

1. Go to GitHub Actions tab
2. Click on the running workflow
3. Click "Cancel workflow"

Or via CLI:
```bash
gh run cancel <run-id>
```

### Re-run Failed Pipeline

1. Go to failed workflow run
2. Click "Re-run jobs"
3. Select "Re-run failed jobs"

Or run all jobs:
```bash
gh run rerun <run-id>
```

## Pipeline Best Practices

### DO ✓

1. **Run tests locally** before pushing
2. **Keep pipelines fast** - aim for <10 minutes
3. **Make tests deterministic** - no flaky tests
4. **Use caching** for dependencies
5. **Monitor pipeline health** - fix broken tests immediately
6. **Tag releases** with semantic versions

### DON'T ✗

1. **Don't skip CI** - even for "small changes"
2. **Don't commit to main** - always use PRs
3. **Don't ignore security warnings** - fix them
4. **Don't deploy on Friday** - unless it's a hotfix
5. **Don't disable tests** to make CI pass
6. **Don't hardcode secrets** in workflows

## Monitoring & Alerts

### Pipeline Alerts

We get notified when:
- Build fails on main/staging/develop
- Tests fail repeatedly
- Deployment fails
- Security vulnerability detected

**Alert channels**:
- Slack: #ci-cd-alerts
- Email: dev-team@company.com
- PagerDuty: For production failures

### Metrics We Track

- **Build Success Rate**: Should be >95%
- **Average Build Time**: <10 minutes
- **Test Flakiness**: Failing tests that pass on retry
- **Deployment Frequency**: Aim for multiple times per day
- **Lead Time**: Commit to production time
- **Mean Time to Recovery**: How fast we fix broken builds

## Docker Best Practices

### Optimized Dockerfile

```dockerfile
# Use specific version, not "latest"
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.github
.pytest_cache
.coverage
htmlcov/
.env
.env.local
*.log
```

## Rollback Procedures

### Quick Rollback (Via ECS)

```bash
# Find previous task definition
aws ecs list-task-definitions \
  --family-prefix app-service \
  --sort DESC \
  --max-items 5

# Update service to previous version
aws ecs update-service \
  --cluster prod-cluster \
  --service app-service \
  --task-definition app-service:123  # Previous version
```

### Rollback via Git

```bash
# Create revert commit
git revert <bad-commit-hash>
git push origin main

# Pipeline will automatically deploy the reverted code
```

## Getting Help

- **CI/CD not working**: #devops channel
- **GitHub Actions questions**: https://docs.github.com/en/actions
- **AWS deployment issues**: On-call DevOps engineer
- **Docker questions**: #docker-help channel
- **Emergency deployments**: Page on-call via PagerDuty
