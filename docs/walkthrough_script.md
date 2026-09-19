# 3–5 Minute Walkthrough Script

**0:00–0:30 — What it does**  
“I'm showing a FastAPI resume-to-job-description fit scorer. It accepts a JD and a PDF/TXT resume and returns an overall score, per-criterion scores, reasoning, evidence, and parser warnings.”

**0:30–1:15 — Run it**  
Start with `uvicorn app.main:app --reload`, open `/docs`, paste a *new* JD you have not used in the repository, upload a new TXT/PDF resume, and execute `/score`. Point out the overall score and criterion breakdown.

**1:15–2:15 — Explain the scoring code**  
Open `app/scorer.py`. Show `model.encode(...)`, cosine similarity, the configured calibration range, and the small evidence bonus. Explain that the weights are in `config.json`, not embedded in the scoring logic.

**2:15–3:00 — Explain failure handling**  
Open `app/parsers.py`. Show that corrupt PDFs return an error and very short extracted text produces `parser_warning` rather than a fake confident score.

**3:00–3:45 — Calibration**  
Run the same JD against `resume_a.txt`, `resume_b.txt`, and `resume_c.txt`. Record the actual three overall scores in `docs/explanation.md`. Call out the A/B gap as the consistency check.

**3:45–4:15 — Honest limitations**  
“I did not implement OCR, a large labeled benchmark, or a full LLM criterion extractor. My next step would be OCR plus a 50–100 pair labeled evaluation set and comparison of heuristic vs. LLM extraction.”
