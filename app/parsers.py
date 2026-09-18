from pathlib import Path
import fitz

class ParseError(Exception):
    pass

def extract_resume_text(filename: str, data: bytes, min_chars: int = 40) -> tuple[str, str | None]:
    suffix = Path(filename).suffix.lower()
    warning = None

    try:
        if suffix == ".txt":
            text = data.decode("utf-8", errors="replace").strip()
        elif suffix == ".pdf":
            doc = fitz.open(stream=data, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc).strip()
            doc.close()
        else:
            raise ParseError("Only PDF and TXT resumes are supported.")
    except Exception as exc:
        raise ParseError(f"Could not parse resume: {exc}") from exc

    if len(text) < min_chars:
        warning = (
            "Resume text could not be reliably extracted. The PDF may be scanned/image-only "
            "or the file may be empty/corrupt. Score is marked low-confidence."
        )
    return text, warning
