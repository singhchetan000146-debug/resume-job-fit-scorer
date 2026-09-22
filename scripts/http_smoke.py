"""Start a real server, make HTTP requests, save evidence, and stop it."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import httpx
ROOT=Path(__file__).resolve().parents[1]

def main():
    process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8765'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(base_url='http://127.0.0.1:8765',trust_env=False,timeout=120) as client:
            for _ in range(50):
                try:
                    client.get('/health').raise_for_status()
                    break
                except httpx.TransportError:
                    time.sleep(.1)
            else:
                raise RuntimeError('Server did not start')
            payload={'job_description':'Requirements:\nBuild Python services for order processing.\nWrite SQL queries for PostgreSQL.\nPreferred qualifications:\nUse Docker for application packaging.', 'resume':'Created Python services to process shop orders.\nMaintained PostgreSQL tables and wrote SQL reporting queries.\nPackaged the service in Docker containers.'}
            response=client.post('/assess',json=payload); response.raise_for_status()
            bad=client.post('/assess/files',files={'job_description':('jd.txt',payload['job_description']),'resume':('broken.pdf',b'%PDF-broken')})
            assert bad.status_code==422
            result={'request':payload,'http_status':response.status_code,'response':response.json(),'unreadable_pdf':{'status':bad.status_code,'body':bad.json()}}
            (ROOT/'results/http_smoke.json').write_text(json.dumps(result,indent=2)+'\n')
            print({'http_status':response.status_code,'overall_score':response.json()['overall_score'],'unreadable_pdf_status':bad.status_code})
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait()

if __name__=='__main__':
    main()
