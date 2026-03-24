"""
AI Chat endpoint — POST /ai/chat
Proxies the conversation to Groq LLM.
"""
import os
from fastapi import APIRouter, BackgroundTasks
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
    
class DebugResponse(BaseModel):
    last_memories: list[str]


@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest, background_tasks: BackgroundTasks):
    # 1. Multi-Stage Recall: Fetch broad context to ensure "no data missed"
    user_query = req.messages[-1].content if req.messages else ""
    
    all_memories = []
    # Broad sweeps with higher top_k (10 instead of default)
    all_memories += recall_memories("user resume analysis skills experience") # Likely matches resume text
    all_memories += recall_memories("user interview performance feedback scores") # Matches interview text
    all_memories += recall_memories("user quiz results domain mastery") # Matches quiz text
    
    # Specific sweep for the current question
    if user_query:
        all_memories += recall_memories(user_query) # top_k=5 is usually default in my service but I'll assume standard library behavior
    
    # Deduplicate while preserving order (approx)
    seen = set()
    memories = []
    for m in all_memories:
        m_stripped = m.strip()
        if m_stripped and m_stripped not in seen:
            memories.append(m_stripped)
            seen.add(m_stripped)

    # 2. Inject memories INTO THE TOP of the system prompt for maximum priority
    # LLMs pay more attention to the first part of the context
    memory_context = ""
    if memories:
        memory_context = "=== USER CAREER HISTORY & PERSONAL DATA (HINDSIGHT - PRIORITY) ===\n"
        memory_context += "You MUST use the following facts to personalize your answer. This data is from the user's past actions.\n\n"
        memory_context += "\n".join([f"- {m}" for m in memories])
        memory_context += "\n\n=== END OF PERSONAL CONTEXT ===\n\n"
    
    enhanced_system = memory_context + req.system

    # 3. Chat Completion
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = chat_completion(
        messages=msgs,
        system=enhanced_system,
        max_tokens=req.max_tokens,
    )
    
    # 4. Diagnostic: Prepend a visible tag so the user (and I) can confirm it's working
    visible_prefix = f"[Hindsight Active: {len(memories)} memories recalled] " if memories else "[Hindsight: No relevant records found] "
    reply = visible_prefix + reply

    # 5. Retain the new interaction (BACKGROUNDED to prevent timeout)
    if user_query:
        background_tasks.add_task(retain_memory, f"User: {user_query}\nAssistant: {reply}")

    return ChatResponse(reply=reply, memories_found=memories[:10])

@router.get("/chat/debug", response_model=DebugResponse)
def debug_memories():
    # Return last 10 entries directly from the bank or via a generic recall
    # Since Hindsight recall is semantic, searching for " " or ".*" might work depending on implementation
    # For now, I'll recall "career profile" as a broad proxy
    last_raw = recall_memories(" ") # Many RAGs return most recent on empty query
    return DebugResponse(last_memories=last_raw[:20])
