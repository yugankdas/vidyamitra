"""
Jobs API — curated job listings + market trends.
GET /jobs/list
GET /jobs/trends
"""
import json
import re
from fastapi import APIRouter
from pydantic import BaseModel
from app.utils import clean_json_str
from app.services.memory_service import retain_memory, recall_memories
import httpx

router = APIRouter(prefix="/jobs", tags=["jobs"])


class Job(BaseModel):
    title: str
    company: str
    location: str
    salary: str = ""
    experience: str = ""
    skills: list[str] = []
    type: str = "Full Time"
    url: str = ""


class JobsResponse(BaseModel):
    jobs: list[Job]
    total: int


class TrendsResponse(BaseModel):
    hot_roles: list[str]
    top_skills: list[str]
    salary_ranges: dict
    insight: str


@router.get("/list", response_model=JobsResponse)
async def list_jobs(role: str = "", location: str = "India"):
    """
    Returns REAL job listings from Adzuna API with an AI fallback.
    """
    from app.core.config import settings
    
    app_id = settings.adzuna_app_id
    app_key = settings.adzuna_app_key
    
    if app_id and app_key:
        try:
            # Adzuna API Search (India = 'in')
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": 6,
                "what": role or "software engineer",
                "content-type": "application/json"
            }
            if location and location.lower() != "india":
                params["where"] = location

            async with httpx.AsyncClient() as client:
                res = await client.get(url, params=params, timeout=10.0)
                res.raise_for_status()
                data = res.json()
                
                results = data.get("results", [])
                jobs = []
                for r in results:
                    jobs.append(Job(
                        title=r.get("title", "Untitled Role").replace("<strong>", "").replace("</strong>", ""),
                        company=r.get("company", {}).get("display_name", "Unknown Company"),
                        location=r.get("location", {}).get("display_name", "Remote / India"),
                        salary=f"₹{r.get('salary_min', 'N/A')} - {r.get('salary_max', '')}",
                        experience="Verified listing",
                        skills=[c.get("label", "") for c in r.get("category", {}).get("tag", []) if c][:3],
                        type="Remote" if "remote" in r.get("title", "").lower() else "Full Time",
                        url=r.get("redirect_url", "")
                    ))
                if jobs:
                    # Hindsight: Retain Search
                    retain_memory(f"User searched for jobs: {role} in {location}. Found {len(jobs)} results.")
                    return JobsResponse(jobs=jobs, total=len(jobs))
        except Exception:
            pass

    # fallback AI logic
    prompt = f"""
Generate 6 realistic tech job listings{f' for the role: {role}' if role else ''} in {location}.
Focus on Indian tech companies (Swiggy, Razorpay, Zomato, Flipkart, CRED, PhonePe, etc.) 
and FAANG India offices.

{f"Relevant User Interests (Hindsight Recall): {', '.join(recall_memories('job preferences'))}" if recall_memories('job preferences') else ""}

CRITICAL: DO NOT USE ANY EMOJIS IN ANY FIELD.

For each job, provide a realistic "url" that would lead to a search for that job on LinkedIn or Google (e.g., https://www.linkedin.com/jobs/search/?keywords=Software+Engineer+at+Razorpay).

Return JSON:
{{
  "jobs": [
    {{
      "title": "<job title>",
      "company": "<company name>",
      "location": "<city, India>",
      "salary": "<salary range in LPA>",
      "experience": "<X-Y YOE>",
      "skills": ["<skill1>", "<skill2>", "<skill3>"],
      "type": "Full Time",
      "url": "<realistic search URL>"
    }}
  ]
}}
"""
    raw = json_completion(prompt, max_tokens=1500)
    try:
        clean = clean_json_str(raw)
        data = json.loads(clean)
        jobs = [Job(**j) for j in data.get("jobs", [])]
        return JobsResponse(jobs=jobs, total=len(jobs))
    except Exception:
        # Fallback static data
        return JobsResponse(
            jobs=[
                Job(title="Senior SDE", company="Razorpay", location="Bengaluru", salary="₹28–38 LPA", experience="4–6 YOE", skills=["React", "Node.js", "PostgreSQL"], icon="🏢", url="https://www.linkedin.com/jobs/search/?keywords=Razorpay+SDE"),
                Job(title="ML Engineer", company="Swiggy", location="Bengaluru", salary="₹22–32 LPA", experience="3–5 YOE", skills=["Python", "TensorFlow", "Spark"], icon="🚀", url="https://www.linkedin.com/jobs/search/?keywords=Swiggy+ML"),
                Job(title="Backend SDE", company="CRED", location="Mumbai", salary="₹18–26 LPA", experience="2–4 YOE", skills=["Go", "Kafka", "Redis"], icon="💳", url="https://www.linkedin.com/jobs/search/?keywords=CRED+Backend"),
            ],
            total=3,
        )


@router.get("/trends", response_model=TrendsResponse)
def job_trends():
    prompt = """
What are the current tech job market trends in India (2025-2026)?

Return JSON:
{
  "hot_roles": ["<role 1>", "<role 2>", "<role 3>", "<role 4>", "<role 5>"],
  "top_skills": ["<skill 1>", "<skill 2>", "<skill 3>", "<skill 4>", "<skill 5>"],
  "salary_ranges": {
    "fresher": "₹5–10 LPA",
    "mid": "₹15–30 LPA",
    "senior": "₹35–60 LPA"
  },
  "insight": "<2-sentence market insight>"
}
"""
    raw = json_completion(prompt, max_tokens=600)
    try:
        clean = clean_json_str(raw)
        data = json.loads(clean)
        return TrendsResponse(**data)
    except Exception:
        return TrendsResponse(
            hot_roles=["AI/ML Engineer", "Full Stack Developer", "DevOps Engineer", "Data Scientist", "Cloud Architect"],
            top_skills=["Python", "React", "Kubernetes", "LLM Fine-tuning", "System Design"],
            salary_ranges={"fresher": "₹5–10 LPA", "mid": "₹15–30 LPA", "senior": "₹35–60 LPA"},
            insight="AI and cloud roles are seeing 40% salary premium in 2025. Indian startups are aggressively hiring backend and ML engineers.",
        )
