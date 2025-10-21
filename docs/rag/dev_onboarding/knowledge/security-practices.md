# Security Best Practices

## Overview

Security is everyone's responsibility. This guide covers essential security practices for our codebase, infrastructure, and day-to-day development work.

**Golden Rules**:
1. Never commit secrets
2. Validate all input
3. Assume breach
4. Least privilege always
5. Security by default

## Secrets Management

### DO NOT Commit Secrets

**Never commit**:
- API keys
- Passwords
- Private keys
- Database credentials
- OAuth tokens
- Encryption keys

**Before committing**:
```bash
# Scan for secrets
git-secrets --scan

# Or use gitleaks
gitleaks detect --verbose
```

### Use Environment Variables

**Good**:
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("STRIPE_API_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
```

**Bad**:
```python
# ❌ NEVER DO THIS
DATABASE_URL = "postgresql://user:password@host/db"
API_KEY = "sk_live_1234567890"
```

### Secrets Storage

**Development**:
- Use `.env` file (add to `.gitignore`)
- Use `python-dotenv` to load
- Share secrets via 1Password team vault

**Production**:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets (encrypted at rest)

**Loading secrets**:
```python
from dotenv import load_dotenv
import os

# Load from .env file in development
load_dotenv()

# Access secrets
db_password = os.getenv("DB_PASSWORD")
```

### Rotating Secrets

**When to rotate**:
- Every 90 days (scheduled)
- After employee departure
- After suspected compromise
- After public exposure

**How to rotate**:
1. Generate new secret
2. Update in secrets manager
3. Deploy with new secret
4. Verify functionality
5. Revoke old secret
6. Document in change log

## Input Validation

### Validate All Input

**Never trust user input**:
```python
from pydantic import BaseModel, EmailStr, constr

class UserInput(BaseModel):
    email: EmailStr  # Validates email format
    username: constr(min_length=3, max_length=20)  # Length validation
    age: int  # Type validation
    
    class Config:
        # Prevent extra fields
        extra = "forbid"

# Usage
try:
    user = UserInput(**request_data)
except ValidationError as e:
    return {"error": "Invalid input", "details": e.errors()}
```

### SQL Injection Prevention

**Use parameterized queries**:
```python
# ❌ VULNERABLE to SQL injection
username = request.args.get('username')
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)

# ✅ SAFE: Parameterized query
username = request.args.get('username')
query = "SELECT * FROM users WHERE username = %s"
db.execute(query, [username])

# ✅ BEST: Use ORM
user = User.objects.filter(username=username).first()
```

### XSS Prevention

**Escape output**:
```python
from markupsafe import escape

# ❌ VULNERABLE to XSS
@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"<h1>Hello {name}</h1>"

# ✅ SAFE: Escape user input
@app.route('/hello')
def hello():
    name = request.args.get('name', '')
    return f"<h1>Hello {escape(name)}</h1>"

# ✅ BEST: Use template engine (auto-escapes)
@app.route('/hello')
def hello():
    name = request.args.get('name', '')
    return render_template('hello.html', name=name)
```

### Path Traversal Prevention

**Validate file paths**:
```python
import os
from pathlib import Path

# ❌ VULNERABLE to path traversal
filename = request.args.get('file')
with open(f'/uploads/{filename}', 'r') as f:
    return f.read()

# ✅ SAFE: Validate path
def safe_join(base_dir, filename):
    """Safely join paths, preventing traversal."""
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    if not target.is_relative_to(base):
        raise ValueError("Invalid file path")
    
    return target

filename = request.args.get('file')
filepath = safe_join('/uploads', filename)
with open(filepath, 'r') as f:
    return f.read()
```

## Authentication & Authorization

### Password Security

**Hashing passwords**:
```python
from passlib.hash import bcrypt

# ❌ NEVER store plain text passwords
user.password = request.form['password']

# ❌ NEVER use weak hashing (MD5, SHA1)
user.password = hashlib.md5(password.encode()).hexdigest()

# ✅ Use strong hashing (bcrypt, argon2)
user.password = bcrypt.hash(request.form['password'])

# Verify password
if bcrypt.verify(submitted_password, user.password):
    login_user(user)
```

**Password requirements**:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not in common password list
- Not similar to username

```python
import re
from common_passwords import is_common

def validate_password(password, username):
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"
    
    if is_common(password):
        return False, "Password is too common"
    
    if username.lower() in password.lower():
        return False, "Password cannot contain username"
    
    return True, "Password is valid"
```

### Session Management

**Secure session cookies**:
```python
from flask import Flask

app = Flask(__name__)

# Session configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),  # Strong random key
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)  # Session timeout
)
```

**Session timeout**:
```python
from datetime import datetime, timedelta

def check_session_timeout(session):
    last_activity = session.get('last_activity')
    if last_activity:
        if datetime.now() - last_activity > timedelta(minutes=30):
            session.clear()
            return False
    
    session['last_activity'] = datetime.now()
    return True
```

### JWT Security

**Secure JWT usage**:
```python
import jwt
from datetime import datetime, timedelta

SECRET = os.getenv('JWT_SECRET')
ALGORITHM = 'HS256'

# ✅ Generate token with expiration
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

# ✅ Verify token
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
```

### Authorization

**Implement RBAC (Role-Based Access Control)**:
```python
from functools import wraps
from flask import abort

