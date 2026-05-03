# Multi-Agent System Pattern

Production-grade reference implementation of a centralized multi-agent architecture with specialized agents, an orchestrator, shared context, and review before final output.

## Highlights

- Research, analysis, writing, and review agents with separate interfaces.
- Orchestrator controls collaboration order.
- Shared context records artifacts from each role.
- Reviewer gates final output quality.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m multi_agent_system_pattern
pytest
```

