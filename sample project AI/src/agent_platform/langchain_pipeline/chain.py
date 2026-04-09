"""LangChain Runnable: orchestrates incident / Cassandra / general paths."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda

from agent_platform.agents.base import AgentContext
from agent_platform.agents.db_agent import CassandraAgent
from agent_platform.agents.incident import IncidentAgent
from agent_platform.chat.schemas import ChatResponse
from agent_platform.langchain_pipeline.route import decide_route


def _coerce_inputs(inputs: Any) -> dict[str, Any]:
    if isinstance(inputs, dict):
        return inputs
    dump = getattr(inputs, "model_dump", None)
    if callable(dump):
        return dump()
    raise TypeError(f"Unexpected chat input type: {type(inputs)!r}")


async def _orchestrate(inputs: Any) -> ChatResponse:
    raw = _coerce_inputs(inputs)
    message = str(raw.get("message", "")).strip()
    if not message:
        return ChatResponse(
            agent_id="general",
            content="Empty message.",
            route="general",
            route_reason="empty",
            data={},
        )

    ctx = AgentContext(
        user_id=raw.get("user_id"),
        session_id=raw.get("session_id"),
    )

    route, reason = await decide_route(message)
    incident = IncidentAgent()
    db = CassandraAgent()

    if route == "incident":
        result = await incident.run(message, ctx)
    elif route == "cassandra_db":
        result = await db.run(message, ctx)
    else:
        return ChatResponse(
            agent_id="general",
            content=(
                "[Orchestrator] No specialized agent matched. "
                "Plug your trained model into LangChain (e.g. ChatOpenAI with custom base_url) "
                "for open-domain answers, or ask about an incident / a Cassandra query."
            ),
            route="general",
            route_reason=reason,
            data={},
        )

    data = {**result.data, "route": route, "route_reason": reason}
    return ChatResponse(
        agent_id=result.agent_id,
        content=result.content,
        route=route,
        route_reason=reason,
        data=data,
    )


def build_orchestrator_runnable() -> RunnableLambda:
    return RunnableLambda(_orchestrate)
