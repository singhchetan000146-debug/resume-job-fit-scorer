from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field
from .config import settings
from .criteria import extract_criteria
from .parsers import extract_resume_text, ParseError
from .scorer import score_resume
from .models import FitResponse

app = FastAPI(title="Resume to Job-Description Fit Scorer", version="1.0.0")

class JDInput(BaseModel):
    job_description: str = Field(min_length=20)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score", response_model=FitResponse)
async def score(
    job_description: str = Form(..., min_length=20),
    resume: UploadFile = File(...)
):
    data = await resume.read()
    try:
        resume_text, warning = extract_resume_text(
            resume.filename or "resume.txt", data, settings.parser_min_chars
        )
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        criteria = extract_criteria(job_description)
        scored = score_resume(criteria, resume_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    overall = round(sum(x.weighted_score for x in scored), 2)
    return FitResponse(
        overall_score=overall,
        parser_warning=warning,
        criteria=scored
    )
