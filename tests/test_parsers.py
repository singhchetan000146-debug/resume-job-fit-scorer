from app.parsers import extract_resume_text, ParseError

def test_txt_parser():
    text, warning = extract_resume_text("resume.txt", b"Python engineer with FastAPI experience.")
    assert "Python" in text
    assert warning is None

def test_invalid_pdf_is_rejected():
    try:
        extract_resume_text("resume.pdf", b"not a real pdf")
    except ParseError:
        assert True
    else:
        assert False
