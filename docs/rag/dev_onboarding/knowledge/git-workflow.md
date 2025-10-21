# Git Workflow Guide

## Branch Strategy

We follow a **Git Flow** inspired workflow with the following main branches:

- `main` - Production code (always deployable)
- `staging` - Pre-production testing
- `develop` - Integration branch for features

## Branch Naming Conventions

```
feature/    - New features (feature/user-authentication)
bugfix/     - Bug fixes (bugfix/login-error)
hotfix/     - Production fixes (hotfix/security-patch)
refactor/   - Code refactoring (refactor/payment-service)
docs/       - Documentation (docs/api-guide)
test/       - Test improvements (test/payment-coverage)
```

Examples:
- `feature/add-payment-processing`
- `bugfix/fix-email-validation`
- `hotfix/patch-security-vulnerability`

## Daily Workflow

### 1. Start Your Day

```bash
# Switch to develop branch
git checkout develop

# Pull latest changes
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 2. Making Changes

```bash
# Check what changed
git status

# See detailed changes
git diff

# Stage specific files
git add path/to/file.py

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "Add user authentication endpoint"
```

### 3. Commit Often

Make small, focused commits:

```bash
# Good commits ✓
git commit -m "Add User model"
git commit -m "Add user registration endpoint"
git commit -m "Add email validation"

# Bad commit ✗
git commit -m "Add entire user system with auth and email and validation"
```

### 4. Push Your Branch

```bash
# First time pushing a new branch
git push -u origin feature/your-feature-name

# Subsequent pushes
git push
```

### 5. Stay Up to Date

Regularly sync with develop:

```bash
# While on your feature branch
git fetch origin
git rebase origin/develop

# If there are conflicts, resolve them and continue
git rebase --continue
```

**Prefer rebase over merge** to keep history clean.

## Commit Message Guidelines

### Format

```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Examples

```bash
# Simple commit
git commit -m "feat: add password reset endpoint"

# With body
git commit -m "fix: resolve race condition in payment processing

The payment service was not properly locking transactions,
causing duplicate charges. Added row-level locking to prevent this.

Fixes #1234"

# Breaking change
git commit -m "feat!: change API response format

BREAKING CHANGE: API now returns camelCase instead of snake_case.
Clients will need to update their parsers."
```

## Pull Request Process

### 1. Create Pull Request

Go to GitHub and create a PR from your feature branch to `develop`.

**PR Title**: Same format as commit messages
```
feat: add user authentication system
```

**PR Description Template**:
```markdown
## What does this PR do?
Brief description of changes

## Why are we making this change?
Context and motivation

## How has this been tested?
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manually tested in dev environment

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No sensitive data committed

## Related Issues
Closes #123
```

### 2. Request Reviews

- Assign at least **1 reviewer** (2 for complex changes)
- Add relevant labels (`backend`, `frontend`, `urgent`, etc.)
- Link related JIRA ticket

### 3. Address Review Comments

```bash
# Make requested changes
git add .
git commit -m "Address review comments"
git push
```

**Tips**:
- Respond to all comments (even if just "done")
- Don't take criticism personally - we're reviewing code, not you
- If you disagree, discuss respectfully
- Mark conversations as "resolved" after addressing

### 4. Merge Requirements

PRs can only be merged when:
- [ ] All CI/CD checks pass (tests, linting, security)
- [ ] At least 1 approval from a reviewer
- [ ] No unresolved conversations
- [ ] Branch is up to date with target branch
- [ ] No merge conflicts

### 5. Merge Your PR

Click "Squash and merge" (preferred) or "Merge" depending on project settings.

**After merging**:
```bash
# Switch back to develop
git checkout develop

# Pull the merged changes
git pull origin develop

# Delete your local branch
git branch -d feature/your-feature-name

# Delete remote branch (if not auto-deleted)
git push origin --delete feature/your-feature-name
```

## Handling Merge Conflicts

### When You See Conflicts

```bash
# Update your branch with latest develop
git fetch origin
git rebase origin/develop

# Git will pause on conflicts
# Edit conflicted files (look for <<<<<<, ======, >>>>>> markers)

# After resolving conflicts
git add .
git rebase --continue

# Force push (rebase rewrites history)
git push --force-with-lease
```

### Conflict Markers Explained

```python
<<<<<<< HEAD (your changes)
def calculate_total(items):
    return sum(item.price for item in items)
=======
def calculate_total(items, tax_rate):
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
>>>>>>> origin/develop (incoming changes)
```

**Resolution**: Choose one version or combine them:
```python
def calculate_total(items, tax_rate=0.0):
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate) if tax_rate else subtotal
```

## Advanced Git Commands

### Undo Last Commit (Keep Changes)

```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)

```bash
git reset --hard HEAD~1
```

### Stash Changes Temporarily

```bash
# Save current changes
git stash

# Apply stashed changes
git stash pop

# List stashes
git stash list
```

### Cherry-Pick a Commit

```bash
# Apply specific commit from another branch
git cherry-pick <commit-hash>
```

### Interactive Rebase (Clean Up Commits)

```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# In the editor:
# pick = keep commit
# squash = combine with previous
# reword = change commit message
# drop = remove commit
```

### View Commit History

```bash
# Detailed log
git log

# One line per commit
git log --oneline

# With graph
git log --graph --oneline --all

# Changes in a file
git log -p path/to/file.py
```

## Git Best Practices

### DO ✓

1. **Commit early and often** - Small commits are easier to review
2. **Write clear commit messages** - Your future self will thank you
3. **Keep branches short-lived** - Merge within 1-3 days
4. **Test before committing** - Run tests locally first
5. **Review your own changes** before creating PR
6. **Pull before you push** - Stay in sync with team

### DON'T ✗

1. **Don't commit to main directly** - Always use PRs
2. **Don't commit large binary files** - Use Git LFS if needed
3. **Don't commit secrets** - Use `.gitignore` and environment variables
4. **Don't force push to shared branches** - Only force push to your feature branch
5. **Don't work on multiple features in one branch** - One branch per feature
6. **Don't ignore merge conflicts** - Resolve them properly

## .gitignore Essentials

Your repository already has `.gitignore`, but be aware of:

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.egg-info/

# Environment variables
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Build
dist/
build/
```

## Troubleshooting

### "Your branch has diverged"

```bash
git pull --rebase origin develop
```

### "Detached HEAD state"

```bash
git checkout develop
```

### "Changes not staged for commit"

```bash
# Stage all changes
git add .

# Or stage specific files
git add path/to/file.py
```

### Accidentally committed to wrong branch

```bash
# On wrong branch, save the commit hash
git log  # Copy the commit hash

# Switch to correct branch
git checkout correct-branch

# Apply the commit
git cherry-pick <commit-hash>

# Go back to wrong branch and remove commit
git checkout wrong-branch
git reset --hard HEAD~1
```

## Git Workflow Cheat Sheet

```bash
# Daily start
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# While working
git add .
git commit -m "feat: add feature"
git push -u origin feature/my-feature

# Stay updated
git fetch origin
git rebase origin/develop
git push --force-with-lease

# After PR merged
git checkout develop
git pull origin develop
git branch -d feature/my-feature
```

## Getting Help

- **Git commands**: `git help <command>` or https://git-scm.com/docs
- **Workflow questions**: Ask in #engineering
- **Stuck on conflicts**: Ask team lead for pair session
- **Best resource**: https://learngitbranching.js.org/ (interactive tutorial)
