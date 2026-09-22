# Resume to Job-Description Fit Scorer

**Chetan Singh | Task 1 | Python + FastAPI + local embeddings**

Upload a job description and a resume as PDF or TXT, or submit their text as JSON.
The API extracts individual requirements, retrieves supporting resume passages,
and returns a weighted score with evidence and reasoning for every criterion.
This is an evidence-review aid: a score is not a hiring decision or a probability
that a candidate is qualified.

## Start here

Use Python 3.11 or 3.12. Recorded verification used Python 3.12 on Linux.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install and start:

```bash
python -m pip install -r requirements-tested.txt
python -m uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs**. Expand `POST /assess/files`, click
**Try it out**, select a job-description PDF/TXT and a resume PDF/TXT, then
**Execute**. These are FastAPI's built-in API docs; no custom frontend is needed.

The first scoring call downloads `BAAI/bge-small-en-v1.5`. It needs internet and
can take much longer than subsequent calls. Model weights are cached in
`.model_cache/`. No API key is required. Once downloaded, embedding inference is
local; document text is not sent to an LLM service. Metadata checks during model
initialization can still require network, depending on the model library.

`requirements.txt` lists direct dependency ranges; `requirements-tested.txt`
pins the exact tested environment, including development tools. On a different
platform, install `requirements-dev.txt` if a pinned wheel is unavailable and rerun
the tests. Model-download revisions are not pinned, so model updates may alter
results. The saved metrics apply to the tested run, not all machines.

## API usage

| Endpoint | Input | Output |
|---|---|---|
| `GET /health` | none | service health and whether the model is loaded |
| `POST /assess` | JSON: `job_description`, `resume` | structured assessment |
| `POST /assess/files` | two multipart files with those same names | same assessment |

PowerShell file example (`curl.exe` avoids the PowerShell alias):

```powershell
curl.exe -X POST http://127.0.0.1:8000/assess/files -F "job_description=@samples/job_description.txt" -F "resume=@samples/resume_a.txt"
```

macOS / Linux:

```bash
curl -X POST http://127.0.0.1:8000/assess/files \
  -F 'job_description=@samples/job_description.txt' \
  -F 'resume=@samples/resume_a.txt'
