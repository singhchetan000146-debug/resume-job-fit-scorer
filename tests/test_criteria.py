from app.criteria import extract_criteria

def test_extracts_multiple_criteria():
    jd = """
    Required: Python and FastAPI.
    2+ years of experience building APIs.
    Bachelor's degree in Computer Science.
    Preferred: Docker and AWS.
    """
    criteria = extract_criteria(jd)
    assert len(criteria) >= 3
    assert abs(sum(c.weight for c in criteria) - 1.0) < 1e-6
