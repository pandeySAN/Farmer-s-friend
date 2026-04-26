from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_tables
import app.schemas.models  # noqa: F401 — registers all ORM models with SQLAlchemy metadata
from app.routers import auth, farmer, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="FarmerAI API",
    description="AI-powered crop planning assistant for Indian farmers",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,   prefix=f"{settings.API_V1_STR}/auth",   tags=["🔐 Auth"])
app.include_router(farmer.router, prefix=f"{settings.API_V1_STR}/farmer", tags=["👨‍🌾 Farmer"])
app.include_router(chat.router,   prefix=f"{settings.API_V1_STR}/chat",   tags=["💬 Chat"])


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": "2.0.0"}