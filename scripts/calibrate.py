"""Actual embedding evaluation. Never falls back to mocked vectors."""
import json
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config import load_settings
from app.embedding import Embedder
from app.schemas import AssessmentRequest
from app.scoring import assess


def main():
    config, engine = load_settings(), None
    engine = Embedder(config)
    jd = (ROOT / 'samples/job_description.txt').read_text()
    reports = {}
    for name in ['a','b','c']:
        report = assess(AssessmentRequest(job_description=jd, resume=(ROOT / f'samples/resume_{name}.txt').read_text()), config, engine)
        reports[name] = report.model_dump()
    repeated = assess(AssessmentRequest(job_description=jd,resume=(ROOT/'samples/resume_a.txt').read_text()),config,engine)
    gap = abs(reports['a']['overall_score']-reports['b']['overall_score'])
    margin = min(reports['a']['overall_score'], reports['b']['overall_score']) - reports['c']['overall_score']
    result = {'sample_type':'three synthetic resumes; small sanity check, not hiring validation',
        'model':config.model_name, 'similar_resume_gap':round(gap,2), 'weaker_resume_margin':round(margin,2),
        'repeat_score_delta':round(abs(repeated.overall_score-reports['a']['overall_score']),2),
        'warm_repeat_ms':repeated.metadata['elapsed_ms'],
        'acceptance':{'similar_gap_at_most_10':gap<=10, 'weaker_margin_at_least_15':margin>=15},
        'reports':reports}
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/calibration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='reports'},indent=2))
    print('scores:', {k:v['overall_score'] for k,v in reports.items()})
    return 0 if all(result['acceptance'].values()) else 1

if __name__ == '__main__':
    sys.exit(main())
