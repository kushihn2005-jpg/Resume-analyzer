"""Calls the Claude API to extract structured data and analyze resume quality."""
import json
import os
from anthropic import Anthropic

from .models import ExtractedProfile, QualityReport, JDMatchResult

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def _call_claude_json(system: str, user_prompt: str) -> dict:
    """Call Claude and parse a JSON object from its response."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def extract_profile(resume_text: str) -> ExtractedProfile:
    system = (
        "You extract structured data from resumes. "
        "Respond with ONLY a JSON object, no preamble, no markdown fences. "
        "Schema: {name, email, phone, total_years_experience (number), "
        "skills (array of strings), education (array of strings), "
        "job_titles (array of strings)}. Use null for unknown fields."
    )
    data = _call_claude_json(system, f"Resume text:\n\n{resume_text}")
    return ExtractedProfile(**data)


def analyze_quality(resume_text: str) -> QualityReport:
    system = (
        "You are an expert resume reviewer and ATS (Applicant Tracking System) specialist. "
        "Evaluate the resume for formatting issues, clarity, lack of quantified achievements, "
        "and ATS-parsing risks (tables, images, unusual fonts/columns, missing keywords sections). "
        "Respond with ONLY a JSON object, no preamble, no markdown fences. "
        "Schema: {overall_score (0-100 integer), "
        "issues: [{category, severity (low/medium/high), description, suggestion}], "
        "strengths: array of strings}."
    )
    data = _call_claude_json(system, f"Resume text:\n\n{resume_text}")
    return QualityReport(**data)


def match_job_description(resume_text: str, jd_text: str) -> JDMatchResult:
    system = (
        "You compare a resume against a job description to assess fit. "
        "Respond with ONLY a JSON object, no preamble, no markdown fences. "
        "Schema: {fit_score (0-100 integer), matched_keywords (array of strings), "
        "missing_keywords (array of strings), summary (2-3 sentence string), "
        "suggested_edits (array of specific, actionable strings)}."
    )
    user_prompt = f"Resume:\n\n{resume_text}\n\n---\n\nJob Description:\n\n{jd_text}"
    data = _call_claude_json(system, user_prompt)
    return JDMatchResult(**data)
