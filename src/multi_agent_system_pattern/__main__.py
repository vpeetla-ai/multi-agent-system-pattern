from .agents import AnalystAgent, ResearchAgent, ReviewerAgent, WriterAgent
from .orchestrator import MultiAgentOrchestrator


def main() -> None:
    result = MultiAgentOrchestrator(
        [ResearchAgent(), AnalystAgent(), WriterAgent(), ReviewerAgent()]
    ).run("Create an enterprise AI automation brief")
    print(result.final_output)
    print(f"approved={result.approved}")


if __name__ == "__main__":
    main()

