import re
from app.schemas import Criterion
from app.parsing import InputError


def extract_criteria(text, config):
    """Transparent rule-based extraction; source wording remains available for review."""
    result, seen = [], set()
    importance = 'required'
    skip_section = False
    for raw in re.split(r'\n|(?<=[.!?])\s+(?=[A-Z])', text):
        line = re.sub(r'^\s*(?:[-*•]+|\d+[.)])\s*', '', raw).strip()
        if not line:
            continue
        low = line.lower().rstrip(':')
        if low in {'preferred', 'preferred qualifications', 'nice to have', 'desirable'}:
            importance, skip_section = 'preferred', False
            continue
        if low in {'requirements', 'required', 'required qualifications', 'qualifications', 'responsibilities', 'must have', 'skills'}:
            importance, skip_section = 'required', False
            continue
        if low in {'benefits', 'about us', 'about the company', 'what we offer'}:
            skip_section = True
            continue
        if skip_section or len(line) < 12 or low in seen:
            continue
        if re.match(r'^(job title|location|salary|we are|join our|job description)\b', low):
            continue
        # Check experience before tools: "3 years of Python" is experience.
        if re.search(r'\b(years?|experience)\b', low):
            category = 'experience'
        elif re.search(r'\b(degree|bachelor|master|diploma|education|phd)\b', low):
            category = 'education'
        elif re.search(r'\b(python|sql|java|fastapi|flask|git|docker|aws|excel|skills?|proficien|knowledge|familiar)', low):
            category = 'skills'
        else:
            category = 'responsibility'
        level = 'preferred' if re.search(r'\b(preferred|optional|nice to have)\b', low) else importance
        result.append(Criterion(text=line, category=category, importance=level))
        seen.add(low)
    if not result:
        raise InputError('No criteria extracted. Provide explicit requirements, ideally one per line.')
    if len(result) > config.max_criteria:
        raise InputError(f'More than {config.max_criteria} criteria found. Shorten the job description.')
    return result


def chunk_resume(text, config):
    chunks = []
    for line in re.split(r'\n|(?<=[.!?])\s+', text):
        words = line.split()
        for start in range(0, len(words), config.chunk_words - config.chunk_overlap):
            chunk = ' '.join(words[start:start + config.chunk_words])
            if chunk and chunk not in chunks:
                chunks.append(chunk)
            if start + config.chunk_words >= len(words):
                break
    return chunks
