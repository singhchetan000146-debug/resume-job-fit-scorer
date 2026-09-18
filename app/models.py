from pydantic import BaseModel, Field

class Criterion(BaseModel):
    name: str
    category: str
    requirement: str
    weight: float = Field(gt=0, le=1)

class CriterionScore(BaseModel):
    name: str
    category: str
    score: float = Field(ge=0, le=100)
    weight: float
    weighted_score: float
    reasoning: str
    evidence: list[str]

class FitResponse(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    parser_warning: str | None = None
    criteria: list[CriterionScore]
