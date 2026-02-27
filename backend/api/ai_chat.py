"""
AI Chat endpoint — POST /ai/chat
Proxies the conversation to Groq LLM.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.groq_service import chat_completion

router = APIRouter(prefix="/ai", tags=["ai"])


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    system: str = ""
    max_tokens: int = 800


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = chat_completion(
        messages=msgs,
        system=req.system,
        max_tokens=req.max_tokens,
    )
    return ChatResponse(reply=reply)
