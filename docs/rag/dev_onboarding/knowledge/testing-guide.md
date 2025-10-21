# Testing Guide

## Testing Philosophy

**"If it's not tested, it's broken"** - We believe in comprehensive testing at multiple levels.

### Testing Pyramid

```
    /\
   /E2E\      <- Few, slow, expensive (5%)
  /------\
 /Integration\ <- Some, moderate speed (25%)
/------------\
/    Unit     \ <- Many, fast, cheap (70%)
```

## Running Tests

### Run All Tests

```bash
# Using pytest
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Parallel execution (faster)
pytest -n auto
```

### Run Specific Tests

```bash
# Single test file
pytest tests/unit/test_user_service.py

# Single test function
pytest tests/unit/test_user_service.py::test_create_user

# Tests matching a pattern
pytest -k "payment"

# Tests with a marker
pytest -m "slow"
```

### Run by Test Type

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

## Unit Tests

Unit tests are fast, isolated tests of individual functions or classes.

### Writing Unit Tests

```python
import pytest
from app.services.user_service import UserService
from app.models import User

class TestUserService:
    """Unit tests for UserService."""
    
    @pytest.fixture
    def user_service(self):
        """Create a UserService instance for testing."""
        return UserService()
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for tests."""
        return {
            'email': 'test@example.com',
            'password': 'SecureP@ss123',
            'username': 'testuser'
        }
    
    def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        # Arrange - setup done in fixtures
        
        # Act
        user = user_service.create_user(**sample_user_data)
        
        # Assert
        assert user.email == sample_user_data['email']
        assert user.username == sample_user_data['username']
        assert user.password != sample_user_data['password']  # Should be hashed
    
    def test_create_user_duplicate_email(self, user_service, sample_user_data):
        """Test that duplicate email raises error."""
        # Arrange
        user_service.create_user(**sample_user_data)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(**sample_user_data)
    
    def test_create_user_invalid_email(self, user_service, sample_user_data):
        """Test that invalid email format raises error."""
        # Arrange
        sample_user_data['email'] = 'not-an-email'
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            user_service.create_user(**sample_user_data)
    
    @pytest.mark.parametrize("password,should_pass", [
        ("ShortP@1", False),          # Too short
        ("nouppercase123!", False),   # No uppercase
        ("NOLOWERCASE123!", False),   # No lowercase
        ("NoNumbers!", False),        # No numbers
        ("NoSpecial123", False),      # No special chars
        ("ValidP@ssw0rd!", True),     # Valid
    ])
    def test_password_validation(self, user_service, password, should_pass):
        """Test password validation with various inputs."""
        result = user_service.validate_password(password)
        assert result == should_pass
```

### Unit Test Best Practices

1. **Test one thing per test** - Each test should verify one behavior
2. **Use AAA pattern** - Arrange, Act, Assert
3. **Use fixtures** for common setup
4. **Use parametrize** for testing multiple inputs
5. **Mock external dependencies** - Don't hit real APIs or databases
6. **Test edge cases** - Empty strings, None, negative numbers, etc.

### Mocking Dependencies

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

class TestPaymentService:
    """Tests for payment processing."""
    
    @patch('app.services.payment_service.stripe.Charge.create')
    def test_process_payment_success(self, mock_stripe):
        """Test successful payment processing."""
        # Arrange
        mock_stripe.return_value = {
            'id': 'ch_123456',
            'status': 'succeeded'
        }
        service = PaymentService()
        
        # Act
        result = service.process_payment(
            amount=100.00,
            token='tok_visa'
        )
        
        # Assert
        assert result['status'] == 'succeeded'
        mock_stripe.assert_called_once()
    
    def test_send_email_with_mock(self):
        """Test email sending with mocked SMTP."""
        # Arrange
        mock_smtp = Mock()
        service = EmailService(smtp_client=mock_smtp)
        
        # Act
        service.send_email(
            to='test@example.com',
            subject='Test',
            body='Test message'
        )
        
        # Assert
        mock_smtp.send.assert_called_once()
