# import logging
# from contextlib import asynccontextmanager
# import asyncio
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from backend.core.config import(
#     ALLOWED_ORIGINS, 
#     APP_DESCRIPTION, 
#     APP_TITLE, 
#     APP_VERSION, 
#     SPACY_MODEL_PRIMARY, 
#     SPACY_MODEL_SECONDARY, SENTENCE_TRANSFORMER_MODEL
# )
# from backend.api.routes import router

# logger=logging.getLogger('ats_resume_scorer')

# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     logger.info('Starting ATS Resume Analyzer API...')

#     logger.info(f'Loading spaCy NLP model: {SPACY_MODEL_PRIMARY}')
#     import spacy
#     try:
#         app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
#         logger.info(f'Loaded {SPACY_MODEL_PRIMARY}')
#     except OSError:
#         logger.warning(f'{SPACY_MODEL_PRIMARY} not found — falling back to {SPACY_MODEL_SECONDARY}')
#         app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
#         logger.info(f'Loaded {SPACY_MODEL_SECONDARY} (fallback)')

#     logger.info(f'Loading SentenceTransformer: {SENTENCE_TRANSFORMER_MODEL}')
#     from sentence_transformers import SentenceTransformer
#     app.state.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
#     logger.info(f'Loaded {SENTENCE_TRANSFORMER_MODEL}')

#     logger.info('All models loaded. API is ready to serve requests.')

#     yield

#     logger.info('shutting down the api!!')

# app=FastAPI(
#     title=APP_TITLE, 
#     description=APP_DESCRIPTION, 
#     version=APP_VERSION, 
#     lifespan=lifespan,
#     docs_url='/docs',
#     redoc_url='/redoc'
# )

# app.add_middleware(
#     CORSMiddleware, 
#     allow_origins=ALLOWED_ORIGINS,
#     allow_credentials=True, 
#     allow_methods     = ['*'],
#     allow_headers     = ['*'],

# )

# app.include_router(router)

# @app.get('/')
# async def root():
#     return {
#         'name':      'ATS Resume Analyzer API',
#         'version':   '2.0.0',
#         'endpoints': {
#             'POST   /api/v1/analyze-resume': 'Analyze a resume',
#             'GET    /api/v1/history':        'Get user history',
#             'DELETE /api/v1/history/:id':    'Delete a history entry',
#             'GET    /api/v1/health':         'Health check',
#             'POST   /api/v1/generate-pdf':   'Generate PDF report from data',
#         },
#     }

# if __name__=='__main__':
#     import uvicorn
#     uvicorn.run(
#         'backend.main:app',
#         host    = '0.0.0.0',
#         port    = 8000,
#         reload  = True,    # Auto-restart on code changes (dev only)
#     )
# (chatgpt )

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import (
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
    SENTENCE_TRANSFORMER_MODEL,
)

from backend.api.routes import router

logger = logging.getLogger("ats_resume_scorer")


async def ensure_models_loaded(app: FastAPI):
    """Load ML models once, only when required."""

    if app.state.models_loaded:
        return

    async with app.state.model_lock:

        if app.state.models_loaded:
            return

        logger.info("Starting ML model initialization...")

        def load_models():
            import spacy
            from sentence_transformers import SentenceTransformer

            # Load spaCy
            logger.info("Loading spaCy model: %s", SPACY_MODEL_PRIMARY)

            try:
                nlp = spacy.load(SPACY_MODEL_PRIMARY)
                logger.info("Loaded %s", SPACY_MODEL_PRIMARY)

            except OSError:
                logger.warning(
                    "%s not found. Loading fallback: %s",
                    SPACY_MODEL_PRIMARY,
                    SPACY_MODEL_SECONDARY,
                )

                nlp = spacy.load(SPACY_MODEL_SECONDARY)
                logger.info("Loaded fallback model: %s", SPACY_MODEL_SECONDARY)

            # Load Sentence Transformer
            logger.info(
                "Loading SentenceTransformer: %s",
                SENTENCE_TRANSFORMER_MODEL,
            )

            embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)

            logger.info("SentenceTransformer loaded successfully")

            return nlp, embedder

        nlp, embedder = await asyncio.to_thread(load_models)

        app.state.nlp = nlp
        app.state.embedder = embedder
        app.state.models_loaded = True

        logger.info("All ML models loaded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting ATS Resume Analyzer API...")

    # Initialize empty model state.
    # Heavy models will load on the first analysis request.
    app.state.nlp = None
    app.state.embedder = None
    app.state.models_loaded = False
    app.state.model_lock = asyncio.Lock()

    logger.info("API startup completed. Models will load on demand.")

    yield

    logger.info("Shutting down ATS Resume Analyzer API...")


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": "ATS Resume Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/v1/analyze-resume": "Analyze a resume",
            "GET /api/v1/history": "Get user history",
            "DELETE /api/v1/history/:id": "Delete a history entry",
            "GET /api/v1/health": "Health check",
            "POST /api/v1/generate-pdf": "Generate PDF report from data",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
