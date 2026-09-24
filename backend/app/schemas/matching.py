from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class ScoreBreakdown(BaseModel):
    verified_skills_component: float
    unverified_skills_component: float
    academic_fit_component: float
    project_fit_component: float

class SkillAnalysis(BaseModel):
    matched_verified_skills: List[str]
    matched_unverified_skills: List[str]
    missing_critical_skills: List[str]
    bonus_skills: List[str]

class ExplainableMatchOut(BaseModel):
    job_id: int
    job_title: str
    company_name: str
    overall_score: float
    match_tier: str  # Strong Fit (80%+) | Moderate Fit (60-79%) | Gap to Bridge (<60%)
    score_breakdown: ScoreBreakdown
    skill_analysis: SkillAnalysis
    readiness_verdict: str
    recommended_action: str

class RoadmapWeek(BaseModel):
    week_number: int
    theme: str
    goal: str
    key_topics: List[str]
    action_items: List[str]
    recommended_resources: List[str]
    milestone_project: str

class RoadmapOut(BaseModel):
    job_id: int
    target_role: str
    current_match_score: float
    projected_match_score: float
    summary: str
    weeks: List[RoadmapWeek]
    created_at: datetime