```

## Integration Tests

Integration tests verify that multiple components work together.

### Database Tests

```python
import pytest
from app.database import init_db, close_db
from app.services.user_service import UserService

@pytest.fixture(scope='function')
def db():
    """Create test database."""
    db_connection = init_db('test_database')
    yield db_connection
    close_db(db_connection)

@pytest.fixture(scope='function')
def user_service(db):
    """Create UserService with test database."""
    return UserService(db)

class TestUserServiceIntegration:
    """Integration tests with real database."""
    
    def test_create_and_retrieve_user(self, user_service):
        """Test creating user and retrieving from database."""
        # Create user
        user = user_service.create_user(
            email='test@example.com',
            password='SecureP@ss123'
        )
        
        # Retrieve user
        retrieved = user_service.get_user_by_email('test@example.com')
        
        # Verify
        assert retrieved.id == user.id
        assert retrieved.email == user.email
    
    def test_transaction_rollback_on_error(self, user_service):
        """Test that database transaction rolls back on error."""
        with pytest.raises(ValueError):
            with user_service.transaction():
                user_service.create_user(
                    email='test@example.com',
                    password='SecureP@ss123'
                )
                # This should cause rollback
                raise ValueError("Intentional error")
        
        # Verify user was not created
        with pytest.raises(UserNotFoundError):
            user_service.get_user_by_email('test@example.com')
```

### API Tests

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

class TestUserAPI:
    """Integration tests for user API endpoints."""
    
    def test_create_user_endpoint(self, client):
        """Test POST /users endpoint."""
        response = client.post(
            '/users',
            json={
                'email': 'test@example.com',
                'password': 'SecureP@ss123',
                'username': 'testuser'
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['email'] == 'test@example.com'
        assert 'password' not in data  # Should not return password
    
    def test_get_user_endpoint(self, client):
        """Test GET /users/{id} endpoint."""
        # Create user first
        create_response = client.post(
            '/users',
            json={
                'email': 'test@example.com',
                'password': 'SecureP@ss123'
            }
        )
        user_id = create_response.json()['id']
        
        # Get user
        response = client.get(f'/users/{user_id}')
        
        assert response.status_code == 200
        assert response.json()['id'] == user_id
    
    def test_authentication_required(self, client):
        """Test that protected endpoint requires authentication."""
        response = client.get('/users/me')
        assert response.status_code == 401
```

## End-to-End Tests

E2E tests simulate real user workflows.

### Selenium/Playwright Tests

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope='session')
def browser():
    """Create browser instance."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

class TestUserWorkflow:
    """End-to-end user workflow tests."""
    
    def test_complete_registration_flow(self, page: Page):
        """Test complete user registration workflow."""
        # Navigate to signup page
        page.goto('http://localhost:8000/signup')
        
        # Fill form
        page.fill('input[name="email"]', 'test@example.com')
        page.fill('input[name="password"]', 'SecureP@ss123')
        page.fill('input[name="confirm_password"]', 'SecureP@ss123')
        
        # Submit
        page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard
        expect(page).to_have_url('http://localhost:8000/dashboard')
        
        # Verify welcome message
        expect(page.locator('h1')).to_have_text('Welcome!')
    
    def test_login_logout_flow(self, page: Page):
        """Test login and logout workflow."""
        # Login
        page.goto('http://localhost:8000/login')
        page.fill('input[name="email"]', 'test@example.com')
        page.fill('input[name="password"]', 'SecureP@ss123')
        page.click('button[type="submit"]')
        
        # Verify logged in
        expect(page.locator('.user-menu')).to_be_visible()
        
        # Logout
        page.click('.logout-button')
        
        # Verify logged out
        expect(page).to_have_url('http://localhost:8000/login')
```

## Test Fixtures

### Common Fixtures

Create reusable fixtures in `conftest.py`:

```python
# tests/conftest.py
import pytest
from app.database import init_db
from app.models import User

@pytest.fixture(scope='session')
def db_session():
    """Database session for all tests."""
    db = init_db('test_database')
    yield db
    db.close()

@pytest.fixture(scope='function')
def clean_db(db_session):
    """Clean database before each test."""
    # Truncate all tables
    for table in ['users', 'payments', 'orders']:
        db_session.execute(f"TRUNCATE TABLE {table} CASCADE")
    db_session.commit()
    yield db_session

@pytest.fixture
def sample_user(clean_db):
    """Create a sample user for tests."""
    user = User(
        email='test@example.com',
        username='testuser',
        password_hash='hashed_password'
    )
    clean_db.add(user)
    clean_db.commit()
    return user
```

## Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.slow
def test_complex_computation():
    """This test takes a while."""
    pass

@pytest.mark.integration
def test_database_operations():
    """Integration test with database."""
    pass

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Test for upcoming feature."""
    pass

