# Code Review Checklist

## Overview

Code reviews are critical for maintaining code quality, sharing knowledge, and catching bugs early. Every pull request requires at least **one approval** from another team member before merging.

**Review Timeline**:
- Small PRs (<100 lines): 24 hours
- Medium PRs (100-500 lines): 48 hours
- Large PRs (>500 lines): Consider breaking into smaller PRs

## Before Requesting Review

### Author Checklist

- [ ] All tests pass locally
- [ ] Code follows our coding standards
- [ ] Added/updated tests for new functionality
- [ ] Updated documentation if needed
- [ ] Ran linter and fixed all issues
- [ ] No debug code or commented-out code
- [ ] Meaningful commit messages following conventions
- [ ] PR description explains the "why" not just the "what"
- [ ] Linked related issues/tickets
- [ ] Self-reviewed the diff before requesting review

### PR Description Template

```markdown
## Description
Brief summary of changes

## Motivation
Why is this change needed?

## Changes
- List of key changes

## Testing
How was this tested?

## Screenshots (if UI changes)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Breaking changes noted
```

## Code Review Checklist

### 1. Functionality

**Does the code work correctly?**

- [ ] Code accomplishes the stated purpose
- [ ] Edge cases are handled
- [ ] Error cases are handled gracefully
- [ ] No obvious bugs or logic errors
- [ ] Changes don't break existing functionality

**Example Issues**:
```python
# ❌ Bad: No error handling
def process_order(order_id):
    order = Order.objects.get(id=order_id)
    return order.total

# ✅ Good: Handles missing order
def process_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        return order.total
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return None
```

### 2. Code Quality

**Is the code well-written?**

- [ ] Code is readable and self-documenting
- [ ] Functions/methods are small and focused
- [ ] Variable names are descriptive
- [ ] No code duplication (DRY principle)
- [ ] Appropriate use of abstractions
- [ ] Complex logic is commented

**Example Issues**:
```python
# ❌ Bad: Unclear variable names, too complex
def p(d):
    t = 0
    for i in d:
        if i['s'] == 'c':
            t += i['a']
    return t

# ✅ Good: Clear names, well-structured
def calculate_completed_order_total(orders):
    """Calculate total amount from completed orders."""
    total = 0
    for order in orders:
        if order['status'] == 'completed':
            total += order['amount']
    return total
```

### 3. Testing

**Are tests adequate?**

- [ ] New code has test coverage
- [ ] Tests are meaningful, not just for coverage
- [ ] Tests cover edge cases and error conditions
- [ ] Tests are maintainable and readable
- [ ] No flaky tests
- [ ] Integration tests for complex features

**Example Issues**:
```python
# ❌ Bad: Only tests happy path
def test_process_order():
    order = Order(id=1, total=100)
    result = process_order(1)
    assert result == 100

# ✅ Good: Tests edge cases too
def test_process_order_success():
    order = Order(id=1, total=100)
    result = process_order(1)
    assert result == 100

def test_process_order_not_found():
    result = process_order(999)
    assert result is None

def test_process_order_zero_total():
    order = Order(id=2, total=0)
    result = process_order(2)
    assert result == 0
```

### 4. Security

**Are there security concerns?**

- [ ] No hardcoded secrets or credentials
- [ ] User input is validated and sanitized
- [ ] SQL injection is prevented (use ORMs properly)
- [ ] XSS vulnerabilities are prevented
- [ ] Authentication/authorization is correct
- [ ] Sensitive data is not logged
- [ ] Dependencies are up to date (no known vulnerabilities)

**Example Issues**:
```python
# ❌ Bad: SQL injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ Good: Parameterized query
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    return db.execute(query, [username])

# ❌ Bad: Hardcoded secret
API_KEY = "sk_live_1234567890abcdef"

# ✅ Good: Environment variable
API_KEY = os.getenv("API_KEY")
```

### 5. Performance

**Will this code perform well?**

- [ ] No obvious performance issues
- [ ] Database queries are efficient (avoid N+1)
- [ ] Appropriate use of caching
- [ ] No unnecessary loops or computations
- [ ] Large data sets are handled properly
- [ ] Async/await used appropriately

**Example Issues**:
```python
# ❌ Bad: N+1 query problem
def get_order_summaries():
    orders = Order.objects.all()
    return [
        {
            'id': order.id,
            'customer': order.customer.name,  # N queries!
            'total': order.total
        }
        for order in orders
    ]

# ✅ Good: Use select_related
def get_order_summaries():
    orders = Order.objects.select_related('customer').all()
    return [
        {
            'id': order.id,
            'customer': order.customer.name,  # Already loaded
            'total': order.total
        }
        for order in orders
    ]
```

### 6. Architecture

**Does the code fit the system design?**

- [ ] Changes follow existing patterns
- [ ] Appropriate use of design patterns
- [ ] Separation of concerns
- [ ] Dependencies are reasonable
- [ ] No circular dependencies
- [ ] API contracts are maintained

**Example Issues**:
```python
# ❌ Bad: Business logic in view
@app.route('/orders/<id>/complete')
def complete_order(id):
    order = Order.objects.get(id=id)
    order.status = 'completed'
    order.save()
    send_email(order.customer.email, "Order completed")
    return jsonify({'success': True})

# ✅ Good: Business logic in service layer
class OrderService:
    def complete_order(self, order_id):
        order = self.order_repo.get(order_id)
        order.complete()
        self.notification_service.send_completion_email(order)
        return order

@app.route('/orders/<id>/complete')
def complete_order(id):
    order = order_service.complete_order(id)
    return jsonify(order.to_dict())
```

