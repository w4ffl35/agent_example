# Coding Standards

## General Principles

1. **Readability over cleverness** - Code is read 10x more than written
2. **Consistency matters** - Follow existing patterns in the codebase
3. **Simple beats complex** - Prefer straightforward solutions
4. **Test your code** - If it's not tested, it's broken
5. **Document the why** - Code shows how, comments explain why

## Python Code Standards

### Formatting

We use **Black** for automatic code formatting:

```bash
# Format your code
black .

# Check without modifying
black --check .
```

**Configuration** (in `pyproject.toml`):
- Line length: 88 characters (Black default)
- Python version: 3.11+
- String normalization: Double quotes

### Linting

We use **Ruff** for fast linting and import sorting:

```bash
# Run linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

**Key Rules**:
- No unused imports or variables
- No mutable default arguments
- Proper exception handling
- Security best practices (no SQL injection, XSS, etc.)

### Type Hints

All new code must include type hints:

```python
# Good ✓
def calculate_total(items: list[dict], tax_rate: float) -> float:
    """Calculate total price including tax."""
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)

# Bad ✗
def calculate_total(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
```

We use **mypy** for type checking:

```bash
# Check types
mypy .
```

Configuration in `pyproject.toml`:
- Strict mode enabled
- No implicit optionals
- Warn on unused ignores

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def process_payment(
    amount: float,
    payment_method: str,
    user_id: int
) -> dict:
    """Process a payment transaction.
    
    This function handles payment processing through various payment
    gateways and records the transaction in the database.
    
    Args:
        amount: Payment amount in USD
        payment_method: Payment method ('credit_card', 'paypal', etc.)
        user_id: ID of the user making the payment
        
    Returns:
        Dictionary containing transaction details:
        {
            'transaction_id': str,
            'status': str,
            'timestamp': datetime
        }
        
    Raises:
        PaymentError: If payment processing fails
        InvalidAmountError: If amount is negative or zero
        
    Example:
        >>> result = process_payment(99.99, 'credit_card', 12345)
        >>> result['status']
        'completed'
    """
    pass
```

**Docstring Line Length**: Maximum 72 characters (shorter than code)

### Naming Conventions

```python
# Variables and functions: snake_case
user_name = "John"
def get_user_data(): pass

# Classes: PascalCase
class UserProfile: pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
API_BASE_URL = "https://api.company.com"

# Private methods/attributes: _leading_underscore
def _internal_helper(): pass
self._cache = {}

# "Protected" (name mangling): __double_underscore
def __private_method(self): pass
```

### Import Organization

Imports should be organized in this order:

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import requests
from django.db import models

# 3. Local application imports
from app.models import User
from app.utils import calculate_total
```

Ruff automatically sorts imports - just run `ruff check --fix .`

### Error Handling

Be specific with exceptions:

```python
# Good ✓
try:
    data = json.loads(response.text)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    raise APIError("Failed to parse API response")

# Bad ✗
try:
    data = json.loads(response.text)
except Exception:
    pass  # Silent failure
```

**Never use bare `except:`** - always specify the exception type.

### Code Organization

```python
class UserService:
    """Service for user-related operations.
    
    Public methods should be listed first, followed by
    private helper methods.
    """
    
    # 1. Class constants
    MAX_LOGIN_ATTEMPTS = 3
    
    # 2. __init__ and setup methods
    def __init__(self, db_connection):
        self.db = db_connection
        self._cache = {}
    
    # 3. Public methods
    def create_user(self, email: str, password: str) -> User:
        """Create a new user account."""
        pass
    
    def get_user(self, user_id: int) -> User:
        """Retrieve user by ID."""
        pass
    
    # 4. Private helper methods
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pass
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        pass
```

## Testing Standards

### Test File Structure

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with database/external services
└── e2e/           # End-to-end tests
```

### Test Naming

```python
def test_calculate_total_with_positive_amounts():
    """Test that total is calculated correctly with positive amounts."""
    pass

def test_calculate_total_raises_error_with_negative_amount():
    """Test that negative amounts raise ValueError."""
    pass
```

Pattern: `test_<function_name>_<scenario>_<expected_result>`

### Test Coverage

- **Minimum**: 80% code coverage for new code
- **Target**: 90%+ for critical business logic
- Run coverage report: `pytest --cov=app --cov-report=html`

### Writing Good Tests

```python
import pytest
from app.services import PaymentService

class TestPaymentService:
    """Tests for PaymentService class."""
    
    @pytest.fixture
    def payment_service(self):
        """Create a payment service instance for testing."""
        return PaymentService(api_key="test_key")
    
    def test_process_payment_success(self, payment_service):
        """Test successful payment processing."""
        # Arrange
        amount = 99.99
        payment_method = "credit_card"
        
        # Act
        result = payment_service.process_payment(
            amount=amount,
            payment_method=payment_method
        )
        
        # Assert
        assert result['status'] == 'completed'
        assert result['amount'] == amount
    
    def test_process_payment_invalid_amount(self, payment_service):
        """Test that negative amounts raise ValueError."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            payment_service.process_payment(
                amount=-10.00,
                payment_method="credit_card"
            )
```

Use the **Arrange-Act-Assert** pattern for clarity.

## Code Review Checklist

Before submitting a PR, verify:

- [ ] Code is formatted with Black
- [ ] Ruff linting passes
- [ ] Type hints added for new functions
- [ ] Docstrings added for public functions
- [ ] Tests written and passing
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is appropriate
- [ ] Logging added for important operations
- [ ] No commented-out code
- [ ] Commit messages are descriptive

## Common Anti-Patterns to Avoid

### 1. God Classes
```python
# Bad ✗ - One class doing too much
class User:
    def authenticate(self): pass
    def send_email(self): pass
    def process_payment(self): pass
    def generate_report(self): pass
```

**Solution**: Split into focused classes (User, EmailService, PaymentService, ReportGenerator)

### 2. Mutable Default Arguments
```python
# Bad ✗
def add_item(item, items=[]):
    items.append(item)
    return items

# Good ✓
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 3. Catching All Exceptions
```python
# Bad ✗
try:
    risky_operation()
except:
    pass

# Good ✓
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### 4. Not Using Context Managers
```python
# Bad ✗
file = open('data.txt')
data = file.read()
file.close()

# Good ✓
with open('data.txt') as file:
    data = file.read()
```

## Performance Guidelines

1. **Use list comprehensions** over loops when appropriate
2. **Avoid premature optimization** - profile before optimizing
3. **Use generators** for large datasets
4. **Cache expensive computations** (with functools.lru_cache)
5. **Use database indexes** for frequent queries
6. **Batch database operations** instead of N+1 queries

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Validate all user input** - Never trust external data
3. **Use parameterized queries** - Prevent SQL injection
4. **Sanitize output** - Prevent XSS attacks
5. **Use HTTPS** for all external API calls
6. **Hash passwords** with bcrypt, never store plaintext

## Tools Setup

Add to your `Makefile`:

```makefile
format:
	black .
	ruff check --fix .

lint:
	black --check .
	ruff check .
	mypy .

test:
	pytest --cov=app --cov-report=term-missing

check: lint test
```

Run before committing:
```bash
make check
```

## Questions?

- **Style questions**: Check this guide first, then ask in #engineering
- **Tool issues**: See #devops
- **Disagreements**: Bring to tech lead for decision
