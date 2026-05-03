# Local Development Guide

## Current Runtime Behavior

This repo runs locally without external credentials. The default agents are deterministic:

- `ResearchAgent`
- `AnalystAgent`
- `WriterAgent`
- `ReviewerAgent`

The orchestrator executes the roles in sequence and stores their outputs in `SharedContext`.

## 1. Setup

```bash
cd /Users/lakshmipraveenabodempudi/multi-agent-system-pattern
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Run Locally

```bash
python -m multi_agent_system_pattern
```

No-key smoke run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m multi_agent_system_pattern
```

Expected behavior:

- Research agent creates evidence.
- Analyst agent consumes research.
- Writer agent drafts the response.
- Reviewer agent approves the output.
- Orchestrator returns the final result.

## 3. Run Tests

```bash
pytest
```

## 4. Environment Variables

Create a local `.env`:

```bash
cp .env.example .env
```

Important variables:

| Variable | Purpose |
| --- | --- |
| `RESEARCH_AGENT_MODEL` | Model for research role |
| `ANALYST_AGENT_MODEL` | Model for analysis role |
| `WRITER_AGENT_MODEL` | Model for writing role |
| `REVIEWER_AGENT_MODEL` | Model for review gate |
| `DATABASE_URL` | Shared context and artifact persistence |
| `VECTOR_DATABASE_URL` | Retrieval memory or enterprise knowledge |
| `ARTIFACT_STORE_URL` | Generated reports and role outputs |
| `MAX_AGENT_CALLS` | Coordination budget |
| `ENABLE_REVIEW_GATE` | Require reviewer approval |
| `ENABLE_HUMAN_ESCALATION` | Escalate rejected outputs |

## 5. Where To Add Real LLM Support

Add model-backed agents in:

```text
src/multi_agent_system_pattern/agents.py
```

Each production agent should:

- Have a clear role contract.
- Read only the context it needs.
- Write typed artifacts.
- Use least-privilege tool access.
- Emit trace events per action.

The orchestrator boundary is:

```text
src/multi_agent_system_pattern/orchestrator.py
```

Keep orchestration policy there: ordering, retries, review gates, parallelization, and escalation.

## 6. Where To Add Database Support

The shared context model lives in:

```text
src/multi_agent_system_pattern/context.py
```

Recommended persisted entities:

- `multi_agent_requests`
- `agent_artifacts`
- `agent_invocations`
- `shared_context_events`
- `review_decisions`
- `human_escalations`

## 7. Production Readiness Checks

- Every agent has a unique role.
- Artifacts are typed and auditable.
- Review gate blocks weak final outputs.
- Agents have least-privilege tools.
- Context does not leak sensitive information across roles.
- Per-agent cost and latency are tracked.

