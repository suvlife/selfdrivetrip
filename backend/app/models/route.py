"""SQLAlchemy ORM models for SelfDriveTrip."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid():
    return str(uuid.uuid4())


class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    share_id = Column(String(16), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    departure = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    total_distance = Column(Float, default=0.0)
    total_duration = Column(Float, default=0.0)  # in hours
    trip_type = Column(String(50), default="自驾游")
    theme = Column(String(100), default="")
    car_type = Column(String(50), default="中型轿车")
    adults = Column(Integer, default=2)
    children = Column(Integer, default=0)
    budget = Column(Float, default=0.0)
    status = Column(String(20), default="draft")  # draft / published
    created_at = Column(DateTime, default=datetime.utcnow)
    view_count = Column(Integer, default=0)

    day_plans = relationship("DayPlan", back_populates="route", cascade="all, delete-orphan", order_by="DayPlan.day_number")
    weather_forecasts = relationship("WeatherForecast", back_populates="route", cascade="all, delete-orphan")


class DayPlan(Base):
    __tablename__ = "day_plans"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    route_id = Column(UUID(as_uuid=False), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(String(20), default="")  # e.g., "2026-07-01" or "Day 1"
    theme = Column(String(100), default="")
    day_distance = Column(Float, default=0.0)
    day_duration = Column(Float, default=0.0)
    day_cost = Column(Float, default=0.0)

    route = relationship("Route", back_populates="day_plans")
    segments = relationship("RouteSegment", back_populates="day_plan", cascade="all, delete-orphan", order_by="RouteSegment.sort_order")
    pois = relationship("POI", back_populates="day_plan", cascade="all, delete-orphan", order_by="POI.sort_order")
    meals = relationship("Meal", back_populates="day_plan", cascade="all, delete-orphan")
    hotels = relationship("Hotel", back_populates="day_plan", cascade="all, delete-orphan")


class RouteSegment(Base):
    __tablename__ = "route_segments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    day_plan_id = Column(UUID(as_uuid=False), ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False)
    from_name = Column(String(255), nullable=False)
    to_name = Column(String(255), nullable=False)
    distance = Column(Float, default=0.0)  # km
    duration = Column(Float, default=0.0)  # hours
    toll_cost = Column(Float, default=0.0)
    fuel_cost = Column(Float, default=0.0)
    polyline = Column(JSON, default=list)  # array of [lng, lat]
    sort_order = Column(Integer, default=0)

    day_plan = relationship("DayPlan", back_populates="segments")
    pois = relationship("POI", back_populates="segment", cascade="all, delete-orphan", order_by="POI.sort_order")


class POI(Base):
    __tablename__ = "pois"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    day_plan_id = Column(UUID(as_uuid=False), ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=False), ForeignKey("route_segments.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(30), nullable=False)  # scenic/restaurant/hotel/gas_station/charging/waypoint
    name = Column(String(255), nullable=False)
    lat = Column(Float, default=0.0)
    lng = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    price_level = Column(String(20), default="")
    image_url = Column(Text, default="")
    description = Column(Text, default="")
    source_url = Column(Text, default="")
    booking_url = Column(Text, default="")
    duration_minutes = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)

    day_plan = relationship("DayPlan", back_populates="pois")
    segment = relationship("RouteSegment", back_populates="pois")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    day_plan_id = Column(UUID(as_uuid=False), ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)  # breakfast/lunch/dinner
    restaurant_name = Column(String(255), nullable=False)
    cuisine_type = Column(String(100), default="")
    cost_per_person = Column(Float, default=0.0)
    image_url = Column(Text, default="")
    rating = Column(Float, default=0.0)
    recommendation = Column(Text, default="")

    day_plan = relationship("DayPlan", back_populates="meals")


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    day_plan_id = Column(UUID(as_uuid=False), ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    lat = Column(Float, default=0.0)
    lng = Column(Float, default=0.0)
    price_per_night = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    image_url = Column(Text, default="")
    booking_url = Column(Text, default="")
    address = Column(Text, default="")
    phone = Column(String(50), default="")

    day_plan = relationship("DayPlan", back_populates="hotels")


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    route_id = Column(UUID(as_uuid=False), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    city_name = Column(String(255), nullable=False)
    date = Column(String(20), nullable=False)
    temperature_high = Column(Float, default=0.0)
    temperature_low = Column(Float, default=0.0)
    weather_condition = Column(String(100), default="")
    icon = Column(String(50), default="")
    humidity = Column(Float, default=0.0)
    wind_speed = Column(Float, default=0.0)

    route = relationship("Route", back_populates="weather_forecasts")


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    session_id = Column(String(255), default="", index=True)
    departure_city = Column(String(255), nullable=False)
    destination_city = Column(String(255), nullable=False)
    month = Column(String(20), default="")
    days = Column(Integer, default=3)
    trip_type = Column(String(50), default="自驾游")
    adults = Column(Integer, default=2)
    children = Column(Integer, default=0)
    car_type = Column(String(50), default="中型轿车")
    budget = Column(Float, default=0.0)
    theme = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
