# Deployment Guide

## Overview

We use a CI/CD pipeline with three main environments:
- **Development** - Automatically deployed from `develop` branch
- **Staging** - Automatically deployed from `staging` branch  
- **Production** - Deployed from `main` branch after manual approval

## Environment URLs

- Development: https://dev.app.company.com
- Staging: https://staging.app.company.com
- Production: https://app.company.com

## Deployment Process

### Deploying to Development

Development deployments happen automatically when you merge to `develop`:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit
3. Push your branch: `git push origin feature/your-feature`
4. Create a Pull Request to `develop` branch
5. Get code review approval (at least 1 reviewer)
6. Merge the PR

**The deployment happens automatically!**

- CI/CD pipeline runs tests
- If tests pass, builds Docker image
- Deploys to development environment
- Takes ~5-10 minutes
- You'll get a Slack notification in #deployments when complete

### Deploying to Staging

Staging is for final testing before production:

1. Create a PR from `develop` to `staging`
2. Get approval from your team lead
3. Merge the PR
4. Automatic deployment to staging begins
5. Takes ~10-15 minutes
6. Smoke tests run automatically after deployment

**Staging Deployment Checklist:**
- [ ] All feature PRs have been merged to develop
- [ ] Tests are passing in develop
- [ ] Feature has been tested in development environment
- [ ] Database migrations have been reviewed (if any)
- [ ] Team lead has approved the staging deployment

### Deploying to Production

Production deployments require extra caution:

1. Create a PR from `staging` to `main`
2. Add the `production-deploy` label
3. Get approval from:
   - Your team lead
   - One senior engineer
   - Product owner (for feature releases)
4. Merge the PR
5. **Manual approval required** in CI/CD pipeline
6. Deployment takes ~15-20 minutes
7. Post-deployment monitoring for 30 minutes

**Production Deployment Checklist:**
- [ ] Feature fully tested in staging
- [ ] Database migrations tested in staging
- [ ] Performance impact assessed
- [ ] Rollback plan documented
- [ ] On-call engineer notified
- [ ] Monitoring dashboards ready
- [ ] Deploy during business hours (unless emergency)

## Deployment Commands

You typically won't run these manually (CI/CD does it), but for reference:

```bash
# Build Docker image
docker build -t company/app:latest .

# Run database migrations
python manage.py migrate --database=production

# Deploy with kubectl (requires proper credentials)
kubectl apply -f k8s/production/

# Check deployment status
kubectl rollout status deployment/app -n production
```

## Database Migrations

### Creating Migrations

```bash
# Create a new migration
python manage.py makemigrations

# Review the generated migration file
# Ensure it's safe (no data loss)
git add migrations/
```

### Migration Safety Rules

1. **Never delete columns** in production without a multi-step process
2. **Always add columns as nullable** first
3. **Test migrations on staging data** before production
4. **Have a rollback plan** for data migrations
5. **Avoid complex data transformations** in migrations

### Risky Migration Pattern (Don't Do This):
```python
# BAD: Dropping column immediately
operations = [
    migrations.RemoveField(model_name='user', name='old_field'),
]
```

### Safe Migration Pattern:
```python
# GOOD: Multi-step approach
# Step 1: Add new nullable field
# Step 2 (separate deploy): Backfill data
# Step 3 (separate deploy): Make field required
# Step 4 (separate deploy): Remove old field
```

## Rollback Procedures

### Automatic Rollback

If health checks fail after deployment, automatic rollback occurs:
- Previous version restored within 2 minutes
- Alert sent to #incidents
- No manual intervention needed

### Manual Rollback

If you need to rollback manually:

```bash
# Development/Staging (via git)
git revert <commit-hash>
git push origin develop

# Production (via CI/CD)
# Go to: https://ci.company.com/app/deployments
# Click "Rollback" on the previous successful deployment
```

**When to Rollback:**
- Critical bugs discovered in production
- Performance degradation
- Data integrity issues
- Security vulnerabilities

## Monitoring Deployments

### During Deployment

Watch these dashboards during production deployments:
- **Application Health**: https://grafana.company.com/app-health
- **Error Rates**: https://sentry.company.com/company/app
- **Performance**: https://datadog.company.com/apm
- **Logs**: https://logs.company.com

### Key Metrics to Monitor

- **Error Rate**: Should stay below 0.1%
- **Response Time (p95)**: Should stay below 500ms
- **CPU/Memory**: Should stay below 70% utilization
- **Database Connections**: Should not exceed pool size

### Red Flags (Immediate Rollback)

- Error rate spikes above 1%
- Response time increases by >50%
- Memory leak detected
- Database connection pool exhausted
- 5xx errors increasing

## Deployment Schedule

- **Development**: Deploy anytime (automated)
- **Staging**: Deploy anytime during business hours
- **Production**: 
  - Regular deploys: Tuesday-Thursday, 10am-2pm PST
  - Emergency deploys: Anytime with VP Engineering approval
  - Avoid: Fridays, weekends, holidays, during high-traffic events

## Hotfix Process

For critical production bugs:

1. Create hotfix branch from `main`: `git checkout -b hotfix/critical-bug main`
2. Fix the bug with minimal changes
3. Create PR directly to `main` (skip develop/staging)
4. Add `hotfix` label
5. Get emergency approval (team lead + on-call engineer)
6. Deploy immediately
7. **Backport fix to develop**: Create PR from hotfix branch to develop

**Hotfix Definition**: 
- Security vulnerability
- Data loss issue  
- Service completely down
- Payment processing broken

## Continuous Integration (CI)

Every PR triggers:
- Unit tests
- Integration tests
- Linting and formatting checks
- Security scans
- Build verification

**All checks must pass before merging.**

## Feature Flags

For risky features, use feature flags:

```python
from feature_flags import is_enabled

if is_enabled('new_feature', user):
    # New code path
else:
    # Old code path
```

Configure flags at: https://features.company.com

Benefits:
- Deploy code without enabling feature
- Gradual rollout (5% → 25% → 50% → 100%)
- Instant rollback without redeployment
- A/B testing capabilities

## Getting Help

- **CI/CD Issues**: #devops channel
- **Deployment Failures**: #incidents (page on-call if urgent)
- **Questions**: #engineering-help
- **On-Call Engineer**: See PagerDuty schedule
