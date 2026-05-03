from multi_agent_system_pattern import (
    AnalystAgent,
    MultiAgentOrchestrator,
    ResearchAgent,
    ReviewerAgent,
    WriterAgent,
)


def test_multi_agent_orchestrator_collects_specialist_outputs() -> None:
    result = MultiAgentOrchestrator(
        [ResearchAgent(), AnalystAgent(), WriterAgent(), ReviewerAgent()]
    ).run("Prepare a customer support automation plan")

    assert result.approved
    assert len(result.context.artifacts) == 4
    assert result.final_output == "Draft response combining research and analysis."

