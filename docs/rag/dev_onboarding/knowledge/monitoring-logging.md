# Monitoring and Logging Guide

## Monitoring Tools

### DataDog (Application Performance Monitoring)

**Dashboard**: https://app.datadoghq.com/dashboard/company-app

**Key Dashboards**:
- **Application Overview**: Request rates, response times, error rates
- **Database Performance**: Query times, connection pool usage
- **Infrastructure**: CPU, memory, disk usage
- **Business Metrics**: User signups, orders, revenue

**Setting Up Alerts**:
```python
# DataDog monitors are configured in Terraform
# See: terraform/monitoring/datadog.tf

# Example: High error rate alert
resource "datadog_monitor" "high_error_rate" {
  name    = "High Error Rate"
  type    = "metric alert"
  message = "Error rate is above 1% @pagerduty-critical"
  query   = "avg(last_5m):sum:app.errors{env:production} > 100"
}
```

### Grafana (Metrics Visualization)

**Dashboard**: https://grafana.company.com

**Common Queries**:
```promql
# Request rate
rate(http_requests_total[5m])

# P95 response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate percentage
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m]) * 100
```

### CloudWatch (AWS Logs and Metrics)

**Logs**: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups

**Log Groups**:
- `/ecs/app-service` - Application logs
- `/ecs/celery-worker` - Background job logs
- `/aws/rds/instance/production` - Database logs

## Application Logging

### Log Levels

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG - Detailed diagnostic information (dev only)
logger.debug(f"Processing user ID: {user_id}")

# INFO - General informational messages
logger.info("User created successfully", extra={"user_id": user.id})

# WARNING - Warning messages (potential issues)
logger.warning("Rate limit approaching", extra={"ip": request.ip})

# ERROR - Error messages (caught exceptions)
logger.error("Payment processing failed", exc_info=True)

# CRITICAL - Critical issues (system failures)
logger.critical("Database connection lost", extra={"db": "primary"})
```

### Structured Logging

**Always use structured logging** for easier querying:

```python
# Good ✓
logger.info(
    "Order processed",
    extra={
        "order_id": order.id,
        "user_id": user.id,
        "amount": order.total,
        "duration_ms": elapsed_time
    }
)

