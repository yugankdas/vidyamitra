"""
Learning Journey API — AI-guided adaptive path based on quiz scores.
POST /learn/generate   → generate full learning path
POST /learn/adapt      → re-adapt path after new quiz score
GET  /learn/resources  → get curated YouTube/Coursera resources for a topic
"""
import json
import re
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.groq_service import json_completion
from app.utils import clean_json_str

# Setup logging
logger = logging.getLogger(__name__)

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
    search_query: str = "" # Fallback search if URL is invalid
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

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

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
  "adapted_from_scores": {"true" if req.quiz_scores else "false"},
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
          "search_query": "<high-intent search query for this specific resource>",
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

    logger.info(f"Generating learning path for role: {req.target_role}")
    raw = json_completion(prompt, max_tokens=2500) # Slightly reduced to avoid timeouts
    
    try:
        clean = clean_json_str(raw)
        data = json.loads(clean)
        
        # Robust module parsing
        raw_modules = data.get("modules", [])
        if not isinstance(raw_modules, list):
            raw_modules = []
            
        modules = []
        for m in raw_modules:
            try:
                # Ensure resources is a list
                if "resources" not in m or not isinstance(m["resources"], list):
                    m["resources"] = []
                
                # Use .get() or provide defaults for Pydantic to avoid strictness failures
                modules.append(Module(
                    id=m.get("id", len(modules) + 1),
                    title=m.get("title", "Untitled Module"),
                    domain=m.get("domain", req.target_role),
                    priority=m.get("priority", "medium"),
                    current_score=m.get("current_score", 0),
                    target_score=m.get("target_score", 90),
                    estimated_weeks=m.get("estimated_weeks", 2),
                    why_this_now=m.get("why_this_now", m.get("why", "Recommended for your path")),
                    resources=[Resource(**r) for r in m["resources"] if isinstance(r, dict) and "url" in r],
                    milestone=m.get("milestone", "Complete this module")
                ))
            except Exception as mod_err:
                logger.warning(f"Failed to parse module: {mod_err}. Data: {m}")
                continue

        if not modules:
             raise ValueError("No valid modules could be parsed from AI response")

        return LearningPath(
            target_role=req.target_role,
            overall_readiness=data.get("overall_readiness", 40),
            total_weeks=data.get("total_weeks", sum(m.estimated_weeks for m in modules)),
            adapted_from_scores=bool(req.quiz_scores),
            modules=modules,
            next_action=data.get("next_action", "Start with the first module"),
            motivational_note=data.get("motivational_note", "You're on the right path!"),
        )
    except Exception as e:
        logger.error(f"Learning Path Generation Error: {str(e)}\nRaw Response: {raw}")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path. The AI response was invalid or incomplete.")


@router.post("/adapt", response_model=LearningPath)
def adapt_learning_path(req: AdaptRequest):
    """Re-prioritize the existing path based on a new quiz result."""
    prompt = f"""
A user just completed a quiz and their path needs adapting.

New quiz result: {req.new_quiz.domain} = {req.new_quiz.score}%
Current path summary: {json.dumps(req.current_path, indent=2)[:2000]}

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

Re-generate the learning path with updated priorities.
If score >= 80, mark that module as "medium" or remove it.
If score < 50, escalate to "critical".
Keep the same JSON structure as before.

Return ONLY valid JSON with the same structure as the original path.
"""
    raw = json_completion(prompt, max_tokens=3000)
    try:
        clean = clean_json_str(raw)
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

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

Include a mix of YouTube playlists/channels AND Coursera courses where applicable.
Use real, existing resources with accurate URLs.

Return ONLY a JSON array:
[
  {{
    "title": "<resource title>",
    "type": "<youtube|coursera|article|practice>",
    "url": "<real URL>",
    "search_query": "<high-intent search query for this specific resource>",
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