def require_permission(permission):
    """Decorator to check user permissions."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Usage
@app.route('/admin/users')
@require_permission('admin.users.view')
def list_users():
    return render_template('users.html')
```

## API Security

### Rate Limiting

**Prevent abuse**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

@app.route('/api/search')
@limiter.limit("10 per minute")
def search():
    return perform_search(request.args.get('q'))
```

### CORS Configuration

**Restrict origins**:
```python
from flask_cors import CORS

# ❌ BAD: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ GOOD: Whitelist specific origins
allowed_origins = [
    "https://app.company.com",
    "https://admin.company.com"
]

CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### API Authentication

**Use API keys securely**:
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return {"error": "API key required"}, 401
        
        if not verify_api_key(api_key):
            return {"error": "Invalid API key"}, 403
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/data')
@require_api_key
def get_data():
    return {"data": "sensitive information"}
```

## Data Protection

### Encryption at Rest

**Encrypt sensitive data**:
```python
from cryptography.fernet import Fernet

# Generate key (do this once, store securely)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

# Decrypt
def decrypt_data(encrypted_data):
    return cipher.decrypt(encrypted_data.encode()).decode()

# Usage
user.ssn = encrypt_data(ssn)
user.save()

# Later
ssn = decrypt_data(user.ssn)
```

### Encryption in Transit

**Always use HTTPS**:
```python
# Force HTTPS redirect
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000
)
```

### PII Handling

**Minimize PII collection**:
- Only collect what you need
- Delete when no longer needed
- Anonymize in logs
- Encrypt in database
- Restrict access

**Logging without PII**:
```python
import logging

# ❌ BAD: Logging PII
logging.info(f"User {user.email} logged in")

# ✅ GOOD: Log user ID instead
logging.info(f"User {user.id} logged in")

# ✅ GOOD: Mask sensitive data
def mask_email(email):
    username, domain = email.split('@')
    return f"{username[:2]}***@{domain}"

logging.info(f"User {mask_email(user.email)} logged in")
```

## Dependency Management

### Keep Dependencies Updated

**Check for vulnerabilities**:
```bash
# Audit dependencies
pip-audit

# Check for outdated packages
pip list --outdated

# Update requirements
pip-compile --upgrade requirements.in
```

**Use Dependabot**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### Pin Dependencies

**In requirements.txt**:
```txt
# ❌ BAD: Unpinned versions
flask
requests

# ✅ GOOD: Pinned versions
flask==3.0.0
requests==2.31.0

# ✅ BETTER: Hash verification
flask==3.0.0 \
    --hash=sha256:abc123...
```

## Security Headers

**Add security headers**:
```python
@app.after_request
def add_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = \
        "default-src 'self'; script-src 'self' 'unsafe-inline'"
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

## Common Vulnerabilities

### OWASP Top 10

1. **Broken Access Control**: Implement proper authorization
2. **Cryptographic Failures**: Use strong encryption, secure storage
3. **Injection**: Validate input, use parameterized queries
4. **Insecure Design**: Security by design, threat modeling
5. **Security Misconfiguration**: Secure defaults, hardening
6. **Vulnerable Components**: Keep dependencies updated
7. **Authentication Failures**: Strong passwords, MFA, rate limiting
8. **Data Integrity Failures**: Verify data integrity, secure CI/CD
9. **Logging Failures**: Comprehensive logging, monitoring
10. **SSRF**: Validate URLs, whitelist allowed hosts

### SSRF Prevention

```python
import ipaddress
from urllib.parse import urlparse

ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com']

def is_safe_url(url):
    """Prevent SSRF attacks."""
    try:
        parsed = urlparse(url)
        
        # Only allow HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check against whitelist
        if parsed.hostname not in ALLOWED_HOSTS:
            return False
        
        # Prevent internal IPs
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            return False
        
        return True
    except:
        return False

# Usage
url = request.args.get('url')
if not is_safe_url(url):
    return {"error": "Invalid URL"}, 400

response = requests.get(url)
```

## Incident Response

### If You Find a Vulnerability

1. **Don't panic**
2. **Document** what you found
3. **Report immediately** to security team (#security)
4. **Don't exploit** the vulnerability
5. **Don't share publicly** until fixed

### If You Commit a Secret

```bash
# Immediately rotate the secret
# Then remove from git history

# Remove from last commit
git reset HEAD~1
git add -A
git commit -m "Your message"
git push --force

# Remove from history (if pushed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (after rotating secret!)
git push --force --all
```

**Then**:
1. Rotate the compromised secret
2. Scan for unauthorized usage
3. Report to security team
4. Document in incident log

## Code Review Security Checklist

- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Rate limiting applied
- [ ] Error messages don't leak info
- [ ] Logging doesn't expose PII
- [ ] Dependencies are up to date

## Security Training

**Required Reading**:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- Our internal security guidelines

**Regular Activities**:
- Quarterly security training
- Monthly security newsletter
- Annual security audit
- Bug bounty program

## Tools We Use

- **Secrets scanning**: git-secrets, gitleaks
- **Dependency scanning**: pip-audit, Dependabot
- **SAST**: Bandit, Semgrep
- **DAST**: OWASP ZAP
- **Vulnerability management**: Snyk
- **WAF**: AWS WAF, Cloudflare

## Getting Help

- **Security questions**: #security channel
- **Report vulnerability**: security@company.com
- **Security review request**: Tag @security-team in PR
- **Incident**: Page security on-call via PagerDuty

## Resources

- [Security Guidelines (Internal)](https://wiki.company.com/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Guidelines](https://www.nist.gov/cybersecurity)
