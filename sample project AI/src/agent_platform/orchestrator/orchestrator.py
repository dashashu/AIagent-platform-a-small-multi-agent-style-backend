from __future__ import annotations

from langchain_core.runnables import Runnable

from agent_platform.agents.base import AgentContext, AgentResult
from agent_platform.langchain_pipeline.chain import build_orchestrator_runnable


class Orchestrator:
    """LangChain-backed dispatcher: incident / Cassandra / general."""

    def __init__(self, runnable: Runnable | None = None) -> None:
        self._runnable: Runnable = runnable or build_orchestrator_runnable()

    async def handle(self, prompt: str, ctx: AgentContext | None = None) -> AgentResult:
        ctx = ctx or AgentContext()
        payload = {
            "message": prompt,
            "user_id": ctx.user_id,
            "session_id": ctx.session_id,
        }
        out = await self._runnable.ainvoke(payload)
        if hasattr(out, "model_dump"):
            d = out.model_dump()
        else:
            d = dict(out)
        return AgentResult(
            agent_id=str(d.get("agent_id", "general")),
            content=str(d.get("content", "")),
            data=dict(d.get("data") or {}),
        )