```

For JSON, paste this into `POST /assess` in `/docs`:

```json
{
  "job_description": "Requirements:\nBuild Python backend services.\nWrite PostgreSQL queries.",
  "resume": "Developed Python backend services for inventory management.\nWrote PostgreSQL queries for monthly reporting."
}
```

The response contains `overall_score`, the extracted `criteria`, source passages
under `evidence`, per-criterion `score`, applied `weight`, normalized
`contribution`, `reasoning`, and `status`. `needs_review` means ask for a concrete
example; absence of strong text evidence does not establish absence of ability.
Metadata includes the actual configuration, model and request duration.
A complete real response is in [results/http_smoke.json](results/http_smoke.json).

## How scoring works

1. Parse and validate text. Reject empty, corrupt, encrypted or image-only PDFs.
2. Extract JD bullets/sentences with explicit rules, preserving their wording.
   Section headers distinguish required from preferred criteria.
3. Split resume sentences into overlapping windows of at most 64 words, with
   16-word overlap for long sentences. Deduplicate identical windows.
4. Make one batched embedding operation for criteria and resume windows. The
   model library internally processes batches of 16.
5. For each criterion, find the greatest cosine similarity to a resume window.
6. Map that similarity to a 0-100 evidence score and aggregate configured weights.

```text
criterion_score = 100 * clip((best_cosine - floor) / (ceiling - floor), 0, 1)
weight = category_weight * importance_weight
overall_score = sum(criterion_score * weight) / sum(weight)
```

A simple possible-negation detector caps the score at 30 when the strongest
passage includes phrases such as "no experience". This is a limited guard,
not reliable contradiction detection. Raw cosine and source evidence remain visible.
There is no keyword-count bonus; repeating a matching line cannot inflate its
maximum similarity.

## Configuration

Edit `config.json` and restart the server. All weights, score thresholds,
chunk sizes and file limits live there. `FIT_CONFIG` can select another file;
`FIT_MODEL_CACHE` can select a cache directory. Pydantic rejects invalid weight
keys, nonpositive weights, invalid score ranges and overlapping chunk settings.

| Setting | Value | Why |
|---|---:|---|
| Similarity floor / ceiling | 0.40 / 1.00 | retain headroom after the initial scale saturated |
| Skills / experience weights | 1.5 / 1.5 | give each of these criteria more influence |
| Education / responsibility weights | 1.0 / 1.0 | explicit baseline weights, adjustable per job |
| Required / preferred multiplier | 2.0 / 1.0 | emphasize stated requirements |
| Chunk words / overlap | 64 / 16 | keep short evidence passages and preserve boundary context |
| File / PDF / text limits | 3 MiB / 20 pages / 30,000 characters | bound this local prototype's input |

Weights apply **per criterion**, not per category budget. A category with many
bullets receives more total influence. Check the extracted list before using a
score. Different jobs and configurations produce scores that are not directly
comparable.

## Actual calibration and tests

```bash
python -m pytest -q
python scripts/calibrate.py
python scripts/http_smoke.py
```

The recorded run passed **24 tests**. Two dependency deprecation warnings were
observed; they did not fail the tests. Unit tests isolate API/validation/arithmetic
with explicit stubs. The two scripts above use the **real embedding model**.
`calibrate.py` exits nonzero if A/B differ by more than 10 points or either is less
than 15 points above C. It does not substitute fake scores if the model fails.

| Synthetic resume | Description | Actual score |
|---|---|---:|
| A | directly relevant backend experience | 87.81 |
| B | similar experience, paraphrased | 78.89 |
| C | graphic-design experience | 31.82 |

A/B gap: **8.92 points**. Weaker-resume margin: **47.07 points**. Repeat A score
change: **0.00**. One warm repeat took **112.49 ms** on the test machine.
This is a tiny, in-sample consistency check, not general accuracy evidence.
See [raw results](results/calibration.json) and
[before/after rationale](docs/calibration_notes.md). The first scale produced
100.00 / 99.82 / 52.90; the retained baseline shows why the range changed.
The separate HTTP smoke input was not used to select the range.

## Errors and limitations

| Condition | Behavior |
|---|---|
| Missing fields, short text, invalid JSON types | 422 validation error |
| Empty / corrupt / encrypted / image-only PDF or invalid UTF-8 | 422 with corrective message |
| Unsupported extension | 415 |
| File, extracted text or page limit exceeded | 413 |
| Model download/inference failure or nonfinite vectors | 503; no invented assessment |
| Invalid server configuration | startup fails clearly |

**Works:** both inputs as TXT/PDF, JSON input, criteria extraction, real local
embeddings, normalized aggregation, configurable weights, evidence retrieval,
calibration script, parser failure handling and model failure handling.

**Not finished:** OCR, reliable tenure/date arithmetic, nuanced negation, atomic
splitting of multi-skill bullets, multilingual evaluation, recruiter-labeled
validation and model revision pinning. Heuristics work best with explicit English
requirements, one per line. Complex PDF layouts can reorder text. A very long JD
bullet can exceed the embedding tokenizer's limit. Model calls are serialized in
this prototype and do not have a hard inference deadline. Input limits do not
replace production request-body/rate limits. Do not expose this unauthenticated
prototype to the public internet.

There is no deployment, authentication, custom frontend or database: none is
needed to demonstrate the assignment. Uploaded files are not saved by the app;
only explicitly run evaluation scripts write local synthetic results.

## Submission files

- [One-page explanation PDF](docs/Chetan_Singh_Explanation.pdf)
- [Explanation source](docs/explanation.md)
- [3-5 minute walkthrough guide](docs/walkthrough_script.md)
- [Actual development prompt record](docs/development_prompts.md)
- [Submission and GitHub instructions](docs/SUBMISSION.md)

Built with AI assistance. Chetan should review the implementation and explain its
trade-offs in his own words. The walkthrough video and hours-spent statement must
come from the actual submission work; neither has been fabricated.

This revision replaces the earlier MiniLM/whole-resume scoring approach with
FastEmbed and passage evidence, removes a line-count bonus, normalizes the
weights present in each JD, and accepts a file for the JD too. The API changes
from `/score` to `/assess` and `/assess/files`; the new configuration is not
compatible with the old keys. Earlier implementation remains in Git history.

## Primary references

- [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastEmbed quickstart](https://qdrant.tech/documentation/fastembed/fastembed-quickstart/)
- [pypdf text extraction and OCR limitations](https://pypdf.readthedocs.io/en/6.0.0/user/extract-text.html)