# Bad ✗
logger.info(f"Order {order.id} processed for user {user.id} amount {order.total}")
```

### Logging Configuration

```python
# app/core/logging.py
import logging.config
import json

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    },
    "loggers": {
        "app": {
            "level": "DEBUG" if DEBUG else "INFO"
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## Querying Logs

### CloudWatch Insights Queries

**Find errors in last hour**:
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

**Count errors by endpoint**:
```
fields @timestamp, path, status_code
| filter status_code >= 500
| stats count() by path
| sort count desc
```

**Slow queries (>1 second)**:
```
fields @timestamp, query, duration_ms
| filter duration_ms > 1000
| sort duration_ms desc
```

**Track specific user activity**:
```
fields @timestamp, @message, user_id
| filter user_id = "12345"
| sort @timestamp desc
```

### DataDog Log Search

```
# Find all errors in production
status:error env:production

# Payment failures
service:payment status:error

# Slow database queries
service:database @duration:>1000

# Specific user actions
@user_id:12345 service:api
```

## Metrics and Instrumentation

### Custom Metrics

```python
from datadog import statsd

# Increment counter
statsd.increment('app.user.signup', tags=['source:web'])

# Record timing
with statsd.timed('app.payment.process'):
    process_payment(order)

# Set gauge
statsd.gauge('app.queue.length', queue.size())

# Record histogram
statsd.histogram('app.order.value', order.total)
```

### Request Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.post("/orders")
async def create_order(order: OrderCreate):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.items", len(order.items))
        span.set_attribute("user.id", current_user.id)
        
        # Nested span for database operation
        with tracer.start_as_current_span("save_to_db"):
            db_order = save_order(order)
        
        # Nested span for external API
        with tracer.start_as_current_span("process_payment"):
            payment = process_payment(db_order)
        
        return db_order
```

## Monitoring Best Practices

### Key Metrics to Track

**Golden Signals** (from Google SRE):
1. **Latency** - Request/response time
2. **Traffic** - Request rate
3. **Errors** - Error rate
4. **Saturation** - Resource utilization

**RED Method**:
- **Rate** - Requests per second
- **Errors** - Failed requests per second
- **Duration** - Request duration

**USE Method** (for resources):
- **Utilization** - % time resource is busy
- **Saturation** - Queue length/wait time
- **Errors** - Error count

### Alert Thresholds

```yaml
# Example alert configuration
alerts:
  - name: High Error Rate
    condition: error_rate > 1%
    duration: 5 minutes
    severity: critical
    notify: pagerduty
    
  - name: Slow Response Time
    condition: p95_latency > 1000ms
    duration: 10 minutes
    severity: warning
    notify: slack
    
  - name: High CPU Usage
    condition: cpu_usage > 80%
    duration: 15 minutes
    severity: warning
    notify: slack
    
  - name: Database Connection Pool Exhausted
    condition: db_connections_available < 5
    duration: 2 minutes
    severity: critical
    notify: pagerduty
```

### Dashboard Organization

**Service Dashboard Structure**:
1. **Overview** - High-level metrics (traffic, errors, latency)
2. **Errors** - Error rates, types, recent errors
3. **Performance** - Response times, slow endpoints
4. **Infrastructure** - CPU, memory, network
5. **Business** - User signups, orders, revenue

## Debugging Production Issues

### Step 1: Check Dashboard

1. Go to monitoring dashboard
2. Look for anomalies in traffic, errors, or latency
3. Check if issue is isolated to specific endpoints

### Step 2: Check Recent Deployments

```bash
# Check recent deployments
gh api repos/company/app/deployments --jq '.[] | {created_at, environment, sha}'

# Check what changed
git log --oneline origin/main~10..origin/main
```

### Step 3: Check Logs

```bash
# Tail production logs
aws logs tail /ecs/app-service --follow --filter-pattern "ERROR"

# Or in CloudWatch Insights
# Use queries from "Querying Logs" section above
```

### Step 4: Check Metrics

Look for correlation:
- Did traffic spike before errors started?
- Did database query time increase?
- Is CPU/memory maxed out?

### Step 5: Check External Services

```bash
# Check Stripe status
curl https://status.stripe.com/api/v2/status.json

# Check AWS status
curl https://status.aws.amazon.com/data.json
```

## Performance Monitoring

### Database Query Performance

```python
# Slow query logging (configured in Postgres)
# Logs queries taking >500ms

# Find slow queries in logs
fields @timestamp, query, duration
| filter duration > 500
| sort duration desc
```

**Common Issues**:
- Missing indexes
- N+1 query problem
- Full table scans
- Connection pool exhaustion

### API Endpoint Performance

```python
# Middleware to track endpoint performance
@app.middleware("http")
async def add_performance_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(duration)
    
    # Log slow requests
    if duration > 1.0:
        logger.warning(
            "Slow request",
            extra={
                "path": request.url.path,
                "duration": duration,
                "method": request.method
            }
        )
    
    return response
```

## Alerting Best Practices

### DO ✓

1. **Alert on symptoms, not causes** - Alert on user impact, not just metrics
2. **Have actionable alerts** - Every alert should have a clear response
3. **Avoid alert fatigue** - Don't alert on every minor issue
4. **Use different severity levels** - Critical (page), Warning (ticket), Info (log)
5. **Include context** - Alert should have runbook link and relevant metrics

### DON'T ✗

1. **Don't alert on everything** - Focus on customer-impacting issues
2. **Don't use same channel for all alerts** - Critical ≠ Warning
3. **Don't have vague alerts** - "Something is wrong" isn't helpful
4. **Don't forget runbooks** - Alerts need context and instructions
5. **Don't ignore flapping alerts** - Fix them or adjust thresholds

## Incident Response

### When You Get Alerted

1. **Acknowledge** the alert (PagerDuty/Slack)
2. **Assess severity** - Is service down? Degraded? Just slow?
3. **Check dashboards** - What's actually happening?
4. **Check recent changes** - Was there a recent deploy?
5. **Mitigate** - Rollback, scale up, disable feature
6. **Communicate** - Update #incidents channel
7. **Fix** - Address root cause
8. **Post-mortem** - Document what happened and how to prevent it

### Incident Severity Levels

**SEV-1 (Critical)**
- Service completely down
- Data loss
- Security breach
- **Response**: Immediate, page on-call

**SEV-2 (High)**
- Major functionality broken
- Significant performance degradation
- **Response**: Within 30 minutes

**SEV-3 (Medium)**
- Minor functionality impaired
- Some users affected
- **Response**: Next business day

**SEV-4 (Low)**
- Minor issues
- Single user affected
- **Response**: Backlog/next sprint

## Resources and Tools

### Monitoring Dashboards

- **DataDog**: https://app.datadoghq.com
- **Grafana**: https://grafana.company.com
- **CloudWatch**: https://console.aws.amazon.com/cloudwatch
- **Status Page**: https://status.company.com

### Documentation

- **DataDog Docs**: https://docs.datadoghq.com
- **CloudWatch Docs**: https://docs.aws.amazon.com/cloudwatch
- **OpenTelemetry**: https://opentelemetry.io/docs

### Getting Help

- **Monitoring issues**: #observability channel
- **Production incidents**: #incidents (page on-call if critical)
- **Dashboard questions**: #monitoring-help
- **Alert tuning**: DevOps team lead
