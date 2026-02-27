"""
Jobs API — curated job listings + market trends.
GET /jobs/list
GET /jobs/trends
"""
import json
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.groq_service import json_completion

router = APIRouter(prefix="/jobs", tags=["jobs"])


class Job(BaseModel):
    title: str
    company: str
    location: str
    salary: str = ""
    experience: str = ""
    skills: list[str] = []
    type: str = "Full Time"
    icon: str = "🏢"
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
def list_jobs(role: str = "", location: str = "India"):
    """
    Returns AI-generated representative job listings.
    In production, replace with a real job board API (Naukri, LinkedIn, etc.)
    """
    prompt = f"""
Generate 6 realistic tech job listings{f' for the role: {role}' if role else ''} in {location}.
Focus on Indian tech companies (Swiggy, Razorpay, Zomato, Flipkart, CRED, PhonePe, etc.) 
and FAANG India offices.

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
      "icon": "<relevant emoji>",
      "url": ""
    }}
  ]
}}
"""
    raw = json_completion(prompt, max_tokens=1500)
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        jobs = [Job(**j) for j in data.get("jobs", [])]
        return JobsResponse(jobs=jobs, total=len(jobs))
    except Exception:
        # Fallback static data
        return JobsResponse(
            jobs=[
                Job(title="Senior SDE", company="Razorpay", location="Bengaluru", salary="₹28–38 LPA", experience="4–6 YOE", skills=["React", "Node.js", "PostgreSQL"], icon="🏢"),
                Job(title="ML Engineer", company="Swiggy", location="Bengaluru", salary="₹22–32 LPA", experience="3–5 YOE", skills=["Python", "TensorFlow", "Spark"], icon="🚀"),
                Job(title="Backend SDE", company="CRED", location="Mumbai", salary="₹18–26 LPA", experience="2–4 YOE", skills=["Go", "Kafka", "Redis"], icon="💳"),
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
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)
        return TrendsResponse(**data)
    except Exception:
        return TrendsResponse(
            hot_roles=["AI/ML Engineer", "Full Stack Developer", "DevOps Engineer", "Data Scientist", "Cloud Architect"],
            top_skills=["Python", "React", "Kubernetes", "LLM Fine-tuning", "System Design"],
            salary_ranges={"fresher": "₹5–10 LPA", "mid": "₹15–30 LPA", "senior": "₹35–60 LPA"},
            insight="AI and cloud roles are seeing 40% salary premium in 2025. Indian startups are aggressively hiring backend and ML engineers.",
        )
