from pathlib import Path
import json
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseModel):
    weights: dict[str, float]
    embedding_model: str
    similarity_floor: float = 0.20
    similarity_ceiling: float = 0.75
    parser_min_chars: int = 40

def load_settings() -> Settings:
    with open(ROOT / "config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    total = sum(data["weights"].values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    return Settings(**data)

settings = load_settings()
