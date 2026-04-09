from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_id: str
    content: str
    data: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    id: str = "base"

    async def run(self, prompt: str, ctx: AgentContext) -> AgentResult:
        raise NotImplementedError
