"""POI search service using AMap (高德地图) Web API."""

import logging
from typing import List, Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def search_poi(
    city: str,
    keyword: str,
    types: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[Dict[str, Any]]:
    """Search Points of Interest via AMap API.

    Args:
        city: City name (e.g., "北京")
        keyword: Search keyword (e.g., "故宫", "餐厅")
        types: POI type filter (e.g., "060000" for scenic spots, "050000" for food)
        page: Page number (1-based)
        page_size: Results per page (max 25)

    Returns:
        List of POI dicts
    """
    api_key = settings.AMAP_KEY
    if not api_key:
        logger.warning("AMAP_KEY not configured")
        return []

    try:
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "key": api_key,
            "keywords": keyword,
            "city": city,
            "offset": min(page_size, 25),
            "page": page,
            "extensions": "all",
            "output": "JSON",
        }
        if types:
            params["types"] = types

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "1":
            logger.error(f"AMap API error: {data.get('info', 'unknown error')}")
            return []

        pois = []
        for item in data.get("pois", []):
            location = item.get("location", "").split(",")
            lng = float(location[0]) if len(location) > 0 else 0.0
            lat = float(location[1]) if len(location) > 1 else 0.0

            # Parse business area / tyep mapping
            poi_type = _map_amap_type(item.get("type", ""))

            photos = item.get("photos", [])
            image_url = photos[0].get("url", "") if photos else ""

            pois.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "lat": lat,
                "lng": lng,
                "type": poi_type,
                "address": item.get("address", ""),
                "pname": item.get("pname", ""),
                "cityname": item.get("cityname", ""),
                "adname": item.get("adname", ""),
                "rating": float(item.get("biz_ext", {}).get("rating", "0") or "0"),
                "cost": float(item.get("biz_ext", {}).get("cost", "0") or "0"),
                "image_url": image_url,
                "tel": item.get("tel", ""),
                "website": item.get("website", ""),
                "distance": item.get("distance", ""),
                "business_area": item.get("business_area", ""),
            })

        return pois

    except Exception as e:
        logger.error(f"AMap API error for '{keyword}' in '{city}': {e}")
        return []


async def search_poi_around(
    city: str,
    keyword: str,
    lat: float,
    lng: float,
    radius: int = 1000,
) -> List[Dict[str, Any]]:
    """Search POIs around a specific location using AMap around API."""
    api_key = settings.AMAP_KEY
    if not api_key:
        return []

    try:
        url = "https://restapi.amap.com/v3/place/around"
        params = {
            "key": api_key,
            "keywords": keyword,
            "location": f"{lng},{lat}",
            "radius": radius,
            "offset": 20,
            "extensions": "all",
            "output": "JSON",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "1":
            return []

        pois = []
        for item in data.get("pois", []):
            location = item.get("location", "").split(",")
            lng = float(location[0]) if len(location) > 0 else 0.0
            lat = float(location[1]) if len(location) > 1 else 0.0

            photos = item.get("photos", [])
            image_url = photos[0].get("url", "") if photos else ""

            pois.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "lat": lat,
                "lng": lng,
                "type": _map_amap_type(item.get("type", "")),
                "address": item.get("address", ""),
                "rating": float(item.get("biz_ext", {}).get("rating", "0") or "0"),
                "cost": float(item.get("biz_ext", {}).get("cost", "0") or "0"),
                "image_url": image_url,
                "distance": item.get("distance", ""),
            })

        return pois

    except Exception as e:
        logger.error(f"AMap around API error: {e}")
        return []


def _map_amap_type(amap_type: str) -> str:
    """Map AMap POI type to our simplified type."""
    amap_type_lower = amap_type.lower()

    scenic_keywords = ["风景名胜", "景点", "公园", "旅游", "景区", "博物馆", "纪念馆", "动物园", "植物园"]
    restaurant_keywords = ["餐饮", "餐厅", "美食", "中餐", "西餐", "快餐", "咖啡", "茶馆"]
    hotel_keywords = ["住宿", "酒店", "宾馆", "旅馆", "民宿", "度假村"]
    gas_keywords = ["加油站", "加气站"]
    charging_keywords = ["充电站", "充电"]

    if any(k in amap_type for k in scenic_keywords):
        return "scenic"
    elif any(k in amap_type for k in restaurant_keywords):
        return "restaurant"
    elif any(k in amap_type for k in hotel_keywords):
        return "hotel"
    elif any(k in amap_type for k in gas_keywords):
        return "gas_station"
    elif any(k in amap_type for k in charging_keywords):
        return "charging"
    else:
        return "waypoint"
