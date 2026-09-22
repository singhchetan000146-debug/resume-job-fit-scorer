# Chetan's walkthrough guide: aim for 4 minutes

Read the code and adapt this outline to your own words. Record your own voice;
do not claim you ran a test or built something without understanding what happened.
The measurements documented here were obtained during this AI-assisted revision.

Before recording: install dependencies, run the calibration once to cache the
model, start `python -m uvicorn app.main:app --reload`, and open `/docs`.
Create a NEW job description and resume not present in samples/ or results/.
Use fictional people and write explicit requirements, one per line. Do not reuse
the HTTP smoke example and call it unseen. Check your microphone with a short clip.

**0:00-0:25 - Introduce the problem.**
Say your name and explain that the tool returns criterion-level evidence and a
weighted fit assessment to help a recruiter ask better follow-up questions.
Mention Python, FastAPI, Pydantic and local FastEmbed embeddings.

**0:25-1:25 - Demonstrate unseen input.**
Open POST /assess/files in the API docs, upload your new JD and resume, and run it.
Show the overall score, one extracted requirement, its evidence passage and its
reasoning. Explain that a low score means insufficient matching text, not proof
that the candidate cannot do the job. Show a broken PDF returning a clear error
if time allows. You can create one by saving plain text with a .pdf extension.

**1:25-2:20 - Explain one code path.**
Open app/scoring.py. Explain the criteria-by-chunk similarity matrix, maximum
similarity, linear mapping, and weighted mean. Open config.json briefly to show
weights are configurable. Explain why there is no matching-line-count bonus.
If asked about the local model, app/embedding.py performs the actual model call,
validates vectors and raises an error caught as HTTP 503.

**2:20-3:10 - Explain calibration with evidence.**
Show results/baseline_calibration.json and results/calibration.json. Explain the
observed saturation at 100 and why the scale changed. Quote 87.81 / 78.89 / 31.82,
the 8.92-point gap, and the limitation of testing only three synthetic resumes.
Do not describe the scores as accuracy percentages.

**3:10-3:35 - Show a real prompt.**
Open docs/development_prompts.md and the matching conversation. The assignment
allows an embedding call instead of an LLM call, so this application has no
runtime chat prompt. Show the actual development instruction used with the coding
assistant and explain which requirements shaped the implementation. Do not invent
a runtime prompt. If the evaluator specifically means a runtime generative prompt,
clarify that interpretation before submission.

**3:35-4:15 - Finish with honest limitations.**
Show the one-page explanation. Mention OCR, compound requirements and larger
held-out evaluation as next steps. State that AI assistance was used and you can
explain the code. Stop the recording within the required 3-5 minutes.

Upload the video to Google Drive. Set General access to Anyone with the link,
Viewer. Open it in a private browser window while logged out and check that the
video plays with audible sound. Paste its public URL into the submission form.
