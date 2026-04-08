"""Auth Component Detector — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import CORS_ORIGINS
from models.schemas import HealthResponse
from routers import scrape, examples
from services import js_scraper

app = FastAPI(
    title="Auth Component Detector API",
    description="Scrape websites and detect authentication components (login forms, OAuth buttons, etc.)",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(scrape.router, prefix="/api", tags=["Scraping"])
app.include_router(examples.router, prefix="/api", tags=["Examples"])


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        playwright_available=js_scraper.is_available(),
    )


# Serve frontend static build if it exists (single-deployment mode)
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
