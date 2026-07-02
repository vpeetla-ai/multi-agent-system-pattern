# Multi-Agent System Pattern


<!-- vpeetla-tech-stack:start -->
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square)]() [![LangGraph](https://img.shields.io/badge/LangGraph-9333EA?style=flat-square)]() [![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square)]() [![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square)]()
<!-- vpeetla-tech-stack:end -->
**Part 4 of 5 — orchestrator + specialists with reviewer gates.** Used in **VAP Platform**.

[▶ Live demo](https://multi-agent-system-pattern.vercel.app) · [Architecture](docs/ARCHITECTURE.md) · [Portfolio](https://venkat-ai.com/work) · [VAP case study](https://github.com/vpeetla-ai/ai-architecture-portfolio/blob/main/case-studies/venkat-ai-platform.md)

## What this is

Production reference for multi-agent collaboration — specialized roles, delegation, coordinated handoffs.

## How we solve it

Orchestrator-controlled routing with critic/reviewer gates before final output; live trace UI for interviews and teaching.

## Case study & tradeoffs

[venkat-ai.com/work](https://venkat-ai.com/work) · Tradeoffs in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

Org skills: [vpeetla-ai-skills](https://github.com/vpeetla-ai/vpeetla-ai-skills). This repo includes `.cursor/skills/`, `AGENTS.md`, and `CONTEXT.md`.

```bash
git clone https://github.com/vpeetla-ai/vpeetla-ai-skills.git
./vpeetla-ai-skills/scripts/install.sh --cursor --codex --project .
```

---


## Implementation status

| Component | Status | Notes |
|-----------|--------|-------|
| Pattern demo + trace UI | ✅ | Live Vercel demo |
| Core agent loop | ✅ | Reference implementation |
| LangGraph production graph | 🟡 | Teaching scope — compose into VAP for fleet use |
| MCP tool bridge | ❌ | See LoopForge / VAP MCP docs |
| AegisAI gateway | ❌ | No side effects in pattern demo |
| Pytest regression | ✅ | `pytest -q` in repo |


[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://multi-agent-system-pattern.vercel.app)
[![Part of Production Agent Patterns](https://img.shields.io/badge/series-Production%20Agent%20Patterns-purple)](https://github.com/vpeetla-ai/multi-agent-system-pattern)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Part 4 of 5** in the [Production Agent Patterns](https://github.com/vpeetla-ai/react-agent-pattern) series.

Production-grade reference implementation of the **Multi-Agent System** pattern — specialized roles, delegation, and coordinated handoffs between agents.

| # | Pattern | Repository | Use when |
|---|---------|------------|----------|
| 1 | ReAct | [react-agent-pattern](https://github.com/vpeetla-ai/react-agent-pattern) | Tool use + reasoning loops |
| 2 | Reflection | [reflection-agent-pattern](https://github.com/vpeetla-ai/reflection-agent-pattern) | Self-critique and improve output |
| 3 | Plan-Execute | [plan-execute-agent-pattern](https://github.com/vpeetla-ai/plan-execute-agent-pattern) | Decompose goals into steps |
| 4 | **Multi-Agent** | **this repo** | Specialized role delegation |
| 5 | Swarm | [swarm-agent-pattern](https://github.com/vpeetla-ai/swarm-agent-pattern) | Parallel autonomous agents |

[▶ Live demo](https://multi-agent-system-pattern.vercel.app) · [📖 Full series roadmap](https://github.com/vpeetla-ai/ai-content-factory/blob/main/docs/agent-patterns/ROADMAP.md) · [🚀 See in production — AI Content Factory](https://ai-content-factory-iota.vercel.app)

---

## What you'll learn

- **Role-specialized agents** (researcher, writer, reviewer) with clear contracts
- Orchestrator delegates tasks and merges outputs
- Shared state vs. message-passing tradeoffs
- Boundaries that map to LangGraph / production service splits

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m multi_agent_system_pattern
pytest
```

Runs without external API keys using deterministic stubs.

```bash
cp .env.example .env
```

See [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## See it in production

[AI Content Factory](https://github.com/vpeetla-ai/ai-content-factory) uses this pattern at scale: Research → Content → SEO/Visual → HITL → Publisher agents on LangGraph.

[▶ Live demo](https://ai-content-factory-iota.vercel.app)

## Related

- **Previous:** [Plan-Execute Agent Pattern](https://github.com/vpeetla-ai/plan-execute-agent-pattern)
- **Next:** [Swarm Agent Pattern](https://github.com/vpeetla-ai/swarm-agent-pattern)

⭐ Star the repo if this pattern helps your work.
