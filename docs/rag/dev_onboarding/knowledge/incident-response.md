# Incident Response Guide

## Overview

Incidents happen. When they do, we need to respond quickly, communicate clearly, and learn from what happened. This guide covers our incident response process from detection to post-mortem.

**Severity Levels**:
- **SEV1 (Critical)**: Complete outage, data loss, security breach
- **SEV2 (High)**: Major feature down, significant performance degradation
- **SEV3 (Medium)**: Minor feature issues, limited user impact
- **SEV4 (Low)**: Cosmetic issues, no user impact

## On-Call Schedule

**Rotation**: Weekly rotation, Monday 9am - Monday 9am

**Current Schedule**: Check #oncall channel or PagerDuty

**Tools**:
- **PagerDuty**: Alerts and escalation
- **Slack**: #incidents channel
- **Zoom**: War room for SEV1/SEV2
- **Status Page**: status.company.com

## When Something Goes Wrong

### 1. Detection

**How you might find out**:
- PagerDuty alert
- User report in #support
- Monitoring dashboard alert
- Error rate spike in Sentry
- Customer escalation

### 2. Initial Assessment (First 5 Minutes)

**Questions to answer**:
1. Is this a real incident?
2. What's the severity?
3. What's the blast radius? (how many users affected)
4. Is it still happening?

**Quick triage**:
```bash
# Check application health
curl https://api.company.com/health

# Check recent deployments
kubectl get pods -n production
kubectl logs -n production deployment/api --tail=100

# Check error rates
# Go to DataDog dashboard: Production Error Rates

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM pg_stat_activity;"
```

### 3. Declare Incident (If Needed)

**When to declare**:
- SEV1: Always
- SEV2: If unclear or multiple teams needed
- SEV3: If cross-team coordination needed
- SEV4: Usually just fix it

**How to declare**:
```
/incident declare in #incidents Slack channel

Title: [SEV1] API returning 500 errors
Impact: All users unable to place orders
```

