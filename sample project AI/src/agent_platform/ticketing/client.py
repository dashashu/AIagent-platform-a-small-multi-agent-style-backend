"""HTTP client for a generic ticketing REST API (configure via env — no secrets in code)."""

from __future__ import annotations

from typing import Any

import httpx

from agent_platform.config import settings


class TicketingClient:
    def __init__(self) -> None:
        self._base = settings.ticketing_base_url.rstrip("/")
        self._key = settings.ticketing_api_key

    def is_configured(self) -> bool:
        return bool(self._base)

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if self._key:
            h["Authorization"] = f"Bearer {self._key}"
        return h

    async def get_ticket(self, ticket_id: str) -> dict[str, Any]:
        if not self.is_configured():
            return {"ok": False, "error": "ticketing_not_configured", "ticket_id": ticket_id}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(f"{self._base}/tickets/{ticket_id}", headers=self._headers())
            if r.status_code >= 400:
                return {"ok": False, "status": r.status_code, "body": r.text}
            return {"ok": True, "ticket": r.json()}

    async def create_ticket(self, title: str, description: str, priority: str = "normal") -> dict[str, Any]:
        if not self.is_configured():
            return {"ok": False, "error": "ticketing_not_configured"}
        payload = {"title": title, "description": description, "priority": priority}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self._base}/tickets", json=payload, headers=self._headers())
            if r.status_code >= 400:
                return {"ok": False, "status": r.status_code, "body": r.text}
            return {"ok": True, "ticket": r.json()}

    async def update_ticket_status(self, ticket_id: str, status: str) -> dict[str, Any]:
        if not self.is_configured():
            return {"ok": False, "error": "ticketing_not_configured"}
        payload = {"status": status}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.patch(
                f"{self._base}/tickets/{ticket_id}",
                json=payload,
                headers=self._headers(),
            )
            if r.status_code >= 400:
                return {"ok": False, "status": r.status_code, "body": r.text}
            return {"ok": True, "ticket": r.json()}
