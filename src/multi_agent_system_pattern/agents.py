from dataclasses import dataclass
from typing import Protocol

from .context import SharedContext


class Agent(Protocol):
    role: str

    def run(self, context: SharedContext) -> str:
        """Produce a role-specific artifact."""


@dataclass
class ResearchAgent:
    role: str = "research"

    def run(self, context: SharedContext) -> str:
        return f"Evidence gathered for '{context.request}'."


@dataclass
class AnalystAgent:
    role: str = "analysis"

    def run(self, context: SharedContext) -> str:
        evidence_count = len(context.by_role("research"))
        return f"Analysis completed using {evidence_count} research artifacts."


@dataclass
class WriterAgent:
    role: str = "writer"

    def run(self, context: SharedContext) -> str:
        return "Draft response combining research and analysis."


@dataclass
class ReviewerAgent:
    role: str = "reviewer"

    def run(self, context: SharedContext) -> str:
        has_research = bool(context.by_role("research"))
        has_analysis = bool(context.by_role("analysis"))
        has_draft = bool(context.by_role("writer"))
        if has_research and has_analysis and has_draft:
            return "approved: final output is grounded and complete"
        return "rejected: missing specialist artifacts"

