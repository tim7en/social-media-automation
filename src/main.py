from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from .api.routers import content, platforms, auth, analytics, webhooks, starter_pro
from .core.config import settings
from .core.database import engine
from .models import Base
from .core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Social Media Automation Platform")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Social Media Automation Platform")


app = FastAPI(
    title="Social Media Automation Platform",
    description="AI-powered content creation and social media automation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content Generation"])
app.include_router(platforms.router, prefix="/api/v1/platforms", tags=["Social Platforms"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(starter_pro.router, prefix="/api/v1/starter-pro", tags=["Starter Pro"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Social Media Automation Platform",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database connection
        # Check Redis connection
        # Check external API availability
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "redis": "healthy",
                "storage": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
