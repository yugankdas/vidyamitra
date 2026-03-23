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
    memories_found: list[str] = []


@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest):
    # 1. Multi-Stage Recall: Fetch broad context to ensure "no data missed"
    user_query = req.messages[-1].content if req.messages else ""
    
    all_memories = []
    # Broad sweeps for key data types
    all_memories += recall_memories("user resume analysis skills experience")
    all_memories += recall_memories("user interview performance feedback scores")
    all_memories += recall_memories("user quiz results domain mastery")
    # Specific sweep for the current question
    if user_query:
        all_memories += recall_memories(user_query)
    
    # Deduplicate while preserving order (approx)
    seen = set()
    memories = []
    for m in all_memories:
        m_stripped = m.strip()
        if m_stripped and m_stripped not in seen:
            memories.append(m_stripped)
            seen.add(m_stripped)

    # 2. Inject memories into system prompt if found
    enhanced_system = req.system
    if memories:
        enhanced_system += "\n\n=== USER CAREER HISTORY & PERSONAL DATA (HINDSIGHT) ===\n"
        enhanced_system += "You MUST use the following facts to personalize your answer. If the context below contains resume scores, interview feedback, or quiz results, refer to them explicitly.\n\n"
        enhanced_system += "\n".join([f"- {m}" for m in memories])
        enhanced_system += "\n\n=== END OF PERSONAL CONTEXT ===\n"

    # 3. Chat Completion
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = chat_completion(
        messages=msgs,
        system=enhanced_system,
        max_tokens=req.max_tokens,
    )
    
    # 4. Retain the new interaction
    if user_query:
        retain_memory(f"User: {user_query}\nAssistant: {reply}")

    return ChatResponse(reply=reply, memories_found=memories[:5])
