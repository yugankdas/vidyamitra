"""
Quiz API — AI quiz generation + grading.
POST /quiz/generate
POST /quiz/submit
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion

router = APIRouter(prefix="/quiz", tags=["quiz"])


class QuizGenerateRequest(BaseModel):
    domain: str           # e.g. "Machine Learning", "React", "System Design"
    difficulty: str = "medium"   # easy | medium | hard
    count: int = 8


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class QuizGenerateResponse(BaseModel):
    domain: str
    difficulty: str
    questions: list[QuizQuestion]


class QuizSubmitRequest(BaseModel):
    questions: list[dict]   # [{id, question, options, correct_index}]
    answers: list[int]      # user's chosen option index per question


class QuizResult(BaseModel):
    score: int              # percentage
    correct: int
    total: int
    grade: str
    feedback: str
    weak_areas: list[str]
    recommendations: list[str]


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz(req: QuizGenerateRequest):
    count = min(max(req.count, 2), 15)
    prompt = f"""
Create {count} multiple-choice quiz questions on the topic "{req.domain}" at {req.difficulty} difficulty.
Target audience: Indian tech students/professionals.

Return JSON:
{{
  "questions": [
    {{
      "id": 1,
      "question": "<question text>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "correct_index": <0-3>,
      "explanation": "<brief explanation of correct answer>"
    }}
  ]
}}
"""
    raw = json_completion(prompt, max_tokens=3000)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        questions = [QuizQuestion(**q) for q in data["questions"]]
        return QuizGenerateResponse(
            domain=req.domain,
            difficulty=req.difficulty,
            questions=questions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse quiz: {e}")


@router.post("/submit", response_model=QuizResult)
def submit_quiz(req: QuizSubmitRequest):
    if len(req.questions) != len(req.answers):
        raise HTTPException(status_code=400, detail="Questions and answers length mismatch")

    correct = sum(
        1 for q, a in zip(req.questions, req.answers)
        if a == q.get("correct_index", -1)
    )
    total = len(req.questions)
    score = round(correct / total * 100) if total else 0
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D"

    # Build prompt for AI feedback
    wrong = [
        req.questions[i]["question"]
        for i, (q, a) in enumerate(zip(req.questions, req.answers))
        if a != q.get("correct_index", -1)
    ]

    prompt = f"""
A student scored {score}% ({correct}/{total}) on a quiz.
Wrong questions: {json.dumps(wrong[:5])}

Return JSON:
{{
  "feedback": "<2-sentence performance summary>",
  "weak_areas": ["<area 1>", "<area 2>"],
  "recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"]
}}
"""
    raw = json_completion(prompt, max_tokens=500)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        ai_data = json.loads(clean)
    except Exception:
        ai_data = {
            "feedback": f"You scored {score}%. Keep practicing!",
            "weak_areas": [],
            "recommendations": ["Review the topics you missed", "Practice more questions"],
        }

    return QuizResult(
        score=score,
        correct=correct,
        total=total,
        grade=grade,
        **ai_data,
    )
