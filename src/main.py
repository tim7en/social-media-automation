from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from .api.routers import content, platforms, auth, analytics, webhooks, starter_pro, workflows, api_keys
from .core.config import settings
from .core.database import engine
from .models import Base
from .core.logger import logger
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, InputValidationMiddleware
from .middleware.health_check import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Social Media Automation Platform")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize performance monitoring and caching
    from .utils.performance import init_performance_utils
    await init_performance_utils()
    
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

# Security middleware (order is important!)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=900)  # 100 calls per 15 minutes

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
app.include_router(health_router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(api_keys.router, prefix="/api/v1", tags=["API Keys"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content Generation"])
app.include_router(platforms.router, prefix="/api/v1/platforms", tags=["Social Platforms"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(starter_pro.router, prefix="/api/v1/starter-pro", tags=["Starter Pro"])
app.include_router(workflows.router, tags=["Workflows"])


@app.get("/api-keys")
async def api_keys_page():
    """Serve the API keys management page"""
    return FileResponse("static/templates/api-keys.html")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Social Media Automation Platform",
        "status": "healthy",
        "version": "1.0.0",
        "api_keys_management": "/api-keys"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # This endpoint is now handled by the health_router
        # but keeping this for backward compatibility
        return {
            "status": "healthy",
            "message": "Social Media Automation Platform",
            "version": "1.0.0",
            "redirect": "/health/detailed"
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
