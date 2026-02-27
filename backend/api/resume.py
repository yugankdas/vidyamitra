"""
Resume API — ATS analysis with structured JSON output.
POST /resume/analyze
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion

router = APIRouter(prefix="/resume", tags=["resume"])


class ResumeRequest(BaseModel):
    resume_text: str
    target_role: str = ""


class ATSResult(BaseModel):
    ats_score: int
    keyword_score: int
    impact_score: int
    missing_keywords: list[str]
    present_keywords: list[str]
    suggestions: list[str]
    section_scores: dict
    overall_feedback: str


@router.post("/analyze", response_model=ATSResult)
def analyze_resume(req: ResumeRequest):
    if len(req.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text too short")

    prompt = f"""
Analyze this resume for ATS compatibility{f' for the role: {req.target_role}' if req.target_role else ''}.

Resume:
{req.resume_text[:4000]}

Return a JSON object with EXACTLY these fields:
{{
  "ats_score": <integer 0-100>,
  "keyword_score": <integer 0-100>,
  "impact_score": <integer 0-100>,
  "missing_keywords": [<list of missing important keywords>],
  "present_keywords": [<list of found keywords>],
  "suggestions": [<list of 5 actionable improvement suggestions>],
  "section_scores": {{
    "experience": <0-100>,
    "education": <0-100>,
    "skills": <0-100>,
    "summary": <0-100>
  }},
  "overall_feedback": "<2-3 sentence summary>"
}}
"""

    raw = json_completion(prompt, max_tokens=1500)
    try:
        # Strip any accidental markdown
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return ATSResult(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
