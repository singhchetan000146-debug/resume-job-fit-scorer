from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from app.config import load_settings
from app.embedding import Embedder, EmbeddingError
from app.parsing import InputError, parse_document
from app.schemas import AssessmentRequest, AssessmentResponse
from app.scoring import assess


def create_app(settings=None, embedder=None):
    config = settings or load_settings()
    engine = embedder or Embedder(config)
    app = FastAPI(title='Resume–JD Fit Scorer', version='1.0.0', description='Evidence assessment for human review. No automatic hiring decisions.')
    app.state.embedder = engine

    @app.exception_handler(InputError)
    async def invalid_input(request, exc):
        return JSONResponse(status_code=exc.status, content={'error':'unreadable_or_invalid_input','detail':str(exc)})

    @app.exception_handler(EmbeddingError)
    async def unavailable(request, exc):
        return JSONResponse(status_code=503, content={'error':'embedding_unavailable','detail':str(exc)})

    @app.get('/health')
    def health():
        return {'status':'ok', 'model_loaded':getattr(engine, 'model', None) is not None}

    @app.post('/assess', response_model=AssessmentResponse)
    def score(payload: AssessmentRequest):
        return assess(payload, config, engine)

    @app.post('/assess/files', response_model=AssessmentResponse)
    async def score_files(job_description: UploadFile = File(...), resume: UploadFile = File(...)):
        async def read(upload):
            try:
                data = await upload.read(config.max_file_bytes + 1)
                return await run_in_threadpool(parse_document, upload.filename, data, config)
            finally:
                await upload.close()
        jd_text, resume_text = await read(job_description), await read(resume)
        payload = AssessmentRequest(job_description=jd_text, resume=resume_text)
        return await run_in_threadpool(assess, payload, config, engine)

    return app

app = create_app()
