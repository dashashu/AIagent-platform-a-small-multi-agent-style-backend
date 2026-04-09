"""Handles incident IDs, status, and resolution-oriented prompts."""

from __future__ import annotations

import re

from agent_platform.agents.base import AgentContext, AgentResult, BaseAgent

# Incident-like references: INC-12345, #12345, incident 42, P1-999
_INCIDENT_PATTERNS = [
    re.compile(r"\bINC[-\s]?\d+\b", re.I),
    re.compile(r"\bincedent\s*#?\d+\b", re.I),
    re.compile(r"\bincident\s*#?\d+\b", re.I),
    re.compile(r"\b(?:resolve|fix|close|reopen)\s+(?:the\s+)?incident\b", re.I),
    re.compile(r"\bP\d+\s*[-–]?\s*incident\b", re.I),
]


def looks_incident_related(text: str) -> bool:
    t = text.strip()
    if any(p.search(t) for p in _INCIDENT_PATTERNS):
        return True
    low = t.lower()
    if "incident" in low or "incedent" in low:  # common typo
        return True
    if any(k in low for k in ("resolve incident", "close ticket", "sev-1", "sev 1", "outage")):
        return True
    return False


class IncidentAgent(BaseAgent):
    id = "incident"

    async def run(self, prompt: str, ctx: AgentContext) -> AgentResult:
        refs = []
        for p in _INCIDENT_PATTERNS:
            refs.extend(m.group(0) for m in p.finditer(prompt))
        refs = list(dict.fromkeys(refs))

        lines = [
            "[Incident agent] Using your trained model + ticketing MCP, next steps would be:",
            "- Fetch ticket details via MCP (`get_ticket`) for referenced IDs.",
            "- Apply runbooks; optionally update status via MCP (`update_ticket`).",
        ]
        if refs:
            lines.insert(1, f"- Detected references: {', '.join(refs)}")
        content = "\n".join(lines)
        return AgentResult(agent_id=self.id, content=content, data={"references": refs})
