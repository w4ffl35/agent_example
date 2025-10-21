# Use Case: Developer Onboarding Assistant

## Overview

This agent serves as an **AI-powered Developer Onboarding Assistant** that helps new engineers at a software company quickly get up to speed with internal tools, processes, and best practices. The agent has access to a knowledge base containing company documentation and can answer questions about development workflows, deployment procedures, coding standards, and team policies.

## Problem Statement

When new developers join a company, they face a steep learning curve:
- Where is documentation scattered across multiple wikis and repos
- They need to know coding standards, git workflows, and deployment processes
- They have questions about internal tools and services
- They need quick answers without interrupting busy team members
- Common questions get asked repeatedly (documentation for X, how to deploy to Y, etc.)

## Solution

An AI assistant that:
1. **Retrieves relevant documentation** from the knowledge base based on natural language queries
2. **Provides accurate, context-aware answers** by combining retrieved information with the LLM's reasoning
3. **Available 24/7** without requiring senior developer time
4. **Maintains conversation context** to handle follow-up questions
5. **Cites sources** so developers can dive deeper into documentation

## User Flow

### Example Interaction 1: Learning About Deployment

```
Developer: How do I deploy my changes to staging?

Agent: [Searches knowledge base for "deploy staging"]
Based on our deployment documentation, here's how to deploy to staging:

1. Ensure all tests pass: `npm run test`
2. Create a pull request to the `develop` branch
3. Once approved and merged, the CI/CD pipeline automatically deploys to staging
4. You can monitor the deployment at https://ci.company.com

The deployment typically takes 5-10 minutes. You'll receive a Slack notification when it completes.

Source: docs/deployment-guide.md
```

### Example Interaction 2: Understanding Code Standards

```
Developer: What are our Python code formatting standards?

Agent: [Searches knowledge base for "Python formatting standards"]
For Python code, we follow these standards:

- **Formatter**: Black with default settings (88 character line length)
- **Linter**: Ruff for fast linting and import sorting
- **Type Checking**: mypy in strict mode for all new code
- **Pre-commit hooks**: Run `pre-commit install` to automatically format on commit

All of these are configured in pyproject.toml. Run `make format` to format your code before committing.

Source: docs/coding-standards.md
```

### Example Interaction 3: Follow-up Context

```
Developer: What about line length for docstrings?

Agent: [Uses conversation context + searches for "docstring formatting"]
For docstrings specifically, we follow PEP 257 conventions with a 72 character line length limit (shorter than code). 

Docstrings should use triple double-quotes and include:
- One-line summary
- Blank line
- Detailed description
- Args, Returns, and Raises sections for functions

Black won't reformat docstrings automatically, so watch your line lengths manually.

Source: docs/coding-standards.md
```

## Agent Capabilities

### 1. **Knowledge Retrieval** (Current Implementation)
- Searches markdown documentation in `docs/rag/` directory
- Uses semantic search to find relevant context
- Returns top-k most relevant document chunks
- Automatically indexes new documents

### 2. **Contextual Understanding**
- Maintains conversation history for follow-up questions
- Trims message history to manage token limits
- Combines retrieved docs with LLM reasoning

### 3. **Streaming Responses**
- Provides real-time feedback as answers are generated
- Better UX than waiting for complete responses

## Success Metrics

1. **Reduction in repetitive questions** in team Slack channels
2. **Faster onboarding time** for new developers (measure time to first PR)
3. **Developer satisfaction** with quality and accuracy of responses
4. **Knowledge base coverage** - identify gaps when agent can't answer

## Knowledge Base Contents

The `docs/rag/` directory should contain markdown files covering:

### Core Documentation
- **setup-guide.md** - Development environment setup instructions
- **deployment-guide.md** - How to deploy to different environments
- **coding-standards.md** - Language-specific coding conventions
- **git-workflow.md** - Branching strategy and PR process
- **testing-guide.md** - How to write and run tests
- **architecture-overview.md** - High-level system architecture

### Tool-Specific Guides
- **ci-cd-pipeline.md** - Understanding the build pipeline
- **monitoring-logging.md** - How to check logs and metrics
- **database-access.md** - Connecting to databases
- **api-documentation.md** - Internal API endpoints

### Process Documentation
- **code-review-checklist.md** - What to look for in reviews
- **incident-response.md** - What to do when things break
- **security-practices.md** - Security guidelines and secrets management

## Future Enhancements

### Additional Tools (Beyond RAG)
1. **JIRA Ticket Lookup** - Query ticket status and details
2. **GitHub Integration** - Check PR status, recent commits
3. **Slack Integration** - Look up team member contact info
4. **Calendar Integration** - Check team meeting schedules
5. **Code Search** - Search actual codebase (beyond docs)

### Enhanced Features
1. **Interactive Tutorials** - Step-by-step walkthroughs
2. **Command Generation** - Generate commonly-used commands
3. **Troubleshooting Assistant** - Diagnose common error messages
4. **Onboarding Checklist** - Track completion of setup tasks

## Why This Use Case Works

1. **Real Business Value** - Solves actual pain point in engineering orgs
2. **Clear RAG Application** - Documentation retrieval is natural fit
3. **Extensible** - Easy to add more tools and knowledge
4. **Measurable Impact** - Can track usage and effectiveness
5. **Relatable** - Reviewers understand the problem (they've been new devs too)
6. **Not Overcomplicated** - Focused scope that's achievable in timeframe

## Evaluation Approach

### Test Cases (for LangSmith Evals)

1. **Direct Question**
   - Input: "How do I run tests?"
   - Expected: Should retrieve testing-guide.md and provide clear command

2. **Multi-step Process**
   - Input: "Walk me through deploying to production"
   - Expected: Should provide ordered steps from deployment guide

3. **Clarification/Follow-up**
   - Input 1: "What's our git workflow?"
   - Input 2: "What branch do I use for hotfixes?"
   - Expected: Second answer should use context from first

4. **Unknown Information**
   - Input: "What's the password for the database?"
   - Expected: Should gracefully say this info isn't in knowledge base (and shouldn't be!)

5. **Ambiguous Query**
   - Input: "How do I deploy?"
   - Expected: Should ask for clarification (staging vs production) or list both options

## Implementation Notes

- System prompt should emphasize being helpful but not making up information
- When docs don't have an answer, agent should acknowledge limitations
- Should encourage users to contribute missing docs back to knowledge base
- Keep responses concise but complete - developers want quick answers
