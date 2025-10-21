# Development Environment Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11 or higher**
- **Git 2.30+**
- **Docker Desktop** (for local services)
- **VS Code** (recommended IDE) or your preferred editor

## Initial Setup Steps

### 1. Clone the Repository

```bash
git clone git@github.com:company/main-app.git
cd main-app
```

### 2. Set Up Python Environment

We use Python virtual environments to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 3. Install Pre-commit Hooks

Pre-commit hooks ensure code quality before committing:

```bash
pre-commit install
```

This will automatically run:
- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- Security checks (bandit)

### 4. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set the following variables:
- `DATABASE_URL` - Ask your team lead for the development database URL
- `API_KEY` - Get from https://internal-portal.company.com/api-keys
- `REDIS_URL` - Usually `redis://localhost:6379` for local development
- `LOG_LEVEL` - Set to `DEBUG` for development

**Never commit `.env` files to git!**

### 5. Start Local Services

We use Docker Compose to run local dependencies:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- LocalStack (AWS services emulation on port 4566)

Check services are running:
```bash
docker-compose ps
```

### 6. Run Database Migrations

Initialize your local database:

```bash
# Run migrations
python manage.py migrate

# Load sample data
python manage.py load_fixtures
```

### 7. Verify Setup

Run the test suite to verify everything is working:

```bash
make test
```

Start the development server:

```bash
python manage.py runserver
```

Visit http://localhost:8000 - you should see the application homepage.

## IDE Configuration

### VS Code (Recommended)

Install these extensions:
- Python (Microsoft)
- Pylance
- Black Formatter
- Ruff
- GitLens
- Docker

The repository includes `.vscode/settings.json` with recommended settings.

### PyCharm

1. Open the project
2. Configure Python interpreter: Settings → Project → Python Interpreter → Select venv/bin/python
3. Enable Django support: Settings → Languages & Frameworks → Django
4. Configure code style: Settings → Editor → Code Style → Python → Import Black settings

## Common Setup Issues

### Issue: "ModuleNotFoundError"
**Solution**: Ensure your virtual environment is activated and dependencies are installed.

### Issue: Database connection errors
**Solution**: 
- Check Docker containers are running: `docker-compose ps`
- Verify DATABASE_URL in `.env` is correct
- Restart containers: `docker-compose restart`

### Issue: Pre-commit hooks failing
**Solution**: 
- Run formatters manually: `make format`
- Check for syntax errors in your code
- Ensure all dev dependencies are installed

### Issue: Port already in use
**Solution**: 
- Find and kill the process: `lsof -ti:8000 | xargs kill -9`
- Or use a different port: `python manage.py runserver 8001`

## Next Steps

Once your environment is set up:
1. Read the [Git Workflow Guide](git-workflow.md)
2. Review [Coding Standards](coding-standards.md)
3. Check out the [Architecture Overview](architecture-overview.md)
4. Pick up a "good first issue" from JIRA

## Getting Help

- **Slack**: #engineering-help channel
- **Team Lead**: @engineering-lead
- **Documentation Issues**: Create a PR to improve this guide!
