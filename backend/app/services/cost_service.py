"""Cost calculation engine for self-driving trips."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Constants
HIGHWAY_TOLL_RATE = 0.5  # yuan per km for highways
FUEL_CONSUMPTION_RATES = {
    "小型轿车": 0.06,   # L/km
    "中型轿车": 0.08,
    "大型轿车": 0.10,
    "SUV": 0.10,
    "越野车": 0.12,
    "MPV": 0.10,
    "小型电动车": 0.0,  # electricity, not fuel
    "中型电动车": 0.0,
    "大型电动车": 0.0,
    "混动车": 0.05,
}
FUEL_PRICE = 8.0  # yuan per liter (92# gasoline)
ELECTRICITY_RATE = 0.15  # yuan per km (approx charging cost)
HIGHWAY_RATIO = 0.7  # Assume 70% of distance is on highways


def calculate_toll_cost(distance_km: float) -> float:
    """Calculate highway toll cost."""
    highway_km = distance_km * HIGHWAY_RATIO
    return round(highway_km * HIGHWAY_TOLL_RATE, 2)


def calculate_fuel_cost(distance_km: float, car_type: str = "中型轿车") -> float:
    """Calculate fuel/electricity cost based on distance and car type."""
    rate = FUEL_CONSUMPTION_RATES.get(car_type, 0.08)

    if "电动" in car_type:
        # Electric vehicle - use electricity rate
        return round(distance_km * ELECTRICITY_RATE, 2)
    elif "混动" in car_type:
        # Hybrid - partial fuel, partial electric
        fuel_part = distance_km * 0.6 * rate * FUEL_PRICE
        electric_part = distance_km * 0.4 * ELECTRICITY_RATE
        return round(fuel_part + electric_part, 2)
    else:
        # Fuel vehicle
        return round(distance_km * rate * FUEL_PRICE, 2)


def calculate_segment_cost(distance_km: float, car_type: str = "中型轿车") -> Dict[str, float]:
    """Calculate costs for a single segment."""
    toll = calculate_toll_cost(distance_km)
    fuel = calculate_fuel_cost(distance_km, car_type)
    total = toll + fuel
    return {
        "toll_cost": toll,
        "fuel_cost": fuel,
        "total_cost": round(total, 2),
    }


def calculate_day_cost(
    distance_km: float,
    car_type: str,
    hotel_price: float = 0.0,
    food_cost: float = 0.0,
    attraction_fees: float = 0.0,
    adults: int = 2,
    children: int = 0,
) -> Dict[str, float]:
    """Calculate total cost for a day."""
    transport = calculate_segment_cost(distance_km, car_type)
    food_total = food_cost * (adults + children * 0.5)
    total = transport["total_cost"] + hotel_price + food_total + attraction_fees
    return {
        "transport_cost": transport["total_cost"],
        "toll_cost": transport["toll_cost"],
        "fuel_cost": transport["fuel_cost"],
        "hotel_cost": hotel_price,
        "food_cost": round(food_total, 2),
        "attraction_cost": attraction_fees,
        "total_cost": round(total, 2),
    }


def calculate_trip_cost(
    total_distance_km: float,
    days: int,
    car_type: str = "中型轿车",
    hotel_per_night: float = 300.0,
    food_per_person_per_day: float = 150.0,
    adults: int = 2,
    children: int = 0,
    attraction_fees_per_day: float = 100.0,
) -> Dict[str, Any]:
    """Calculate total trip cost estimate."""
    transport = calculate_segment_cost(total_distance_km, car_type)
    hotel_total = hotel_per_night * (days - 1)  # First day no hotel needed (departure)
    food_total = food_per_person_per_day * days * (adults + children * 0.5)
    attraction_total = attraction_fees_per_day * days

    total = transport["total_cost"] + hotel_total + food_total + attraction_total

    return {
        "total_transport": transport["total_cost"],
        "toll_total": transport["toll_cost"],
        "fuel_total": transport["fuel_cost"],
        "hotel_total": round(hotel_total, 2),
        "food_total": round(food_total, 2),
        "attraction_total": round(attraction_total, 2),
        "hotel_per_night": hotel_per_night,
        "food_per_person_per_day": food_per_person_per_day,
        "grand_total": round(total, 2),
        "breakdown": {
            "transport_pct": round(transport["total_cost"] / total * 100, 1) if total > 0 else 0,
            "hotel_pct": round(hotel_total / total * 100, 1) if total > 0 else 0,
            "food_pct": round(food_total / total * 100, 1) if total > 0 else 0,
            "attraction_pct": round(attraction_total / total * 100, 1) if total > 0 else 0,
        },
    }
