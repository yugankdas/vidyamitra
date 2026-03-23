"""
Interview API — question generation + answer scoring.
POST /interview/question
POST /interview/score
"""
import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion, chat_completion
from app.utils import clean_json_str
from app.services.memory_service import retain_memory

router = APIRouter(prefix="/interview", tags=["interview"])


class QuestionRequest(BaseModel):
    role: str
    mode: str = "behavioral"  # "behavioral" | "technical"
    difficulty: str = "medium"


class QuestionResponse(BaseModel):
    question: str
    tips: list[str]
    follow_ups: list[str]


class ScoreRequest(BaseModel):
    question: str
    answer: str
    mode: str = "behavioral"


class ScoreResponse(BaseModel):
    score: int          # 0-100
    grade: str          # A, B, C, D
    strengths: list[str]
    improvements: list[str]
    star_feedback: str
    model_answer_hint: str


@router.post("/question", response_model=QuestionResponse)
def generate_question(req: QuestionRequest):
    prompt = f"""
Generate 1 interview question for the following role and mode.
Role: {req.role}
Mode: {req.mode} (behavioral, technical, or situational)
Difficulty: {req.difficulty}

Target Indian tech industry standards (top startups and FAANG).

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

Return JSON:
{{
  "question": "<the question text>",
  "tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "follow_ups": ["<follow-up question 1>", "<follow-up question 2>"]
}}
"""
    raw = json_completion(prompt, max_tokens=600)
    try:
        clean = clean_json_str(raw)
        data = json.loads(clean)
        return QuestionResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse: {e}")


@router.post("/score", response_model=ScoreResponse)
def score_answer(req: ScoreRequest):
    prompt = f"""
Score the user's interview answer based on the question and mode.
Question: {req.question}
Answer: {req.answer}
Mode: {req.mode}

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

Return JSON:
{{
  "score": <0-100 integer>,
  "grade": "<A/B/C/D/F>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "star_feedback": "<optional feedback on STAR method>",
  "model_answer_hint": "<brief hint of a great answer>"
}}
"""
    raw = json_completion(prompt, max_tokens=800)
    try:
        clean = clean_json_str(raw)
        data = json.loads(clean)
        
        # Hindsight: Retain the score
        score_res = ScoreResponse(**data)
        retain_memory(f"Interview session for role '{req.mode}' (evaluating '{req.question}'): Scored {score_res.score}% ({score_res.grade}). Improvements recommended: {', '.join(score_res.improvements[:3])}")
        
        return score_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse: {e}")
