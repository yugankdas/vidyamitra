"""
Interview API — question generation + answer scoring.
POST /interview/question
POST /interview/score
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion, chat_completion

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
Generate a {req.difficulty} {req.mode} interview question for a {req.role} role at an Indian tech company.

Return JSON:
{{
  "question": "<the interview question>",
  "tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "follow_ups": ["<follow-up question 1>", "<follow-up question 2>"]
}}
"""
    raw = json_completion(prompt, max_tokens=600)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return QuestionResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse: {e}")


@router.post("/score", response_model=ScoreResponse)
def score_answer(req: ScoreRequest):
    prompt = f"""
Score this interview answer for a {req.mode} question.

Question: {req.question}
Answer: {req.answer}

Return JSON:
{{
  "score": <integer 0-100>,
  "grade": "<A|B|C|D>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "star_feedback": "<feedback on STAR method usage>",
  "model_answer_hint": "<brief hint for a better answer>"
}}
"""
    raw = json_completion(prompt, max_tokens=800)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return ScoreResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse: {e}")
