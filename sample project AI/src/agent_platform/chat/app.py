"""
Chat HTTP API via LangServe (LangChain). LangServe mounts runnables on a small FastAPI app.
"""

from __future__ import annotations

from fastapi import FastAPI
from langserve import add_routes

from agent_platform.chat.schemas import ChatRequest, ChatResponse
from agent_platform.langchain_pipeline.chain import build_orchestrator_runnable

app = FastAPI(title="Agent Platform Chat (LangServe)", version="0.1.0")
_chain = build_orchestrator_runnable()

add_routes(
    app,
    _chain,
    path="/v1/chat",
    input_type=ChatRequest,
    output_type=ChatResponse,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
