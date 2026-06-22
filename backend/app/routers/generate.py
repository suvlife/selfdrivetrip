"""Generate router - Main AI route generation endpoint."""

import json
import logging
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.route import Route, DayPlan, RouteSegment, POI, Meal, Hotel, SavedSearch
from app.schemas.route import (
    GenerateRequest,
    GenerateResponse,
    RouteOut,
)
from app.services.ai_service import generate_routes
from app.utils import generate_share_id, generate_uuid, parse_float, parse_int

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])


def _save_route_to_db(db: Session, route_data: dict) -> Route:
    """Save a generated route dict into the database. Returns the Route model."""
    share_id = generate_share_id()

    route = Route(
        id=generate_uuid(),
        share_id=share_id,
        title=route_data.get("title", "自驾游路线"),
        departure=route_data.get("departure", ""),
        destination=route_data.get("destination", ""),
        total_distance=parse_float(route_data.get("total_distance"), 0.0),
        total_duration=parse_float(route_data.get("total_duration"), 0.0),
        trip_type=route_data.get("trip_type", "自驾游"),
        theme=route_data.get("theme", ""),
        car_type=route_data.get("car_type", "中型轿车"),
        adults=parse_int(route_data.get("adults"), 2),
        children=parse_int(route_data.get("children"), 0),
        budget=parse_float(route_data.get("budget"), 0.0),
        status="draft",
        created_at=datetime.utcnow(),
        view_count=0,
    )
    db.add(route)
    db.flush()  # Get route.id

    day_plans_data = route_data.get("day_plans", [])
    for dp_idx, dp_data in enumerate(day_plans_data):
        day_plan = DayPlan(
            id=generate_uuid(),
            route_id=route.id,
            day_number=parse_int(dp_data.get("day_number"), dp_idx + 1),
            date=dp_data.get("date", f"第{dp_idx+1}天"),
            theme=dp_data.get("theme", ""),
            day_distance=parse_float(dp_data.get("day_distance"), 0.0),
            day_duration=parse_float(dp_data.get("day_duration"), 0.0),
            day_cost=parse_float(dp_data.get("day_cost"), 0.0),
        )
        db.add(day_plan)
        db.flush()

        # Segments
        segments_data = dp_data.get("segments", [])
        for seg_idx, seg_data in enumerate(segments_data):
            segment = RouteSegment(
                id=generate_uuid(),
                day_plan_id=day_plan.id,
                from_name=seg_data.get("from_name", ""),
                to_name=seg_data.get("to_name", ""),
                distance=parse_float(seg_data.get("distance"), 0.0),
                duration=parse_float(seg_data.get("duration"), 0.0),
                toll_cost=parse_float(seg_data.get("toll_cost"), 0.0),
                fuel_cost=parse_float(seg_data.get("fuel_cost"), 0.0),
                polyline=seg_data.get("polyline", []),
                sort_order=parse_int(seg_data.get("sort_order"), seg_idx),
            )
            db.add(segment)
            db.flush()

            # POIs attached to segment
            seg_pois = seg_data.get("pois", [])
            for poi_idx, poi_data in enumerate(seg_pois):
                poi = POI(
                    id=generate_uuid(),
                    day_plan_id=day_plan.id,
                    segment_id=segment.id,
                    type=poi_data.get("type", "waypoint"),
                    name=poi_data.get("name", ""),
                    lat=parse_float(poi_data.get("lat"), 0.0),
                    lng=parse_float(poi_data.get("lng"), 0.0),
                    rating=parse_float(poi_data.get("rating"), 0.0),
                    price_level=poi_data.get("price_level", ""),
                    image_url=poi_data.get("image_url", ""),
                    description=poi_data.get("description", ""),
                    source_url=poi_data.get("source_url", ""),
                    booking_url=poi_data.get("booking_url", ""),
                    duration_minutes=parse_int(poi_data.get("duration_minutes"), 0),
                    sort_order=parse_int(poi_data.get("sort_order"), poi_idx),
                )
                db.add(poi)

        # Day-level POIs
        day_pois = dp_data.get("pois", [])
        for poi_idx, poi_data in enumerate(day_pois):
            poi = POI(
                id=generate_uuid(),
                day_plan_id=day_plan.id,
                segment_id=None,
                type=poi_data.get("type", "waypoint"),
                name=poi_data.get("name", ""),
                lat=parse_float(poi_data.get("lat"), 0.0),
                lng=parse_float(poi_data.get("lng"), 0.0),
                rating=parse_float(poi_data.get("rating"), 0.0),
                price_level=poi_data.get("price_level", ""),
                image_url=poi_data.get("image_url", ""),
                description=poi_data.get("description", ""),
                source_url=poi_data.get("source_url", ""),
                booking_url=poi_data.get("booking_url", ""),
                duration_minutes=parse_int(poi_data.get("duration_minutes"), 0),
                sort_order=parse_int(poi_data.get("sort_order"), poi_idx),
            )
            db.add(poi)

        # Meals
        meals_data = dp_data.get("meals", [])
        for meal_data in meals_data:
            meal = Meal(
                id=generate_uuid(),
                day_plan_id=day_plan.id,
                type=meal_data.get("type", "lunch"),
                restaurant_name=meal_data.get("restaurant_name", ""),
                cuisine_type=meal_data.get("cuisine_type", ""),
                cost_per_person=parse_float(meal_data.get("cost_per_person"), 0.0),
                image_url=meal_data.get("image_url", ""),
                rating=parse_float(meal_data.get("rating"), 0.0),
                recommendation=meal_data.get("recommendation", ""),
            )
            db.add(meal)

        # Hotels
        hotels_data = dp_data.get("hotels", [])
        for hotel_data in hotels_data:
            hotel = Hotel(
                id=generate_uuid(),
                day_plan_id=day_plan.id,
                name=hotel_data.get("name", ""),
                lat=parse_float(hotel_data.get("lat"), 0.0),
                lng=parse_float(hotel_data.get("lng"), 0.0),
                price_per_night=parse_float(hotel_data.get("price_per_night"), 0.0),
                rating=parse_float(hotel_data.get("rating"), 0.0),
                image_url=hotel_data.get("image_url", ""),
                booking_url=hotel_data.get("booking_url", ""),
                address=hotel_data.get("address", ""),
                phone=hotel_data.get("phone", ""),
            )
            db.add(hotel)

    db.commit()
    db.refresh(route)
    return route


@router.post("/generate", response_model=GenerateResponse)
async def generate_route_plan(req: GenerateRequest, db: Session = Depends(get_db)):
    """Main AI route generation endpoint.

    Takes user's trip requirements, generates 3-5 route plans via LLM,
    saves them to database, and returns the results.
    """
    try:
        logger.info(
            f"Generating routes: {req.departure_city} -> {req.destination_city}, "
            f"{req.days} days, {req.budget} budget"
        )

        # Generate routes via AI
        routes_data = await generate_routes(
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

        if not routes_data:
            raise HTTPException(
                status_code=500,
                detail="Route generation failed. AI service returned no routes.",
            )

        # Save to database
        saved_routes = []
        route_ids = []

        for route_data in routes_data:
            route = _save_route_to_db(db, route_data)
            saved_routes.append(RouteOut.model_validate(route))
            route_ids.append(route.id)

        return GenerateResponse(
            success=True,
            message=f"成功生成 {len(saved_routes)} 条路线方案",
            routes=saved_routes,
            route_ids=route_ids,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Route generation failed")
        raise HTTPException(status_code=500, detail=f"Route generation failed: {str(e)}")
