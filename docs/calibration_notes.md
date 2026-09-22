# Calibration experiment

This is a three-sample synthetic sanity check, not a validated recruiter benchmark.
The acceptance checks were specified in scripts/calibrate.py before the first run:
A/B gap <= 10 points and both at least 15 points above C.

Initial range 0.30-0.85 yielded A=100.00, B=99.82, C=52.90. This passed the gap
check but saturated almost every strong criterion. Inspecting raw similarities
showed that a ceiling of 0.85 clipped meaningful differences. The original
output is retained in results/baseline_calibration.json and commit history.

The revised mapping uses floor=0.40 and ceiling=1.00: identical vectors can reach
100, while close paraphrases retain some headroom. This is a transparent heuristic
chosen on these examples, not a learned probability or independently validated
threshold. After the change A=87.81, B=78.89, C=31.82; gap=8.92 points.
The wider 0.60 range also limits the slope: a 0.05 cosine change maps to 8.33
points before clipping and aggregation. It cannot guarantee all paraphrases
stay close; independent examples and recruiter labels are the next test.

No bonus depends on the number of matching lines. Repeating a statement cannot
increase its maximum similarity, and identical chunks are deduplicated. Required
criteria count twice as much as preferred criteria before category weighting.
Category weights are per criterion, so splitting one bullet into several changes
the total category influence. Verify the extracted criteria before interpreting
results. A multi-skill bullet can match only one skill strongly; it is not proof
that all named skills are present.

All measurements came from a real local FastEmbed model call. Unit tests use
explicit stubs only to isolate HTTP behavior and arithmetic. Download time is not
included in the warm repeat measurement. The model had already been downloaded
before calibration; the first sample includes model initialization.
