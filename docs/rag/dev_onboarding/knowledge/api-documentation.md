# Internal API Documentation

## API Overview

Our internal API is built with **FastAPI** and follows RESTful principles. All endpoints require authentication except for `/health` and `/docs`.

**Base URL**:
- Development: `http://localhost:8000`
- Staging: `https://api-staging.company.com`
- Production: `https://api.company.com`

**API Documentation**:
- OpenAPI/Swagger UI: `{base_url}/docs`
- ReDoc: `{base_url}/redoc`
- OpenAPI JSON: `{base_url}/openapi.json`

## Authentication

All API requests require a JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Getting a Token

```bash
curl -X POST https://api.company.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

```bash
curl -X GET https://api.company.com/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Core API Endpoints

### Health Check

```http
GET /health
```

Returns server health status. No authentication required.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.2.3",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "name": "John Doe"
}
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <token>
```

### User Endpoints

#### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

#### Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer <token>
```

#### Update User
```http
PUT /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

#### Delete User
```http
DELETE /users/{user_id}
Authorization: Bearer <token>
```

### Order Endpoints

#### List Orders
```http
GET /orders?page=1&page_size=20&status=completed
Authorization: Bearer <token>
```

**Query Parameters**:
- `page` (int): Page number, default 1
- `page_size` (int): Items per page, default 20, max 100
- `status` (string): Filter by status (pending, completed, cancelled)

**Response**:
```json
{
  "items": [
    {
      "id": 456,
      "user_id": 123,
      "total": 99.99,
      "status": "completed",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

#### Create Order
```http
POST /orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102"
  }
}
```

#### Get Order Details
```http
GET /orders/{order_id}
Authorization: Bearer <token>
```

#### Cancel Order
```http
POST /orders/{order_id}/cancel
Authorization: Bearer <token>
```

### Payment Endpoints

#### Process Payment
```http
POST /payments
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 456,
  "payment_method": "credit_card",
  "stripe_token": "tok_visa"
}
```

#### Get Payment Status
```http
GET /payments/{payment_id}
Authorization: Bearer <token>
```

## Request/Response Format

### Standard Response Format

**Success Response**:
```json
{
  "data": {
    // Resource data
  },
  "message": "Success"
}
```

**Error Response**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

### HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

**Limits**:
- Anonymous: 100 requests per hour
- Authenticated: 1000 requests per hour
- Premium: 5000 requests per hour

**Response Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705318800
```

**Rate Limit Exceeded Response**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 3600
  }
}
```

## Pagination

All list endpoints support pagination:

```http
GET /orders?page=2&page_size=50
```

**Response includes pagination metadata**:
```json
{
  "items": [...],
  "total": 500,
  "page": 2,
  "page_size": 50,
  "pages": 10,
  "has_next": true,
  "has_prev": true
}
```

## Filtering and Sorting

### Filtering

```http
GET /users?is_active=true&created_after=2024-01-01
GET /orders?status=completed&min_amount=100
```

### Sorting

```http
GET /users?sort=created_at:desc
GET /orders?sort=total:asc,created_at:desc
```

## Error Handling

### Validation Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ]
  }
}
```

### Business Logic Errors

```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Cannot process payment: insufficient funds",
    "details": {
      "required": 99.99,
      "available": 50.00
    }
  }
}
```

## Making API Calls from Code

### Python (requests)

```python
import requests

# Get token
response = requests.post(
    'https://api.company.com/auth/login',
    json={'email': 'user@example.com', 'password': 'password123'}
)
token = response.json()['access_token']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'https://api.company.com/users/me',
    headers=headers
)
user = response.json()
```

### Python (httpx - async)

```python
import httpx

async def get_user():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            'https://api.company.com/auth/login',
            json={'email': 'user@example.com', 'password': 'password123'}
        )
        token = response.json()['access_token']
        
        # Get user
        response = await client.get(
            'https://api.company.com/users/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        return response.json()
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('https://api.company.com/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const {access_token} = await loginResponse.json();

// Make authenticated request
const response = await fetch('https://api.company.com/users/me', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
const user = await response.json();
```

## Testing API Endpoints

### Using cURL

```bash
# Set token as variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Make request
curl -X GET https://api.company.com/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Using HTTPie

```bash
# More readable than curl
http GET https://api.company.com/users/me \
  Authorization:"Bearer $TOKEN"

# POST request
http POST https://api.company.com/orders \
  Authorization:"Bearer $TOKEN" \
  items:='[{"product_id":1,"quantity":2}]'
```

### Using Postman

1. Import OpenAPI spec from `/openapi.json`
2. Set up environment variables for tokens
3. Create collection with common requests
4. Share collection with team

## API Versioning

We use URL-based versioning:
- Current version: `/v1/`
- Next version (beta): `/v2/`

```http
GET https://api.company.com/v1/users/me
GET https://api.company.com/v2/users/me
```

**Deprecation Policy**:
- New version announced 3 months before release
- Old version supported for 6 months after new version released
- Deprecation warnings in response headers

## Webhooks

Subscribe to events via webhooks:

```http
POST /webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://yourapp.com/webhook",
  "events": ["order.created", "payment.completed"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload**:
```json
{
  "event": "order.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "order_id": 456,
    "user_id": 123,
    "total": 99.99
  }
}
```

## Best Practices

### DO ✓

1. **Use pagination** for list endpoints
2. **Handle rate limits** with exponential backoff
3. **Validate tokens** before making requests
4. **Use HTTPS** in production
5. **Log API errors** for debugging
6. **Set timeouts** on requests
7. **Cache responses** when appropriate

### DON'T ✗

1. **Don't hardcode tokens** - use environment variables
2. **Don't ignore errors** - always check status codes
3. **Don't retry immediately** - use backoff strategy
4. **Don't log sensitive data** - passwords, tokens, etc.
5. **Don't send large payloads** - use pagination/chunking

## Getting Help

- **API Documentation**: `/docs` endpoint
- **API Issues**: #api-help channel
- **Authentication Problems**: #auth-team
- **Rate Limit Increases**: Submit request to API team
- **Breaking Changes**: Announced in #api-announcements