@pytest.mark.skipif(condition, reason="Skipping in CI")
def test_local_only():
    """Only run locally."""
    pass
```

Configure markers in `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    unit: marks tests as unit tests
```

## Code Coverage

### Measuring Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open report
open htmlcov/index.html
```

### Coverage Requirements

- **Minimum**: 80% overall coverage
- **Critical code**: 95%+ (payment processing, authentication, etc.)
- **New code**: Must maintain or improve coverage

### Coverage Configuration

In `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/config/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def view_dashboard(self):
        """Most common user action."""
        self.client.get("/dashboard")
    
    @task(1)
    def create_item(self):
        """Less frequent action."""
        self.client.post("/items", json={
            "name": "Test Item",
            "price": 99.99
        })
```

Run: `locust -f tests/performance/locustfile.py`

## Testing Best Practices

### DO ✓

1. **Write tests first** (TDD) or alongside code
2. **Keep tests fast** - Unit tests should run in milliseconds
3. **Use descriptive names** - Test names are documentation
4. **Test edge cases** - Empty inputs, nulls, boundaries
5. **One assertion per test** (generally) - Makes failures clear
6. **Use fixtures** to reduce duplication
7. **Mock external services** - Don't hit real APIs in tests
8. **Run tests before committing** - Catch issues early

### DON'T ✗

1. **Don't test implementation details** - Test behavior, not internals
2. **Don't write flaky tests** - Tests should be deterministic
3. **Don't skip tests** without good reason
4. **Don't test third-party code** - Trust the libraries you use
5. **Don't make tests dependent** on each other
6. **Don't use sleep()** - Use proper waits/polling
7. **Don't hardcode values** - Use fixtures and factories

## Continuous Integration

Tests run automatically on every PR:

```yaml
# .github/workflows/test.yml
name: Tests
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest --cov=app --cov-fail-under=80
```

## Debugging Failed Tests

### Using pytest debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### Verbose output

```bash
# See print statements
pytest -s

# Verbose output
pytest -v

# Even more verbose
pytest -vv
```

### Capture logs

```python
def test_with_logging(caplog):
    """Test that captures log output."""
    with caplog.at_level(logging.INFO):
        my_function()
    
    assert "Expected log message" in caplog.text
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_user_service.py
│   ├── test_payment_service.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_auth_flow.py
├── e2e/
│   ├── test_user_workflows.py
│   └── test_checkout_flow.py
└── performance/
    └── locustfile.py
```

## Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/unit/test_user_service.py::test_create_user

# Run tests matching pattern
pytest -k "payment"

# Run only fast tests
pytest -m "not slow"

# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Getting Help

- **Test failures**: Check #engineering-help
- **pytest questions**: https://docs.pytest.org/
- **Coverage issues**: Ask in daily standup
- **Writing better tests**: Pair with senior engineer