This creates:
- Incident Slack channel (#incident-123)
- PagerDuty incident
- Status page update (for SEV1/SEV2)

### 4. Assemble Response Team

**Incident Commander (IC)**:
- Usually the on-call engineer
- Makes decisions, delegates tasks
- Manages communication
- Does NOT fix the issue directly

**Technical Lead**:
- Investigates root cause
- Coordinates fixes
- Delegates investigation tasks

**Communications Lead** (SEV1/SEV2):
- Updates status page
- Posts updates to #incidents
- Notifies stakeholders

**Roles Assignment**:
```
In #incident-123 channel:

@john IC
@sarah Tech Lead  
@mike Comms Lead
```

## Investigation Process

### Gather Information

**Check these first**:
1. Recent deployments
2. Database performance
3. External service status
4. Error logs
5. Monitoring dashboards

**Useful Commands**:
```bash
# Recent deployments
kubectl rollout history deployment/api -n production

# Current pods and restarts
kubectl get pods -n production -o wide

# Recent errors
kubectl logs -n production deployment/api --since=30m | grep ERROR

# Database connections
psql $DATABASE_URL -c "
  SELECT pid, state, query_start, query 
  FROM pg_stat_activity 
  WHERE state != 'idle' 
  ORDER BY query_start;
"

# Redis connection test
redis-cli -h $REDIS_HOST ping

# Check disk space
df -h

# Check memory
free -h

# Recent deployments from git
git log --oneline --since="2 hours ago" origin/main
```

**Check External Services**:
- AWS Status: https://status.aws.amazon.com/
- Stripe Status: https://status.stripe.com/
- DataDog Status: https://status.datadoghq.com/

### Common Issues Checklist

- [ ] Recent deployment?
- [ ] Database connection pool exhausted?
- [ ] Redis connection issues?
- [ ] API rate limit hit?
- [ ] SSL certificate expired?
- [ ] Disk space full?
- [ ] Memory exhausted?
- [ ] External service down?
- [ ] DDoS attack?
- [ ] Configuration change?

## Mitigation vs. Resolution

### Mitigation: Stop the Bleeding

**Goal**: Reduce impact quickly, even if not a full fix

**Common Mitigations**:
1. **Rollback deployment**
   ```bash
   # Roll back to previous version
   kubectl rollout undo deployment/api -n production
   kubectl rollout status deployment/api -n production
   ```

2. **Scale up resources**
   ```bash
   # Increase replicas
   kubectl scale deployment/api --replicas=10 -n production
   ```

3. **Disable problematic feature**
   ```python
   # Feature flag in admin panel or database
   UPDATE feature_flags SET enabled = false WHERE name = 'new_checkout';
   ```

4. **Increase resource limits**
   ```bash
   # Edit deployment with more memory/CPU
   kubectl edit deployment/api -n production
   ```

5. **Clear cache**
   ```bash
   redis-cli -h $REDIS_HOST FLUSHALL
   ```

6. **Kill long-running queries**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'active' AND query_start < now() - interval '5 minutes';
   ```

### Resolution: Fix the Root Cause

**After mitigation**, work on proper fix:
1. Identify root cause
2. Develop fix
3. Test in staging
4. Deploy to production
5. Monitor closely

## Communication During Incident

### Internal Updates

**Frequency**:
- SEV1: Every 15-30 minutes
- SEV2: Every 30-60 minutes
- SEV3: When there's something to say

**Update Template**:
```
Status Update - 10:45am

Current Status: Still investigating
Impact: ~50% of users seeing slow response times
What we know: Database connection pool saturation
What we're doing: Scaling up DB connections, investigating queries
ETA: Unknown, investigating
Next update: 11:00am
```

### External Communication (SEV1/SEV2)

**Status Page Updates**:
1. **Incident identified**: "We're investigating reports of..."
2. **Investigating**: "We've identified the issue and are working on a fix..."
3. **Monitoring**: "A fix has been deployed and we're monitoring..."
4. **Resolved**: "The issue has been resolved..."

**Customer Support**:
- Post in #customer-support with status
- Provide template responses
- Keep them updated

## Incident Resolution

### When to Mark Resolved

- [ ] Root cause identified
- [ ] Fix deployed and verified
- [ ] Metrics back to normal
- [ ] Monitoring for 30+ minutes (SEV1)
- [ ] No user reports

### Close-Out Checklist

- [ ] Mark incident resolved in PagerDuty
- [ ] Update status page to "Resolved"
- [ ] Post final update in #incidents
- [ ] Thank responders
- [ ] Schedule post-mortem (within 48 hours)

## Post-Incident Activities

### Immediate (Same Day)

1. **Document timeline** in incident channel
   - What happened when
   - Actions taken
   - Impact duration
   - Key decision points

2. **Create tracking issue** for follow-up work
   ```markdown
   ## Follow-up from Incident #123
   
   Root cause: Database connection pool exhausted
   
   Action items:
   - [ ] Increase default connection pool size
   - [ ] Add alerting for connection pool usage
   - [ ] Review slow queries
   - [ ] Add circuit breaker pattern
   ```

### Post-Mortem Meeting (Within 48 Hours)

**Attendees**: Incident responders + stakeholders

**Blameless Culture**: Focus on systems and processes, not individuals

**Agenda**:
1. Timeline review
2. Root cause analysis (5 Whys)
3. What went well
4. What could be better
5. Action items

**5 Whys Example**:
```
Problem: API returned 500 errors

Why? Database queries timed out
Why? Connection pool was exhausted  
Why? New feature made 10x more queries than expected
Why? We didn't load test the feature
Why? We don't have automated load testing

Root cause: No load testing process
Action: Implement automated load testing in CI
```

### Post-Mortem Document

**Template**:
```markdown
# Incident Post-Mortem: [Title]

**Date**: 2024-01-15
**Duration**: 2 hours 15 minutes
**Severity**: SEV1
**Impact**: All users unable to place orders

## Summary
Brief description of what happened

## Timeline
- 10:00am: Deployment started
- 10:15am: First error reports
- 10:30am: Incident declared
- 10:45am: Root cause identified
- 11:00am: Rollback completed
- 12:15pm: Proper fix deployed

## Root Cause
Detailed explanation

## Impact
- 10,000 affected users
- $50,000 estimated lost revenue
- 2,000 support tickets

## What Went Well
- Fast detection (15 minutes)
- Quick rollback decision
- Good communication

## What Could Be Better
- Earlier load testing
- Better monitoring
- Automated rollback

## Action Items
- [ ] Add load testing (@john, Due: 2024-01-22)
- [ ] Add connection pool monitoring (@sarah, Due: 2024-01-18)
- [ ] Document rollback procedure (@mike, Due: 2024-01-20)

## Lessons Learned
Key takeaways
```

## Common Incident Scenarios

### Scenario 1: Application Crash Loop

**Symptoms**: Pods constantly restarting

**Investigation**:
```bash
kubectl get pods -n production
kubectl logs -n production pod/api-abc123 --previous
```

**Common Causes**:
- Startup probe failure
- Out of memory
- Uncaught exception on startup
- Missing environment variable

**Mitigation**: Rollback deployment

### Scenario 2: Database Connection Issues

**Symptoms**: "connection pool exhausted" errors

**Investigation**:
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check connection limit
SHOW max_connections;

-- Long-running queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

**Mitigation**: 
- Kill long queries
- Scale up connection pool
- Restart application

### Scenario 3: High Error Rate

**Symptoms**: 500 errors spike in Sentry

**Investigation**:
- Check Sentry for error patterns
- Review recent deployments
- Check external service status

**Mitigation**:
- Rollback if caused by deployment
- Add circuit breaker for external services
- Scale up if traffic spike

### Scenario 4: Slow Response Times

**Symptoms**: API latency >5s

**Investigation**:
- Check DataDog APM traces
- Review database query times
- Check external API calls
- Look for N+1 queries

**Mitigation**:
- Add caching
- Optimize slow queries
- Scale horizontally

## Escalation

**When to escalate**:
- Can't resolve within 30 minutes (SEV1)
- Need expertise from another team
- Need leadership decision
- Need to page additional people

**How to escalate**:
```
/escalate in #incident-123

Reason: Need database expertise, queries are slow
Team: @database-team
```

## Prevention

**Better than responding to incidents: preventing them**

1. **Pre-deployment checks**
   - Run full test suite
   - Load test major changes
   - Review monitoring before deploy
   - Deploy during business hours

2. **Monitoring**
   - Set up alerts for key metrics
   - Use SLIs and SLOs
   - Synthetic monitoring
   - Log aggregation

3. **Gradual rollouts**
   - Canary deployments
   - Feature flags
   - Blue/green deployments

4. **Chaos engineering**
   - Regular game days
   - Test failure scenarios
   - Practice incident response

## On-Call Best Practices

### Before Your Shift

- [ ] Test PagerDuty notification
- [ ] Review recent incidents
- [ ] Check runbooks are up to date
- [ ] Ensure laptop is charged
- [ ] VPN credentials working

### During Your Shift

- [ ] Respond to pages within 5 minutes
- [ ] Keep laptop nearby
- [ ] Stay relatively sober
- [ ] Don't leave town without backup

### After Your Shift

- [ ] Handoff to next person
- [ ] Document any ongoing issues
- [ ] Update runbooks if needed

## Resources

- **Runbooks**: `/docs/runbooks/`
- **Monitoring**: https://app.datadoghq.com
- **Logs**: https://logs.company.com
- **Status Page**: https://status.company.com
- **PagerDuty**: https://company.pagerduty.com
- **Incident Retros**: `/docs/post-mortems/`

## Getting Help

- **Urgent (during incident)**: Page in #incidents
- **Questions about on-call**: #oncall channel
- **Update runbooks**: PR to `/docs/runbooks/`
- **Incident feedback**: Talk to your manager
