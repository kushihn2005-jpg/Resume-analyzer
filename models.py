from pydantic import BaseModel
from typing import List, Optional


class ExtractedProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    total_years_experience: Optional[float] = None
    skills: List[str] = []
    education: List[str] = []
    job_titles: List[str] = []


class QualityIssue(BaseModel):
    category: str  # e.g. "formatting", "clarity", "quantification", "ats"
    severity: str  # "low", "medium", "high"
    description: str
    suggestion: str


class QualityReport(BaseModel):
    overall_score: int  # 0-100
    issues: List[QualityIssue]
    strengths: List[str]


class JDMatchResult(BaseModel):
    fit_score: int  # 0-100
    matched_keywords: List[str]
    missing_keywords: List[str]
    summary: str
    suggested_edits: List[str]


class AnalysisResponse(BaseModel):
    profile: ExtractedProfile
    quality: QualityReport
    jd_match: Optional[JDMatchResult] = None
