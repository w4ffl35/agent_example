# Agent Engineer Take Home Exercise

## Build an Agent You’d Actually Use

**Why we’re giving you this**

We’re a team of senior engineers who like working with other seniors. We’re not testing for “gotchas” or textbook trivia. We’re looking for people who can design clean, thoughtful systems with LangGraph/LangChain, and explain tradeoffs in a way that shows taste and judgment.

If you can show us how you think, and leave us excited to pair with you, that’s a win.

**The Challenge**

Design and build a small agentic app that could plausibly live inside a business. We don’t care if it’s a CLI,, or lightweight web app, or something else, pick the medium you’re comfortable with.

The agent should:

- Use LangGraph for state and control flow.
- Use LangChain for model calls, tools, and RAG.
- Be instrumented with LangSmith for tracing and evals.
- Solve a problem end-to-end.

We suggest something like (feel free to use mocks/stubs for APIs and/or tool calls):

- Customer support triage
- HR policy assistant
- Travel booking helper
- Or your own creative idea (bonus points if it feels useful).

**Must-haves**

- Graph clarity: show how state moves and decisions are made.
- At least one tool (could be a stubbed API, DB, or file system).
- RAG: simple retrieval against a mini knowledge base you define.
- LangSmith traces: we should be able to see runs and metadata.
- Eval: one small dataset with expected outcomes.

**Nice-to-haves**

- PII redaction or guardrails.
- Streaming output to your interface.
- Docker, Makefile, or simple setup script.

**Deliverables**

- Repo link.
- Short README with:Quickstart instructions.
    - Graph diagram (Mermaid, draw.io, or screenshot).
    - Design notes: what you chose to do, and why.
    - What you’d improve with more time.
- We will also have you go over the app with us so we can ask questions and you can talk through it.

**How we’ll review**

- Taste: Does this feel like something we’d be proud to demo?
- Clarity: Is the graph/state easy to follow?
- Craft: Are decisions explained? Are tradeoffs sensible?
- Vibes: Do we see curiosity, creativity, and a little fun in how you approached it?

We don’t care about lines of code. We care about how you think, what you prioritize, and whether you’d bring good energy to a client project.