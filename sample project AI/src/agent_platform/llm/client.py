"""Assumes a trained/hosted LLM behind an OpenAI-compatible HTTP API (optional)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from agent_platform.config import settings


@dataclass
class LLMMessage:
    role: str
    content: str


class LLMClient:
    """Thin wrapper: no training logic — call your deployed model."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.llm_api_key
        self.model = model or settings.llm_model

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    async def chat(self, messages: list[LLMMessage], **kwargs: Any) -> str:
        if not self.is_configured():
            raise RuntimeError("LLM is not configured; set AGENT_LLM_BASE_URL and AGENT_LLM_API_KEY")
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{self.base_url}/v1/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]