### 7. Documentation

**Is the code well-documented?**

- [ ] Public APIs have docstrings
- [ ] Complex logic is explained
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Migration guide for breaking changes

**Example Issues**:
```python
# ❌ Bad: No documentation
def calculate_discount(price, user_level):
    if user_level == 3:
        return price * 0.8
    elif user_level == 2:
        return price * 0.9
    return price

# ✅ Good: Clear documentation
def calculate_discount(price: float, user_level: int) -> float:
    """
    Calculate discounted price based on user level.
    
    Args:
        price: Original price in USD
        user_level: User tier (1=basic, 2=premium, 3=enterprise)
    
    Returns:
        Discounted price. Basic users get no discount,
        premium users get 10% off, enterprise users get 20% off.
    
    Example:
        >>> calculate_discount(100, 3)
        80.0
    """
    discount_rates = {3: 0.8, 2: 0.9}
    return price * discount_rates.get(user_level, 1.0)
```

### 8. Error Handling

**Are errors handled properly?**

- [ ] Exceptions are caught appropriately
- [ ] Error messages are helpful
- [ ] Errors are logged with context
- [ ] User-facing errors are user-friendly
- [ ] Resources are cleaned up (use context managers)

**Example Issues**:
```python
# ❌ Bad: Swallows all errors
try:
    process_payment(order)
except:
    pass

# ✅ Good: Specific exception handling with logging
try:
    process_payment(order)
except PaymentGatewayError as e:
    logger.error(f"Payment failed for order {order.id}: {e}")
    raise PaymentProcessingError(f"Unable to process payment: {e}")
except Exception as e:
    logger.exception(f"Unexpected error processing order {order.id}")
    raise
```

## Common Issues to Watch For

### Python-Specific

- **Mutable default arguments**: Use `None` and initialize in function
- **Global state**: Avoid global variables
- **Import order**: Follow PEP 8 (stdlib, third-party, local)
- **Type hints**: Use for public APIs
- **List comprehensions**: Don't overuse, keep readable
- **With statements**: Use for file/resource handling

### Database

- **N+1 queries**: Use `select_related`/`prefetch_related`
- **Missing indexes**: Add indexes for frequently queried fields
- **Transactions**: Use for multi-step operations
- **Raw SQL**: Avoid unless necessary, use ORM
- **Migrations**: Review carefully, test on staging

### API Changes

- **Breaking changes**: Document and version properly
- **Backwards compatibility**: Maintain when possible
- **Response format**: Follow established patterns
- **Status codes**: Use appropriate HTTP codes
- **Error messages**: Be consistent and helpful

## How to Give Good Feedback

### DO ✓

1. **Be specific**: Point to exact lines, explain why
2. **Be constructive**: Suggest alternatives
3. **Ask questions**: "Have you considered...?"
4. **Praise good code**: Positive feedback matters
5. **Focus on code, not person**: "This function" not "You"
6. **Provide context**: Link to docs, examples
7. **Distinguish must-fix vs. nice-to-have**

**Good Example**:
```
Line 45: Consider using a context manager here for automatic resource cleanup:

with open(filename, 'r') as f:
    data = f.read()

This ensures the file is always closed, even if an exception occurs.
```

### DON'T ✗

1. **Don't be vague**: "This looks wrong" - explain!
2. **Don't be dismissive**: "This is terrible"
3. **Don't nitpick formatting**: Let linters handle it
4. **Don't block on opinions**: Distinguish issues from preferences
5. **Don't rewrite everything**: Suggest targeted improvements

**Bad Example**:
```
This code is messy. Rewrite it.
```

## Review Priorities

### P0: Must Fix Before Merge

- Security vulnerabilities
- Bugs that break functionality
- Broken tests
- Code that doesn't follow standards
- Missing critical tests

### P1: Should Fix

- Code quality issues
- Suboptimal performance
- Missing tests for edge cases
- Unclear variable names
- Missing documentation

### P2: Nice to Have

- Minor style preferences
- Additional optimizations
- Enhanced documentation
- Refactoring opportunities

## Approval Criteria

**Approve** when:
- Code works correctly
- Tests are adequate
- No security issues
- Follows standards
- Documentation is sufficient
- Minor issues can be addressed in follow-up

**Request Changes** when:
- Bugs or security issues
- Missing critical tests
- Code doesn't follow standards
- Performance problems
- Architecture concerns

**Comment (no approval)** when:
- You have suggestions but they're optional
- You're not the right reviewer
- You want to leave feedback but others should approve

## Time Management

### Quick Reviews (<5 min)

- Small bug fixes
- Documentation updates
- Test additions
- Dependency updates

### Standard Reviews (15-30 min)

- New features
- Refactoring
- API changes

### Deep Reviews (1+ hour)

- Architecture changes
- Security-sensitive code
- Complex algorithms
- Database migrations

**If a PR is too large to review**, ask the author to split it up!

## After Approval

- [ ] Squash commits if needed
- [ ] Update PR with any changes
- [ ] Ensure CI passes
- [ ] Merge using appropriate strategy
- [ ] Delete branch after merge
- [ ] Monitor deployment

## Resources

- [Our Coding Standards](./coding-standards.md)
- [Testing Guide](./testing-guide.md)
- [Security Best Practices](./security-practices.md)
- [Git Workflow](./git-workflow.md)
