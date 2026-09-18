import re
from .models import Criterion
from .config import settings

CATEGORY_MAP = {
    "must_have_skills": ["required", "must", "should have", "skills", "qualification"],
    "experience": ["experience", "years", "worked", "background"],
    "education": ["degree", "bachelor", "master", "education", "qualification"],
    "tools": ["python", "sql", "fastapi", "flask", "aws", "docker", "git", "pandas", "excel",
              "kubernetes", "react", "java", "c++", "embedded", "stm32", "esp32"],
    "domain_knowledge": ["domain", "machine learning", "ai", "electronics", "vlsi", "pcb",
                         "semiconductor", "data science"],
    "nice_to_have": ["preferred", "plus", "nice to have", "bonus"]
}

def _category(text: str) -> str:
    low = text.lower()
    if any(x in low for x in CATEGORY_MAP["nice_to_have"]):
        return "nice_to_have"
    if any(x in low for x in CATEGORY_MAP["education"]):
        return "education"
    if any(x in low for x in CATEGORY_MAP["experience"]):
        return "experience"
    if any(x in low for x in CATEGORY_MAP["tools"]):
        return "tools"
    if any(x in low for x in CATEGORY_MAP["domain_knowledge"]):
        return "domain_knowledge"
    return "must_have_skills"

def extract_criteria(jd: str) -> list[Criterion]:
    # Transparent baseline: preserve bullet/sentence requirements instead of hiding extraction
    # behind a framework. Repeated/near-empty lines are removed.
    raw = re.split(r"\n|(?<=[.!?])\s+", jd)
    candidates = []
    for line in raw:
        s = re.sub(r"^[\s•\-*\d.)]+", "", line).strip()
        if len(s) < 12:
            continue
        low = s.lower()
        signal = any(k in low for vals in CATEGORY_MAP.values() for k in vals)
        if signal or len(candidates) < 6:
            candidates.append(s)

    # Deduplicate while keeping order.
    unique = []
    seen = set()
    for c in candidates:
        key = re.sub(r"\W+", " ", c.lower()).strip()
        if key not in seen:
            unique.append(c)
            seen.add(key)

    # Limit to actionable criteria. In a production system, an LLM extraction step could replace
    # this transparent baseline while keeping the same Criterion schema.
    unique = unique[:12]
    if not unique:
        unique = ["General fit to the supplied job description"]

    # Split configured weight among criteria by category. This makes weights externally configurable.
    counts = {}
    for u in unique:
        counts[_category(u)] = counts.get(_category(u), 0) + 1

    result = []
    for i, req in enumerate(unique, 1):
        cat = _category(req)
        weight = settings.weights.get(cat, 0.0) / counts[cat]
        result.append(Criterion(
            name=f"Criterion {i}",
            category=cat,
            requirement=req,
            weight=weight
        ))
    return result
