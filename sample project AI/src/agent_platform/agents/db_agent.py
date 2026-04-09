"""Cassandra (C*) read-only style agent — parameterized CQL only."""

from __future__ import annotations

import re
from typing import Any

from agent_platform.agents.base import AgentContext, AgentResult, BaseAgent
from agent_platform.config import settings

_CQLISH = re.compile(
    r"\b(?:select|from|where|cassandra|cql|keyspace|table|replica|consistency)\b",
    re.I,
)


def looks_db_related(text: str) -> bool:
    low = text.lower()
    if _CQLISH.search(text):
        return True
    if any(k in low for k in ("query the db", "query database", "run query", "c* ", "csandra")):
        return True
    return False


class CassandraAgent(BaseAgent):
    id = "cassandra_db"

    def __init__(self) -> None:
        self._session = None

    def _connect(self) -> Any:
        if self._session is not None:
            return self._session
        hosts = [h.strip() for h in settings.cassandra_hosts.split(",") if h.strip()]
        if not hosts:
            return None
        try:
            from cassandra.cluster import Cluster
            from cassandra.auth import PlainTextAuthProvider
        except ImportError:
            return None

        auth = None
        if settings.cassandra_username or settings.cassandra_password:
            auth = PlainTextAuthProvider(
                settings.cassandra_username or "",
                settings.cassandra_password or "",
            )
        cluster = Cluster(hosts, auth_provider=auth)
        self._session = cluster.connect(settings.cassandra_keyspace or None)
        return self._session

    async def run(self, prompt: str, ctx: AgentContext) -> AgentResult:
        session = self._connect()
        if session is None:
            return AgentResult(
                agent_id=self.id,
                content=(
                    "[DB agent] Cassandra not configured (set AGENT_CASSANDRA_HOSTS and optional "
                    "AGENT_CASSANDRA_KEYSPACE), or install extras: pip install 'agent-platform[cassandra]'.\n"
                    "When configured, only allow-listed parameterized SELECTs should run from the orchestrator."
                ),
                data={"configured": False},
            )

        # Demo: orchestrator should pass extracted CQL; here we only acknowledge capability.
        return AgentResult(
            agent_id=self.id,
            content=(
                "[DB agent] Session active. Route validated, parameterized CQL from the orchestrator "
                "to this agent — never concatenate raw user text into queries."
            ),
            data={"configured": True, "keyspace": settings.cassandra_keyspace},
        )
