# Resume → Job-Description Fit Scorer

A small applied-AI service that compares a resume (PDF/TXT) against a job description and returns an overall fit score plus per-criterion evidence and reasoning.

## Why this design

- **FastAPI + Pydantic**: typed request/response validation and a small HTTP surface.
- **PyMuPDF**: local PDF text extraction. TXT uses UTF-8 decoding with replacement.
- **Sentence Transformers**: one real embedding call is made for each criterion/resume comparison.
- **Config-driven weights**: category weights live in `config.json`; the scoring code does not hardcode business weights.
- **Transparent calibration**: raw cosine similarity is mapped from an empirically chosen range (`0.20–0.75`) to 0–100, then combined with a small evidence bonus. This reduces exaggerated score gaps between semantically similar resumes.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The first scoring request downloads/caches `all-MiniLM-L6-v2` if it is not already available.

## Usage

Open `http://127.0.0.1:8000/docs` and use `POST /score`.

The endpoint expects multipart form data:
- `job_description`: text
- `resume`: `.pdf` or `.txt`

Example curl:

```bash
curl -X POST "http://127.0.0.1:8000/score" ^
  -F "job_description=Required Python, FastAPI and 2 years API experience. Bachelor's degree preferred. Docker is a plus." ^
  -F "resume=@samples/resume_a.txt"
```

The response contains:
- `overall_score` from 0–100
- `parser_warning` if text extraction is suspicious
- per criterion: score, weight, weighted contribution, reasoning, and evidence lines

## Error handling

- Unsupported file types → HTTP 400
- Corrupt/unparseable PDFs → HTTP 400
- Empty/image-only PDFs → accepted with a low-confidence parser warning rather than pretending the resume was read
- Embedding model load/call failure → HTTP 503 with a useful error
- Invalid/missing request fields → FastAPI/Pydantic validation error

## Calibration

Use the three calibration samples in `samples/` with the same JD:

| Sample | Relationship | Intended observation |
|---|---|---|
| resume_a.txt | strong match | high score |
| resume_b.txt | very similar to A, wording changed | close to A |
| resume_c.txt | partial match | materially lower |

The key requirement is **consistency**, not a magic universal threshold. When A/B are semantically similar, their overall scores should remain close. Record your actual run results in the explanation document before submission.

## Tests

```bash
pytest -q
```

## What works vs. what doesn't

### Works
- PDF/TXT ingestion
- Criteria extraction
- Per-criterion embedding score
- Configurable weights
- Evidence lines and reasoning
- Parser warning for low-text PDFs
- LLM/embedding failure handling
- Calibration sample workflow

### Not finished
- OCR for scanned/image-only PDFs
- LLM-based extraction of nuanced requirements (the baseline is intentionally transparent and heuristic)
- A larger labeled evaluation set
- Authentication, persistence, frontend, and deployment

These are intentionally excluded because the assignment says infrastructure is not the scoring focus.

## Suggested Git history

Do not submit as one commit. Make small, meaningful commits, for example:

1. `chore: scaffold FastAPI service`
2. `feat: add pdf and txt resume parsing`
3. `feat: add configurable criteria extraction`
4. `feat: add embedding-based scoring`
5. `feat: add parser and embedding error handling`
6. `test: add calibration samples and API tests`
7. `docs: add explanation and usage guide`

## Important submission note

The evaluator asks for a **public GitHub repository** and a **public Google Drive walkthrough**. This project creates the local code, but you must push it to your own GitHub account and record/upload your own 3–5 minute video.
