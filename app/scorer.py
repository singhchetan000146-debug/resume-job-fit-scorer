import re
import numpy as np
from sentence_transformers import SentenceTransformer
from .config import settings
from .models import Criterion, CriterionScore

_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = SentenceTransformer(settings.embedding_model)
        except Exception as exc:
            raise RuntimeError(
                f"Embedding model failed to load: {exc}. "
                "Check internet/model cache and install dependencies."
            ) from exc
    return _MODEL

def _keywords(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", text.lower()))

def _evidence(requirement: str, resume: str) -> list[str]:
    req_words = _keywords(requirement)
    lines = [x.strip() for x in resume.splitlines() if x.strip()]
    hits = []
    for line in lines:
        overlap = req_words & _keywords(line)
        if len(overlap) >= 1:
            hits.append(line[:240])
    return hits[:3]

def score_criterion(criterion: Criterion, resume: str) -> CriterionScore:
    model = _get_model()
    try:
        emb = model.encode([criterion.requirement, resume], normalize_embeddings=True)
        sim = float(np.dot(emb[0], emb[1]))
    except Exception as exc:
        raise RuntimeError(f"Embedding call failed: {exc}") from exc

    # Calibration: map the observed cosine range to 0-100 instead of using raw similarity.
    floor = settings.similarity_floor
    ceiling = settings.similarity_ceiling
    semantic = max(0.0, min(1.0, (sim - floor) / (ceiling - floor))) * 100

    hits = _evidence(criterion.requirement, resume)
    keyword_bonus = min(15.0, len(hits) * 5.0)
    score = min(100.0, 0.85 * semantic + keyword_bonus)

    if not resume.strip():
        score = 0.0

    reasoning = (
        f"Semantic similarity={sim:.3f}; calibrated semantic score={semantic:.1f}. "
        f"Found {len(hits)} supporting resume line(s). "
        f"Final criterion score={score:.1f}/100."
    )
    return CriterionScore(
        name=criterion.name,
        category=criterion.category,
        score=round(score, 2),
        weight=round(criterion.weight, 4),
        weighted_score=round(score * criterion.weight, 2),
        reasoning=reasoning,
        evidence=hits
    )

def score_resume(criteria: list[Criterion], resume: str) -> list[CriterionScore]:
    return [score_criterion(c, resume) for c in criteria]
