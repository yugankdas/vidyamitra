"""
Career API — personalized plan + skill gap detection.
POST /career/plan
POST /career/skill-gap
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion

router = APIRouter(prefix="/career", tags=["career"])


class CareerPlanRequest(BaseModel):
    resume_text: str
    target_role: str
    quiz_scores: dict = {}     # { "domain": score }
    timeline_weeks: int = 12


class WeekPlan(BaseModel):
    week: int
    focus: str
    tasks: list[str]
    resources: list[str]


class CareerPlanResponse(BaseModel):
    target_role: str
    readiness_score: int
    timeline_weeks: int
    weekly_plan: list[WeekPlan]
    key_milestones: list[str]
    top_resources: list[str]


class SkillGapRequest(BaseModel):
    current_skills: list[str]
    target_role: str


class SkillGapResponse(BaseModel):
    target_role: str
    match_percentage: int
    required_skills: list[str]
    present_skills: list[str]
    missing_skills: list[str]
    priority_skills: list[str]    # top 3 to learn first
    estimated_weeks: int


@router.post("/plan", response_model=CareerPlanResponse)
def career_plan(req: CareerPlanRequest):
    prompt = f"""
Create a {req.timeline_weeks}-week personalized career roadmap.
Target Role: {req.target_role}
Resume Summary: {req.resume_text[:1500]}
Quiz Scores: {json.dumps(req.quiz_scores)}

Return JSON:
{{
  "readiness_score": <0-100>,
  "weekly_plan": [
    {{
      "week": 1,
      "focus": "<topic focus>",
      "tasks": ["<task 1>", "<task 2>"],
      "resources": ["<resource 1>"]
    }}
  ],
  "key_milestones": ["<milestone 1>", "<milestone 2>", "<milestone 3>"],
  "top_resources": ["<resource with URL>", "<resource 2>", "<resource 3>"]
}}

Include only first 4 weeks in weekly_plan for brevity.
"""
    raw = json_completion(prompt, max_tokens=2000)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return CareerPlanResponse(
            target_role=req.target_role,
            timeline_weeks=req.timeline_weeks,
            weekly_plan=[WeekPlan(**w) for w in data.get("weekly_plan", [])],
            readiness_score=data.get("readiness_score", 50),
            key_milestones=data.get("key_milestones", []),
            top_resources=data.get("top_resources", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse plan: {e}")


@router.post("/skill-gap", response_model=SkillGapResponse)
def skill_gap(req: SkillGapRequest):
    prompt = f"""
Perform a skill gap analysis.
Target Role: {req.target_role}
Current Skills: {json.dumps(req.current_skills)}

Return JSON:
{{
  "match_percentage": <0-100>,
  "required_skills": ["<skill 1>", ...],
  "present_skills": ["<matched skill>", ...],
  "missing_skills": ["<missing skill>", ...],
  "priority_skills": ["<top 1>", "<top 2>", "<top 3>"],
  "estimated_weeks": <integer weeks to close gap>
}}
"""
    raw = json_completion(prompt, max_tokens=800)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return SkillGapResponse(target_role=req.target_role, **data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse gap: {e}")
