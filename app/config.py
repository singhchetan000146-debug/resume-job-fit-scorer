import json
import os
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]

class Settings(BaseModel):
    model_config = ConfigDict(extra='forbid')
    model_name: str
    batch_size: int = Field(16, ge=1, le=64)
    chunk_words: int = Field(64, ge=16, le=128)
    chunk_overlap: int = Field(16, ge=0)
    similarity_floor: float = Field(.30, ge=-1, le=1)
    similarity_ceiling: float = Field(.85, ge=-1, le=1)
    negation_score_cap: float = Field(30, ge=0, le=100)
    evidence_limit: int = Field(3, ge=1, le=5)
    weights: dict[str, float]
    importance_weights: dict[str, float]
    max_criteria: int = Field(30, ge=1, le=100)
    review_threshold: float = Field(60, ge=0, le=100)
    strong_evidence_threshold: float = Field(80, ge=0, le=100)
    max_file_bytes: int = Field(3145728, ge=1)
    max_pdf_pages: int = Field(20, ge=1)
    max_characters: int = Field(30000, ge=100, le=30000)

    @model_validator(mode='after')
    def valid(self):
        import math
        if self.similarity_floor >= self.similarity_ceiling:
            raise ValueError('similarity_floor must be below similarity_ceiling')
        if self.chunk_overlap >= self.chunk_words:
            raise ValueError('chunk_overlap must be smaller than chunk_words')
        for values, keys in [(self.weights, {'experience','education','skills','responsibility'}),
                              (self.importance_weights, {'required','preferred'})]:
            if set(values) != keys or any(not math.isfinite(v) or v <= 0 for v in values.values()):
                raise ValueError('Provide all expected weights as finite positive numbers')
        if self.review_threshold >= self.strong_evidence_threshold:
            raise ValueError('review threshold must be below strong evidence threshold')
        return self


def load_settings():
    return Settings.model_validate_json(Path(os.getenv('FIT_CONFIG', ROOT / 'config.json')).read_text())
