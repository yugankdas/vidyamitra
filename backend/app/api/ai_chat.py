"""
AI Chat endpoint — POST /ai/chat
Proxies the conversation to Groq LLM.
"""
import os
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.memory_service import retain_memory, recall_memories
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
    # Retrieve relevant memories
    user_query = req.messages[-1].content if req.messages else ""
    memories = recall_memories(user_query)
    
    # Inject memories into system prompt if found
    enhanced_system = req.system
    if memories:
        enhanced_system += "\n\nRelevant Memories (Hindsight Recall):\n" + "\n".join(memories)
        enhanced_system += "\n\nUse these memories to maintain context and continuity. If memories conflict with new info, prioritize new info but acknowledge the past."

    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = chat_completion(
        messages=msgs,
        system=enhanced_system,
        max_tokens=req.max_tokens,
    )
    
    # Retain the new interaction
    if user_query:
        retain_memory(f"User: {user_query}\nAssistant: {reply}")

    return ChatResponse(reply=reply)
