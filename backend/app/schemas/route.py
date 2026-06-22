"""Pydantic models for request/response serialization."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ─── POI ────────────────────────────────────────────────────────────────────


class POIBase(BaseModel):
    type: str = "waypoint"
    name: str = ""
    lat: float = 0.0
    lng: float = 0.0
    rating: float = 0.0
    price_level: str = ""
    image_url: str = ""
    description: str = ""
    source_url: str = ""
    booking_url: str = ""
    duration_minutes: int = 0
    sort_order: int = 0


class POICreate(POIBase):
    segment_id: Optional[str] = None


class POIOut(POIBase):
    id: str
    day_plan_id: str
    segment_id: Optional[str] = None

    class Config:
        from_attributes = True


# ─── RouteSegment ────────────────────────────────────────────────────────────


class RouteSegmentBase(BaseModel):
    from_name: str = ""
    to_name: str = ""
    distance: float = 0.0
    duration: float = 0.0
    toll_cost: float = 0.0
    fuel_cost: float = 0.0
    polyline: List[List[float]] = Field(default_factory=list)
    sort_order: int = 0


class RouteSegmentCreate(RouteSegmentBase):
    pass


class RouteSegmentOut(RouteSegmentBase):
    id: str
    day_plan_id: str
    pois: List[POIOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ─── Meal ────────────────────────────────────────────────────────────────────


class MealBase(BaseModel):
    type: str = "lunch"  # breakfast/lunch/dinner
    restaurant_name: str = ""
    cuisine_type: str = ""
    cost_per_person: float = 0.0
    image_url: str = ""
    rating: float = 0.0
    recommendation: str = ""


class MealCreate(MealBase):
    pass


class MealOut(MealBase):
    id: str
    day_plan_id: str

    class Config:
        from_attributes = True


# ─── Hotel ───────────────────────────────────────────────────────────────────


class HotelBase(BaseModel):
    name: str = ""
    lat: float = 0.0
    lng: float = 0.0
    price_per_night: float = 0.0
    rating: float = 0.0
    image_url: str = ""
    booking_url: str = ""
    address: str = ""
    phone: str = ""


class HotelCreate(HotelBase):
    pass


class HotelOut(HotelBase):
    id: str
    day_plan_id: str

    class Config:
        from_attributes = True


# ─── DayPlan ─────────────────────────────────────────────────────────────────


class DayPlanBase(BaseModel):
    day_number: int = 1
    date: str = ""
    theme: str = ""
    day_distance: float = 0.0
    day_duration: float = 0.0
    day_cost: float = 0.0


class DayPlanCreate(DayPlanBase):
    segments: List[RouteSegmentCreate] = Field(default_factory=list)
    pois: List[POICreate] = Field(default_factory=list)
    meals: List[MealCreate] = Field(default_factory=list)
    hotels: List[HotelCreate] = Field(default_factory=list)


class DayPlanOut(DayPlanBase):
    id: str
    route_id: str
    segments: List[RouteSegmentOut] = Field(default_factory=list)
    pois: List[POIOut] = Field(default_factory=list)
    meals: List[MealOut] = Field(default_factory=list)
    hotels: List[HotelOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ─── WeatherForecast ────────────────────────────────────────────────────────


class WeatherForecastOut(BaseModel):
    id: str
    route_id: str
    city_name: str
    date: str
    temperature_high: float
    temperature_low: float
    weather_condition: str
    icon: str
    humidity: float
    wind_speed: float

    class Config:
        from_attributes = True


# ─── Route ───────────────────────────────────────────────────────────────────


class RouteBase(BaseModel):
    title: str = ""
    departure: str = ""
    destination: str = ""
    total_distance: float = 0.0
    total_duration: float = 0.0
    trip_type: str = "自驾游"
    theme: str = ""
    car_type: str = "中型轿车"
    adults: int = 2
    children: int = 0
    budget: float = 0.0
    status: str = "draft"


class RouteCreate(RouteBase):
    day_plans: List[DayPlanCreate] = Field(default_factory=list)


class RouteListItem(BaseModel):
    id: str
    share_id: str
    title: str
    departure: str
    destination: str
    total_distance: float
    total_duration: float
    trip_type: str
    theme: str
    car_type: str
    adults: int
    children: int
    budget: float
    status: str
    created_at: datetime
    view_count: int

    class Config:
        from_attributes = True


class RouteOut(RouteBase):
    id: str
    share_id: str
    created_at: datetime
    view_count: int
    day_plans: List[DayPlanOut] = Field(default_factory=list)
    weather_forecasts: List[WeatherForecastOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ─── Generation ──────────────────────────────────────────────────────────────


class GenerateRequest(BaseModel):
    departure_city: str
    destination_city: str
    month: str = "7月"
    days: int = 3
    trip_type: str = "自驾游"
    adults: int = 2
    children: int = 0
    car_type: str = "中型轿车"
    budget: float = 5000.0
    theme: str = ""
    session_id: str = ""


class GenerateResponse(BaseModel):
    success: bool
    message: str = ""
    routes: List[RouteOut] = Field(default_factory=list)
    route_ids: List[str] = Field(default_factory=list)


# ─── SavedSearch ─────────────────────────────────────────────────────────────


class SavedSearchCreate(BaseModel):
    session_id: str = ""
    departure_city: str
    destination_city: str
    month: str = ""
    days: int = 3
    trip_type: str = "自驾游"
    adults: int = 2
    children: int = 0
    car_type: str = "中型轿车"
    budget: float = 0.0
    theme: str = ""


class SavedSearchOut(BaseModel):
    id: str
    session_id: str
    departure_city: str
    destination_city: str
    month: str
    days: int
    trip_type: str
    adults: int
    children: int
    car_type: str
    budget: float
    theme: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Generic ─────────────────────────────────────────────────────────────────


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "SelfDriveTrip"
    version: str = "1.0.0"
