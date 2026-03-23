"""
Resume API — ATS analysis with structured JSON output.
POST /resume/analyze
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion
from app.utils import clean_json_str
from app.services.memory_service import retain_memory

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
CRITICAL: NO EMOJIS.

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
        clean = clean_json_str(raw)
        data = json.loads(clean)
        
        # Hindsight: Retain the analysis result
        res = ATSResult(**data)
        role_label = f" (Target: {req.target_role})" if req.target_role else ""
        retain_memory(f"Resume ATS Analysis{role_label}: Score {res.ats_score}%. Feedback: {res.overall_feedback}. Missing Keywords: {', '.join(res.missing_keywords[:5])}")
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
