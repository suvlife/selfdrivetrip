"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.models.route import SavedSearch
from app.schemas.route import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    SavedSearchCreate,
    SavedSearchOut,
)
from app.routers import routes as routes_router
from app.routers import generate as generate_router
from app.services.weather_service import get_weather
from app.services.image_service import search_images
from app.services.poi_service import search_poi
from app.services.article_service import search_articles

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("Starting SelfDriveTrip API...")
    init_db()
    logger.info("Database tables created/verified.")
    yield
    logger.info("Shutting down SelfDriveTrip API...")


app = FastAPI(
    title=settings.APP_NAME,
    description="SelfDriveTrip - AI-powered self-driving trip route planner",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_router.router)
app.include_router(generate_router.router)

# ─── General-purpose API router ──────────────────────────────────────────────

general = APIRouter(prefix="/api", tags=["general"])


@general.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", app="SelfDriveTrip", version="1.0.0")


@general.get("/weather")
async def weather_data(city: str = Query(..., description="City name"), db: Session = Depends(get_db)):
    """Get weather data for a city."""
    result = await get_weather(city)
    return result


@general.get("/images")
async def image_search(
    query: str = Query(..., description="Search term"),
    per_page: int = Query(9, ge=1, le=30),
):
    """Search images."""
    results = await search_images(query, per_page)
    return {"query": query, "results": results}


@general.get("/poi")
async def poi_search(
    city: str = Query(..., description="City name"),
    keyword: str = Query(..., description="POI search keyword"),
    types: str = Query(None, description="POI type filter"),
    page: int = Query(1, ge=1),
):
    """Search Points of Interest via Baidu Maps API."""
    results = await search_poi(city, keyword, types, page)
    return {"city": city, "keyword": keyword, "results": results}


@general.get("/articles")
async def article_search(
    query: str = Query(..., description="Search term"),
    max_results: int = Query(5, ge=1, le=10),
):
    """Search travel articles."""
    results = await search_articles(query, max_results)
    return {"query": query, "results": results}


@general.post("/saved-searches", response_model=SavedSearchOut)
def save_search(req: SavedSearchCreate, db: Session = Depends(get_db)):
    """Save a search form submission."""
    search = SavedSearch(
        session_id=req.session_id,
        departure_city=req.departure_city,
        destination_city=req.destination_city,
        month=req.month,
        days=req.days,
        trip_type=req.trip_type,
        adults=req.adults,
        children=req.children,
        car_type=req.car_type,
        budget=req.budget,
        theme=req.theme,
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return SavedSearchOut.model_validate(search)


app.include_router(general)
