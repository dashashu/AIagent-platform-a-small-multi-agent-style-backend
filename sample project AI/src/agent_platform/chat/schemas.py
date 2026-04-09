from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    user_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    agent_id: str
    content: str
    route: str | None = None
    route_reason: str | None = None
    data: dict = Field(default_factory=dict)
