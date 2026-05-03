from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Artifact:
    role: str
    content: str


@dataclass
class SharedContext:
    request: str
    context_id: str = field(default_factory=lambda: str(uuid4()))
    artifacts: list[Artifact] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.artifacts.append(Artifact(role=role, content=content))

    def by_role(self, role: str) -> list[str]:
        return [artifact.content for artifact in self.artifacts if artifact.role == role]

