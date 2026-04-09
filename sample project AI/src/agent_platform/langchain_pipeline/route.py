"""Routing via LangChain (heuristics or structured LLM classification)."""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent_platform.agents.db_agent import looks_db_related
from agent_platform.agents.incident import looks_incident_related
from agent_platform.config import settings

ROUTER_SYSTEM = """You are a routing classifier for an enterprise assistant.
Classify the user message into exactly one agent category.

- incident: incident numbers (INC-*, #123), resolving/closing incidents, Sev, outages tied to tickets
- cassandra_db: Cassandra/CQL, database queries, keyspaces/tables
- general: everything else
"""


class RouteDecision(BaseModel):
    agent: Literal["incident", "cassandra_db", "general"] = Field(
        description="Which specialized agent should handle the message"
    )
    reason: str = Field(default="", description="Brief justification")


def classify_heuristic(prompt: str) -> tuple[str, str]:
    if looks_incident_related(prompt):
        return "incident", "heuristic_incident"
    if looks_db_related(prompt):
        return "cassandra_db", "heuristic_db"
    return "general", "heuristic_general"


def _router_llm() -> ChatOpenAI | None:
    if not settings.llm_base_url or not settings.llm_api_key:
        return None
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url.rstrip("/"),
        temperature=0,
    )


async def decide_route(message: str) -> tuple[str, str]:
    if settings.use_llm_routing:
        llm = _router_llm()
        if llm is not None:
            structured = llm.with_structured_output(RouteDecision)
            msgs = [
                SystemMessage(content=ROUTER_SYSTEM),
                HumanMessage(content=message),
            ]
            out: RouteDecision = await structured.ainvoke(msgs)
            agent = out.agent if out.agent in ("incident", "cassandra_db", "general") else "general"
            return agent, out.reason or "llm_router"
    return classify_heuristic(message)
