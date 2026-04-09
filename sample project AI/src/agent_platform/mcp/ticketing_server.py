"""
Ticketing MCP server (stdio). Exposes tools for agents/IDEs to call your ticketing backend.

Run: python -m agent_platform.mcp.ticketing_server
Or: agent-mcp-ticketing (after pip install -e .)
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from agent_platform.ticketing.client import TicketingClient

mcp = FastMCP("ticketing-tools")
_client = TicketingClient()


def _dump(obj: Any) -> str:
    return json.dumps(obj, default=str)


@mcp.tool()
async def get_ticket(ticket_id: str) -> str:
    """Fetch a ticket/incident by id (e.g. INC-12345)."""
    result = await _client.get_ticket(ticket_id)
    return _dump(result)


@mcp.tool()
async def create_ticket(title: str, description: str, priority: str = "normal") -> str:
    """Create a new ticket. Priority: low, normal, high, urgent."""
    result = await _client.create_ticket(title, description, priority=priority)
    return _dump(result)


@mcp.tool()
async def update_ticket_status(ticket_id: str, status: str) -> str:
    """Update ticket status (e.g. open, in_progress, resolved, closed)."""
    result = await _client.update_ticket_status(ticket_id, status)
    return _dump(result)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
