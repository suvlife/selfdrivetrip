"""Routes router - CRUD for routes, share, list."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.route import Route, SavedSearch
from app.schemas.route import (
    RouteOut,
    RouteListItem,
    SavedSearchCreate,
    SavedSearchOut,
    PaginatedResponse,
)
from app.utils import generate_share_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("", response_model=PaginatedResponse)
def list_routes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all published shared routes (paginated)."""
    query = db.query(Route).filter(Route.status == "published")
    total = query.count()
    routes = query.order_by(desc(Route.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for route in routes:
        items.append(RouteListItem.model_validate(route))

    return PaginatedResponse(
        items=[item.model_dump() for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/recent", response_model=List[SavedSearchOut])
def get_recent_searches(
    session_id: str = Query("", description="Session ID for anonymous user"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get recent saved searches / forms."""
    query = db.query(SavedSearch)
    if session_id:
        query = query.filter(SavedSearch.session_id == session_id)
    searches = query.order_by(desc(SavedSearch.created_at)).limit(limit).all()
    return [SavedSearchOut.model_validate(s) for s in searches]


@router.get("/{share_id}", response_model=RouteOut)
def get_route(share_id: str, db: Session = Depends(get_db)):
    """Get a specific route by its share_id (full detail with all relations)."""
    route = db.query(Route).filter(Route.share_id == share_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Increment view count
    route.view_count = (route.view_count or 0) + 1
    db.commit()

    return RouteOut.model_validate(route)


@router.post("/{share_id}/publish", response_model=RouteOut)
def publish_route(share_id: str, db: Session = Depends(get_db)):
    """Publish a draft route."""
    route = db.query(Route).filter(Route.share_id == share_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route.status = "published"
    db.commit()
    db.refresh(route)
    return RouteOut.model_validate(route)
