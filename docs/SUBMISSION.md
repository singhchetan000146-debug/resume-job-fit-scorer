# Submission checklist for Chetan Singh

## What the project contains

Working API, source code, configurable weights, three calibration samples with
real measurements, 24 tests, a one-page explanation PDF, and a recording outline.
The git history includes the original repository and incremental revision work.
No video or hours-spent claim is included: supply your actual recording and time.

## Submit these fields

1. GitHub repository URL: use your public repository only after the revised files
   are pushed. Confirm the README shows A/B/C = 87.81 / 78.89 / 31.82.
2. Explanation Document: upload `docs/Chetan_Singh_Explanation.pdf`.
3. Walkthrough Video Link: your own 3-5 minute Google Drive recording, shared
   as Anyone with the link, Viewer.
4. Hours Spent: report your actual time, including review and recording.

Open both links in an incognito/private window. Confirm the repository contents
and that the video plays without login. Anonymous Git reads were possible during
preparation; that does not replace checking the final submitted links yourself.

## If the GitHub update could not be pushed automatically

The downloadable package includes `resume-fit.bundle`, containing real history,
and a source snapshot. Extract the ZIP, then use Git in its outer folder:

```bash
git clone resume-fit.bundle resume-fit-submit
cd resume-fit-submit
git remote set-url origin https://github.com/singhchetan000146-debug/resume-job-fit-scorer.git
git fetch origin
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:main
```

Only push after the ancestor command succeeds (exit code 0). If the remote has
new work, stop and merge it; do not force-push. GitHub may ask you to sign in via
your local credential manager. Do not paste tokens into a chat or commit them.
A ZIP uploaded through GitHub's file-upload UI does not import the bundled
history; use the Git commands.

If no original repository update is wanted, create an empty public repository
in GitHub and use its URL as origin instead. The bundle preserves the history.

## Before you record

Follow the README setup and run:

```bash
python -m pytest -q
python scripts/calibrate.py
```

Read the PDF and the scoring code. Explain these points in your own words:
what cosine similarity measures; how scores are mapped; why the denominator sums
only the present weights; what happens when a PDF cannot be read; and why three
samples do not establish general accuracy.

The assignment offers one 48-hour extension if requested before the deadline.
An earlier screenshot shows a request was sent; it does not establish approval.
Verify the current deadline and any reply yourself. No extension email has been
sent as part of this revision.
