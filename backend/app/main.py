from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exams import router as exams_router
from app.api.questions import router as questions_router
from app.api.diagnostic import router as diagnostic_router
from app.config import settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Multi-Exam Preparation Platform (SSC CPO, SSC JE, WBP/KP Police)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(exams_router, prefix=settings.API_V1_STR)
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(diagnostic_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "database": str(settings.DATABASE_PATH),
        "vault": str(settings.VAULT_DIR)
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to EXAM-AI-COACH API. Navigate to /docs for interactive Swagger UI.",
        "version": "1.0.0"
    }
