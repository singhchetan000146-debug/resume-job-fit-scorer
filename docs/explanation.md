# Design Explanation — Resume → JD Fit Scorer

**1. Design parameter — similarity calibration range (0.20–0.75).**  
I chose the cosine-similarity range used to map embeddings to a 0–100 semantic score after inspecting the behavior of the MiniLM embedding model on the three calibration resumes. Using raw cosine similarity directly made the score range too compressed and made small wording changes look disproportionately important. The configured range makes the score easier to interpret while keeping the underlying similarity visible in the reasoning. The category weights are separate and live in `config.json`, so business priorities can change without editing scoring logic.

**2. Failure actually observed.**  
The first parser implementation treated any PDF file as readable text. An image-only/scanned resume produced almost no extracted characters. The system could therefore have returned a confident-looking low score for the wrong reason. I changed the behavior to detect very short extracted text and return a `parser_warning` instead. Corrupt PDFs are rejected with HTTP 400. A production next step would add OCR rather than silently guessing.

**3. Metric tracked — score consistency across calibration samples.**  
I tracked the overall score for three resumes against the same JD, especially the absolute gap between the two near-duplicate resumes (A and B). This metric tells me whether wording changes are dominating the decision. The target is that A and B stay close while the partial-match resume C remains distinguishable. Before submission, I will record the actual scores from the running service here rather than claiming numbers I did not observe.

**4. Not finished / next step.**  
I did not finish OCR or a larger labeled benchmark, and the criteria extractor is a transparent heuristic rather than a full LLM extraction pipeline. Next I would add OCR for scanned PDFs, create 50–100 labeled resume/JD pairs, measure rank correlation/calibration error, and compare the heuristic extractor with an LLM extractor using the same scoring interface.
