"""
Main FastAPI application for Stock Screener.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from app.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Indian Stock Market Screener with AI-powered Breakout Detection",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["screener"])

# Mount static files for frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    logger.info(f"Frontend directory mounted: {FRONTEND_DIR}")


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Perform initialization tasks.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Test Redis connection
    from app.services.redis_service import RedisService
    redis = RedisService()
    if redis.ping():
        logger.info("Redis connection successful")
    else:
        logger.error("Redis connection failed!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Cleanup tasks.
    """
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Serve the frontend UI."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback to API info if frontend not available
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
            "api": "/api/v1"
        }


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
