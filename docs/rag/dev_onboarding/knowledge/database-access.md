# Database Access Guide

## Database Overview

We use **PostgreSQL 15** as our primary database with **Redis** for caching.

### Connection Details

**Development** (Local):
```
Host: localhost
Port: 5432
Database: company_dev
User: postgres
Password: postgres
```

**Staging**:
```
Host: staging-db.company.internal
Port: 5432
Database: company_staging
User: app_user
Password: (from AWS Secrets Manager)
```

**Production**:
```
Host: prod-db.company.internal
Port: 5432  
Database: company_prod
User: app_user
Password: (from AWS Secrets Manager)
```

## Connecting to Databases

### Using psql CLI

```bash
# Local development
psql postgresql://postgres:postgres@localhost:5432/company_dev

# Staging (via bastion/VPN)
psql postgresql://app_user:PASSWORD@staging-db.company.internal:5432/company_staging

# Production (read-only access, requires approval)
psql postgresql://readonly_user:PASSWORD@prod-db.company.internal:5432/company_prod
```

### Using Database Client (DBeaver, DataGrip, etc.)

1. Open your SQL client
2. Create new PostgreSQL connection
3. Enter connection details above
4. Test connection
5. Save

### From Python Code

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get connection string from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Common Database Operations

### Viewing Tables

```sql
-- List all tables
\dt

-- Describe table structure
\d users

-- Show table with indexes
\d+ users

-- List all schemas
\dn

-- Show current database
SELECT current_database();
```

### Querying Data

```sql
-- Select users
SELECT id, email, created_at 
FROM users 
WHERE is_active = true 
LIMIT 10;

-- Join tables
SELECT u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.email
ORDER BY order_count DESC
LIMIT 10;

-- Check recent activity
SELECT * FROM users 
WHERE created_at > NOW() - INTERVAL '1 day'
ORDER BY created_at DESC;
```

### Database Performance

```sql
-- Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 20;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find missing indexes (tables doing sequential scans)
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan as avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;
```

## Database Migrations

We use **Alembic** for database migrations.

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user preferences table"

# Create empty migration (for data migrations)
alembic revision -m "Backfill user data"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by one version
alembic upgrade +1

# Downgrade by one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Migration File Example

```python
"""Add user preferences table

Revision ID: abc123def456
Create Date: 2024-01-15 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(20), default='light'),
        sa.Column('notifications_enabled', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])

def downgrade():
    op.drop_index('ix_user_preferences_user_id')
    op.drop_table('user_preferences')
```

## Database Best Practices

### DO ✓

1. **Use transactions** for multi-step operations
2. **Add indexes** on frequently queried columns
3. **Use connection pooling** (already configured)
4. **Close connections** after use
5. **Use parameterized queries** (ORM does this automatically)
6. **Test migrations** in staging before production

### DON'T ✗

1. **Don't query in loops** (N+1 problem)
2. **Don't SELECT \*** - specify columns
3. **Don't store sensitive data unencrypted**
4. **Don't run production queries in development**
5. **Don't modify production data without approval**
6. **Don't create indexes without testing impact**

## Backup and Recovery

### Backups

**Automated backups** run daily at 2 AM UTC:
- Retention: 30 days
- Stored in S3
- Encrypted at rest

**Manual backup**:
```bash
# Backup database
pg_dump -h localhost -U postgres company_dev > backup.sql

# Backup specific table
pg_dump -h localhost -U postgres -t users company_dev > users_backup.sql

# Backup with compression
pg_dump -h localhost -U postgres company_dev | gzip > backup.sql.gz
```

### Restore

```bash
# Restore from backup
psql -h localhost -U postgres company_dev < backup.sql

# Restore with gzip
gunzip -c backup.sql.gz | psql -h localhost -U postgres company_dev

# Restore specific table
psql -h localhost -U postgres company_dev < users_backup.sql
```

## Redis Cache

### Connecting to Redis

```bash
# Local
redis-cli

# Staging
redis-cli -h staging-redis.company.internal -p 6379 -a PASSWORD

# Production (read-only)
redis-cli -h prod-redis.company.internal -p 6379 -a PASSWORD
```

### Common Redis Commands

```bash
# View all keys (don't use in production!)
KEYS *

# Better: scan with cursor
SCAN 0 MATCH user:* COUNT 100

# Get value
GET user:12345

# Set value with expiration (in seconds)
SET user:12345 "{\"name\":\"John\"}" EX 3600

# Delete key
DEL user:12345

# Check if key exists
EXISTS user:12345

# Get TTL (time to live)
TTL user:12345

# Check memory usage
INFO memory

# Clear all data (DANGEROUS!)
FLUSHALL
```

### Using Redis from Python

```python
import redis
import json

# Create Redis client
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Set value with expiration
redis_client.setex(
    'user:12345',
    3600,  # 1 hour
    json.dumps({'name': 'John', 'email': 'john@example.com'})
)

# Get value
user_data = redis_client.get('user:12345')
if user_data:
    user = json.loads(user_data)

# Delete
redis_client.delete('user:12345')

# Pattern-based deletion
for key in redis_client.scan_iter('user:*'):
    redis_client.delete(key)
```

## Database Access Permissions

### Development
- Full access to local database
- Can create/modify/delete any data

### Staging
- Read/write access
- Can test data operations
- Ask team lead for credentials

### Production
- **Default**: NO direct access
- **Read-only**: Approved users only (analysts, senior engineers)
- **Write access**: Only through application or approved migration scripts
- **Emergency access**: Requires VP Engineering approval

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -h localhost -U postgres -c "SELECT 1"

# Check if database is running
systemctl status postgresql

# Check connection limit
SELECT count(*) FROM pg_stat_activity;
SELECT max_connections FROM pg_settings WHERE name = 'max_connections';
```

### Performance Issues

```bash
# Check active queries
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE state != 'idle' 
AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start DESC;

# Kill long-running query
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE pid = 12345;

# Check locks
SELECT * FROM pg_locks WHERE NOT granted;
```

## Getting Help

- **Database issues**: #database-help channel
- **Migration problems**: Database team lead
- **Production access**: Submit request via https://access.company.com
- **Performance tuning**: Senior backend engineer or DBA
- **Emergency database issues**: Page on-call via PagerDuty
