from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

from .parser import extract_text
from .analyzer import extract_profile, analyze_quality, match_job_description
from .models import AnalysisResponse

app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(default=None),
):
    file_bytes = await resume.read()
    try:
        resume_text = extract_text(file_bytes, resume.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the file. It may be a scanned image without OCR text.",
        )

    try:
        profile = extract_profile(resume_text)
        quality = analyze_quality(resume_text)

        jd_match = None
        if job_description and job_description.strip():
            jd_match = match_job_description(resume_text, job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {type(e).__name__}: {e}")

    return AnalysisResponse(profile=profile, quality=quality, jd_match=jd_match)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the simple frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")