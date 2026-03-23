"""
AI Chat endpoint — POST /ai/chat
Proxies the conversation to Groq LLM.
"""
import os
from fastapi import APIRouter
from pydantic import BaseModel
from hindsight import Hindsight
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


# Initialize Hindsight with a persistent bank
MEM_PATH = os.path.join(os.getcwd(), "app", "data", "memories")
os.makedirs(MEM_PATH, exist_ok=True)
hs = Hindsight(path=MEM_PATH)

@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest):
    # Retrieve relevant memories
    user_query = req.messages[-1].content if req.messages else ""
    memories = hs.recall(user_query)
    
    # Inject memories into system prompt if found
    enhanced_system = req.system
    if memories:
        enhanced_system += "\n\nRelevant Memories (Recall):\n" + "\n".join(memories)
        enhanced_system += "\n\nUse these memories to maintain context and continuity. If memories conflict with new info, prioritize new info but acknowledge the past."

    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = chat_completion(
        messages=msgs,
        system=enhanced_system,
        max_tokens=req.max_tokens,
    )
    
    # Retain the new interaction
    if user_query:
        hs.retain(f"User: {user_query}\nAssistant: {reply}")
        # Optionally reflect periodically (simplified for now)
        # hs.reflect() 

    return ChatResponse(reply=reply)
