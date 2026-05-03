from dataclasses import dataclass

from .agents import Agent
from .context import SharedContext


@dataclass(frozen=True)
class MultiAgentResult:
    final_output: str
    context: SharedContext
    approved: bool


class MultiAgentOrchestrator:
    def __init__(self, agents: list[Agent]) -> None:
        roles = [agent.role for agent in agents]
        if len(roles) != len(set(roles)):
            raise ValueError("Agent roles must be unique")
        self.agents = agents

    def run(self, request: str) -> MultiAgentResult:
        context = SharedContext(request=request)
        for agent in self.agents:
            context.add(agent.role, agent.run(context))

        review = context.by_role("reviewer")[-1] if context.by_role("reviewer") else ""
        approved = review.startswith("approved")
        final_output = context.by_role("writer")[-1] if approved else review
        return MultiAgentResult(final_output=final_output, context=context, approved=approved)

