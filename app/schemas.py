from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    job_description: str = Field(min_length=20, max_length=30000)
    resume: str = Field(min_length=20, max_length=30000)

    @field_validator('job_description', 'resume', mode='before')
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value

class Criterion(BaseModel):
    text: str
    category: Literal['experience','education','skills','responsibility']
    importance: Literal['required','preferred']

class Evidence(BaseModel):
    chunk_id: int
    text: str
    similarity: float

class CriterionResult(Criterion):
    score: float = Field(ge=0, le=100)
    weight: float
    contribution: float
    evidence: list[Evidence]
    reasoning: str
    status: Literal['strong_evidence','partial_evidence','needs_review']

class AssessmentResponse(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    criteria: list[CriterionResult]
    human_review_required: bool = True
    warnings: list[str]
    metadata: dict
