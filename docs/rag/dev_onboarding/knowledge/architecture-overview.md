# System Architecture Overview

## High-Level Architecture

Our application follows a **microservices-inspired monolith** architecture - we maintain separation of concerns and clear service boundaries while keeping everything in a single deployable unit for now.

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                     (AWS Application LB)                     │
└────────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
┌───────────▼──────────┐  ┌────────▼──────────┐
│   Web Server 1       │  │   Web Server 2    │
│   (FastAPI)          │  │   (FastAPI)       │
└───────────┬──────────┘  └────────┬──────────┘
            │                       │
            └───────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  PostgreSQL  │ │   Redis    │ │   S3       │
│  (Primary)   │ │   Cache    │ │   Storage  │
└──────────────┘ └────────────┘ └────────────┘
```

## Core Components

### 1. API Layer (FastAPI)

**Location**: `app/api/`

Handles HTTP requests and responses:
- RESTful API endpoints
- Request validation (Pydantic models)
- Authentication/Authorization
- Rate limiting
- API documentation (auto-generated OpenAPI)

**Key Files**:
- `app/api/routes/` - Endpoint definitions
- `app/api/dependencies.py` - Dependency injection
- `app/api/middleware.py` - Request/response middleware

### 2. Service Layer

**Location**: `app/services/`

Contains business logic:
- `UserService` - User management, authentication
- `PaymentService` - Payment processing
- `OrderService` - Order management
- `EmailService` - Email notifications
- `NotificationService` - Push notifications

**Design Pattern**: Service classes are injected as dependencies
```python
from app.services.user_service import UserService

def get_user_endpoint(
    user_id: int,
    user_service: UserService = Depends()
):
    return user_service.get_user(user_id)
```

### 3. Data Layer

**Location**: `app/models/` and `app/repositories/`

**Models**: SQLAlchemy ORM models
- Define database schema
- Handle relationships
- Validation at model level

**Repositories**: Data access layer
- Abstract database operations
- Reusable queries
- Transaction management

```python
# Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

# Repository
class UserRepository:
    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(
            User.email == email
        ).first()
```

### 4. Background Jobs

**Location**: `app/jobs/`

Asynchronous task processing using Celery:
- Email sending
- Report generation
- Data synchronization
- Scheduled tasks (cron-like)

**Example**:
```python
@celery_app.task
def send_welcome_email(user_id: int):
    user = get_user(user_id)
    send_email(
        to=user.email,
        subject="Welcome!",
        template="welcome"
    )
```

## Data Flow

### Typical Request Flow

```
1. Client Request → Load Balancer
2. Load Balancer → Web Server
3. Web Server → Middleware (auth, logging)
4. Middleware → API Route
5. API Route → Service Layer (business logic)
6. Service Layer → Repository (data access)
7. Repository → Database
8. Database → Repository (data returned)
9. Repository → Service Layer
10. Service Layer → API Route (response formatted)
11. API Route → Client (JSON response)
```

### With Caching

```
1. Client Request → API
2. API → Cache Check (Redis)
3. If Cache Hit:
   - Return cached response
4. If Cache Miss:
   - Query Database
   - Store in Cache
   - Return response
```

## Database Schema

### Core Tables

**users**
- `id` (PK)
- `email` (unique)
- `password_hash`
- `created_at`
- `updated_at`
- `is_active`

**orders**
- `id` (PK)
- `user_id` (FK → users)
- `status` (pending, completed, cancelled)
- `total_amount`
- `created_at`

**payments**
- `id` (PK)
- `order_id` (FK → orders)
- `amount`
- `payment_method`
- `stripe_charge_id`
- `status`
- `created_at`

### Relationships

```
User (1) ─── (N) Orders
Order (1) ─── (N) Payments
```

## External Services

### Stripe (Payment Processing)

```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def charge_payment(amount: int, token: str):
    return stripe.Charge.create(
        amount=amount,
        currency='usd',
        source=token
    )
```

### SendGrid (Email)

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to: str, subject: str, html: str):
    message = Mail(
        from_email='noreply@company.com',
        to_emails=to,
        subject=subject,
        html_content=html
    )
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    sg.send(message)
```

### AWS S3 (File Storage)

```python
import boto3

s3_client = boto3.client('s3')

def upload_file(file_data: bytes, key: str):
    s3_client.put_object(
        Bucket='company-uploads',
        Key=key,
        Body=file_data
    )
```

## Security Architecture

### Authentication Flow

```
1. User submits credentials (email/password)
2. Server validates credentials
3. Server generates JWT token
4. Client stores token (localStorage/cookie)
5. Client includes token in subsequent requests
6. Server validates token on each request
```

### JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": "2024-12-31T23:59:59Z",
  "roles": ["user"]
}
```

### API Security

- **HTTPS Only** - All traffic encrypted with TLS
- **CORS** - Configured to allow specific origins
- **Rate Limiting** - 100 requests/minute per IP
- **Input Validation** - Pydantic models validate all inputs
- **SQL Injection Protection** - ORM with parameterized queries
- **XSS Protection** - Output sanitization
- **CSRF Tokens** - For state-changing operations

## Caching Strategy

### What We Cache

- **User sessions** (Redis, TTL: 24 hours)
- **API responses** (Redis, TTL: 5 minutes)
- **Database query results** (Redis, TTL: varies)
- **Static assets** (CDN, indefinite)

### Cache Invalidation

```python
from app.cache import cache

# Set with TTL
cache.set('user:123', user_data, ttl=3600)

# Get
user_data = cache.get('user:123')

# Invalidate
cache.delete('user:123')

# Pattern-based invalidation
cache.delete_pattern('user:*')
```

## Monitoring & Observability

### Metrics (DataDog)

- **Application Metrics**:
  - Request rate (requests/second)
  - Response time (p50, p95, p99)
  - Error rate
  
- **System Metrics**:
  - CPU usage
  - Memory usage
  - Disk I/O
  
- **Business Metrics**:
  - User signups
  - Orders placed
  - Revenue

### Logging (CloudWatch)

```python
import logging

logger = logging.getLogger(__name__)

# Structured logging
logger.info(
    "User created",
    extra={
        "user_id": user.id,
        "email": user.email,
        "source": "api"
    }
)
```

**Log Levels**:
- DEBUG - Detailed diagnostic info (dev only)
- INFO - General informational messages
- WARNING - Warning messages (potential issues)
- ERROR - Error messages (caught exceptions)
- CRITICAL - Critical issues (system failures)

### Tracing (Distributed Tracing)

We use OpenTelemetry to trace requests across services:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_payment"):
    # This operation is traced
    payment = process_payment(order_id)
```

## Scalability Considerations

### Current Capacity

- **Traffic**: ~1000 requests/second
- **Users**: 100,000 active users
- **Database**: 500GB data
- **Response Time**: p95 < 200ms

### Scaling Strategies

#### Horizontal Scaling (Add More Servers)
- Load balancer distributes traffic
- Stateless application servers
- Shared database and cache

#### Vertical Scaling (Bigger Servers)
- Increase CPU/RAM
- Used for database initially

#### Database Scaling
1. **Read Replicas** - For read-heavy workloads
2. **Sharding** - Split data across multiple databases
3. **Connection Pooling** - Reuse database connections

#### Caching
- Redis for frequently accessed data
- Reduces database load
- Faster response times

## Deployment Architecture

### Environments

- **Development**: Developer laptops (local)
- **Staging**: AWS ECS (mirrors production)
- **Production**: AWS ECS (multi-AZ)

### Infrastructure as Code

We use Terraform to manage infrastructure:
```hcl
resource "aws_ecs_cluster" "main" {
  name = "company-app-cluster"
}

resource "aws_ecs_service" "app" {
  name            = "app-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
}
```

### Blue-Green Deployments

1. Deploy new version (green) alongside old version (blue)
2. Run smoke tests on green
3. Switch traffic to green
4. Monitor for issues
5. Keep blue running for quick rollback if needed
6. After 24 hours, terminate blue

## Technology Stack Summary

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic
- **Task Queue**: Celery
- **Message Broker**: Redis

### Database
- **Primary**: PostgreSQL 15
- **Cache**: Redis 7
- **Search**: Elasticsearch (future)

### Infrastructure
- **Cloud**: AWS
- **Compute**: ECS (Elastic Container Service)
- **Load Balancer**: Application Load Balancer
- **Storage**: S3
- **CDN**: CloudFront

### DevOps
- **CI/CD**: GitHub Actions
- **Container**: Docker
- **Orchestration**: ECS
- **Monitoring**: DataDog
- **Logs**: CloudWatch
- **Alerting**: PagerDuty

## Future Architecture Plans

### Short Term (Next 6 months)
1. Add read replicas for database
2. Implement full-text search with Elasticsearch
3. Add GraphQL API alongside REST
4. Implement event-driven architecture (publish/subscribe)

### Long Term (1-2 years)
1. Split into true microservices
2. Event sourcing for critical data
3. Multi-region deployment
4. Implement CQRS pattern

## Common Architectural Patterns

### Repository Pattern
Abstracts data access from business logic.

### Dependency Injection
Services are injected as needed, improving testability.

### Factory Pattern
Used for creating complex objects (e.g., payment processors).

### Strategy Pattern
Different algorithms for same operation (e.g., payment methods).

### Observer Pattern
Event notifications (e.g., order placed → send email).

## Performance Optimization

### Database Queries
- Use indexes on frequently queried columns
- Avoid N+1 queries (use joins or eager loading)
- Use database connection pooling
- Monitor slow queries

### Application
- Async I/O for external calls
- Batch operations when possible
- Use appropriate data structures
- Profile code for bottlenecks

### Frontend
- CDN for static assets
- Gzip compression
- Lazy loading
- Bundle optimization

## Questions?

- **Architecture decisions**: Ask tech lead or #architecture channel
- **Scaling questions**: #devops channel
- **Database design**: Database team lead
- **Security concerns**: Security team (#security-team)
