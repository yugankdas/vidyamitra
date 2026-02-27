"""
Learning Journey API — AI-guided adaptive path based on quiz scores.
POST /learn/generate   → generate full learning path
POST /learn/adapt      → re-adapt path after new quiz score
GET  /learn/resources  → get curated YouTube/Coursera resources for a topic
"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_service import json_completion

router = APIRouter(prefix="/learn", tags=["learning"])


# ── Models ───────────────────────────────────────────

class QuizScore(BaseModel):
    domain: str       # e.g. "React", "System Design"
    score: int        # 0-100
    difficulty: str = "medium"


class LearningGenerateRequest(BaseModel):
    target_role: str
    quiz_scores: list[QuizScore] = []
    current_skills: list[str] = []
    weekly_hours: int = 10        # hours available per week


class Resource(BaseModel):
    title: str
    type: str          # "youtube" | "coursera" | "article" | "practice"
    url: str
    duration: str      # e.g. "4h 30m" or "6 weeks"
    difficulty: str    # "beginner" | "intermediate" | "advanced"
    why: str           # why this is recommended for this user


class Module(BaseModel):
    id: int
    title: str
    domain: str
    priority: str      # "critical" | "high" | "medium"
    current_score: int # from quiz, 0 if not taken
    target_score: int
    estimated_weeks: int
    why_this_now: str  # AI reasoning
    resources: list[Resource]
    milestone: str     # what they can do after completing this


class LearningPath(BaseModel):
    target_role: str
    overall_readiness: int        # 0-100
    total_weeks: int
    adapted_from_scores: bool
    modules: list[Module]
    next_action: str              # single most important thing to do right now
    motivational_note: str


class AdaptRequest(BaseModel):
    current_path: dict
    new_quiz: QuizScore


class ResourceRequest(BaseModel):
    topic: str
    level: str = "intermediate"
    count: int = 4


# ── Routes ───────────────────────────────────────────

@router.post("/generate", response_model=LearningPath)
def generate_learning_path(req: LearningGenerateRequest):
    scores_text = ""
    if req.quiz_scores:
        scores_text = "Quiz scores: " + ", ".join(
            f"{s.domain}: {s.score}%" for s in req.quiz_scores
        )
    else:
        scores_text = "No quiz scores yet — generate a balanced path."

    skills_text = f"Current skills: {', '.join(req.current_skills)}" if req.current_skills else ""

    prompt = f"""
You are an expert career coach for Indian tech professionals.
Build an adaptive AI learning path.

Target Role: {req.target_role}
{scores_text}
{skills_text}
Available time: {req.weekly_hours} hours/week

Rules:
- Modules with quiz score < 50 are "critical" priority
- Modules with score 50-70 are "high" priority  
- Modules with score > 70 are "medium" (polish)
- If no quiz taken for a domain, estimate from the role requirements
- For each module, recommend 2-3 REAL resources (actual YouTube channels/playlists or Coursera courses that exist)
- Use Indian context where relevant

Return ONLY valid JSON:
{{
  "overall_readiness": <0-100 integer>,
  "total_weeks": <integer>,
  "adapted_from_scores": {str(bool(req.quiz_scores)).lower()},
  "next_action": "<single most impactful action to take TODAY>",
  "motivational_note": "<1 sentence personal encouragement based on their scores>",
  "modules": [
    {{
      "id": 1,
      "title": "<module title>",
      "domain": "<domain name>",
      "priority": "<critical|high|medium>",
      "current_score": <0-100>,
      "target_score": <target 0-100>,
      "estimated_weeks": <integer>,
      "why_this_now": "<1 sentence AI reasoning why this module is prioritized>",
      "milestone": "<what they can do/build after completing this>",
      "resources": [
        {{
          "title": "<resource title>",
          "type": "<youtube|coursera|article|practice>",
          "url": "<real URL>",
          "duration": "<time estimate>",
          "difficulty": "<beginner|intermediate|advanced>",
          "why": "<why specifically for this user>"
        }}
      ]
    }}
  ]
}}

Include 3-5 modules total, ordered by priority. Keep it realistic and actionable.
"""

    raw = json_completion(prompt, max_tokens=3000)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        modules = [Module(**m) for m in data["modules"]]
        return LearningPath(
            target_role=req.target_role,
            overall_readiness=data.get("overall_readiness", 40),
            total_weeks=data.get("total_weeks", 12),
            adapted_from_scores=bool(req.quiz_scores),
            modules=modules,
            next_action=data.get("next_action", "Start with the first critical module"),
            motivational_note=data.get("motivational_note", "You're on the right path!"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse learning path: {e}")


@router.post("/adapt", response_model=LearningPath)
def adapt_learning_path(req: AdaptRequest):
    """Re-prioritize the existing path based on a new quiz result."""
    prompt = f"""
A user just completed a quiz and their path needs adapting.

New quiz result: {req.new_quiz.domain} = {req.new_quiz.score}%
Current path summary: {json.dumps(req.current_path, indent=2)[:2000]}

Re-generate the learning path with updated priorities.
If score >= 80, mark that module as "medium" or remove it.
If score < 50, escalate to "critical".
Keep the same JSON structure as before.

Return ONLY valid JSON with the same structure as the original path.
"""
    raw = json_completion(prompt, max_tokens=3000)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        modules = [Module(**m) for m in data["modules"]]
        return LearningPath(
            target_role=req.current_path.get("target_role", ""),
            overall_readiness=data.get("overall_readiness", 50),
            total_weeks=data.get("total_weeks", 10),
            adapted_from_scores=True,
            modules=modules,
            next_action=data.get("next_action", "Continue with updated priorities"),
            motivational_note=data.get("motivational_note", "Great progress!"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adapt path: {e}")


@router.post("/resources", response_model=list[Resource])
def get_resources(req: ResourceRequest):
    """Get curated YouTube/Coursera resources for a specific topic."""
    prompt = f"""
Recommend {req.count} real learning resources for: "{req.topic}" at {req.level} level.
Target audience: Indian tech professionals.

Include a mix of YouTube playlists/channels AND Coursera courses where applicable.
Use real, existing resources with accurate URLs.

Return ONLY a JSON array:
[
  {{
    "title": "<resource title>",
    "type": "<youtube|coursera|article|practice>",
    "url": "<real URL>",
    "duration": "<time>",
    "difficulty": "<beginner|intermediate|advanced>",
    "why": "<why this resource is great for this topic>"
  }}
]
"""
    raw = json_completion(prompt, max_tokens=1000)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return [Resource(**r) for r in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {e}")
