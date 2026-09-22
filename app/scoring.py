import re
import time
import numpy as np
from app.criteria import extract_criteria, chunk_resume
from app.parsing import validate_text
from app.schemas import AssessmentResponse, CriterionResult, Evidence


def assess(request, config, embedder):
    started = time.perf_counter()
    criteria = extract_criteria(validate_text(request.job_description, config), config)
    chunks = chunk_resume(validate_text(request.resume, config), config)
    vectors = embedder.embed([c.text for c in criteria] + chunks)
    similarities = np.clip(vectors[:len(criteria)] @ vectors[len(criteria):].T, -1, 1)
    total_weight = sum(config.weights[c.category] * config.importance_weights[c.importance] for c in criteria)
    results = []
    warnings = ['Scores measure text evidence, not verified competence or a hiring recommendation.',
                'Criteria extraction is rule-based. Check the extracted list and category weights.',
                'Numeric tenure, negation and multi-skill requirements require human verification.']
    for criterion, row in zip(criteria, similarities):
        indices = np.argsort(-row, kind='stable')[:config.evidence_limit]
        best = float(row[indices[0]])
        score = float(np.clip((best-config.similarity_floor)/(config.similarity_ceiling-config.similarity_floor)*100, 0, 100))
        negative = bool(re.search(r'\b(no experience|never used|not familiar|unfamiliar|have not|haven.t|lack of)\b', chunks[indices[0]], re.I))
        if negative:
            score = min(score, config.negation_score_cap)
        weight = config.weights[criterion.category] * config.importance_weights[criterion.importance]
        status = 'strong_evidence' if score >= config.strong_evidence_threshold else 'partial_evidence' if score >= config.review_threshold else 'needs_review'
        reason = f'Best evidence chunk {int(indices[0])} has cosine similarity {best:.3f}; configured linear mapping gives {score:.1f}/100.'
        if negative:
            reason += ' Possible negation detected; score capped. Verify this statement manually.'
        if status == 'needs_review':
            reason += ' Ask for a concrete example demonstrating this requirement.'
        results.append(CriterionResult(**criterion.model_dump(), score=round(score,2), weight=weight,
            contribution=round(score*weight/total_weight,4),
            evidence=[Evidence(chunk_id=int(i), text=chunks[i], similarity=round(float(row[i]),4)) for i in indices],
            reasoning=reason, status=status))
    return AssessmentResponse(overall_score=round(sum(r.contribution for r in results),2), criteria=results,
        warnings=warnings, metadata={'model':config.model_name, 'elapsed_ms':round((time.perf_counter()-started)*1000,2),
            'resume_chunks':len(chunks), 'config':config.model_dump(), 'score_meaning':'evidence alignment, not probability'})
