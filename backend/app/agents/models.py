from pydantic import BaseModel

class ResumeModel(BaseModel):
    skills: list[str]
    projects: list[str]
    experience: list[str]
    education: list[str]

class JDModel(BaseModel):
    title: str
    company: str
    skills: list[str]
    seniority: str | None
    description_summary: str

class GapAnalysisModel(BaseModel):
    missing_skills: list[str]
    strengths: list[str]

class RecommendationModel(BaseModel):
    action_items: list[str]
    projected_improvement_pct: float

class CareerTrendModel(BaseModel):
    top_missing_skill: str
    skill_frequency: dict[str, float]
    most_valuable_project: str
    potential_match_increase_pct: float

class DailyReportModel(BaseModel):
    new_jobs: int
    high_match_jobs: int
    top_companies: list[str]
    strengths: list[str]
    company_insights: dict[str, str]
    weaknesses: list[str]
    recommended_action: str
