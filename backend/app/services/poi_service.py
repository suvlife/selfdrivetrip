"""POI search service using Baidu Maps (百度地图) Web API."""

import logging
from typing import List, Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BAIDU_PLACE_SEARCH_URL = "https://api.map.baidu.com/place/v2/search"
BAIDU_PLACE_DETAIL_URL = "https://api.map.baidu.com/place/v2/detail"

# Mapping from Baidu tag keywords to our internal POI types
_TAG_TO_TYPE: list[tuple[list[str], str]] = [
    (["风景名胜", "景点", "公园", "旅游", "景区", "博物馆"], "scenic"),
    (["餐饮", "餐厅", "美食", "中餐", "西餐", "咖啡", "茶馆"], "restaurant"),
    (["住宿", "酒店", "宾馆", "旅馆", "民宿", "度假村"], "hotel"),
    (["加油站", "加气站"], "gas_station"),
    (["充电站", "充电"], "charging"),
]

# Reverse mapping: our internal type → Baidu search tag (for filtering)
_TYPE_TO_BAIDU_TAG: dict[str, str] = {
    "scenic": "景点",
    "restaurant": "美食",
    "hotel": "酒店",
    "gas_station": "加油站",
    "charging": "充电站",
}


def _map_baidu_tag(tag_string: str) -> str:
    """Map Baidu Maps 'tag' field to our simplified POI type.

    Baidu returns tags like '美食;中餐厅' or '景点;公园'.
    """
    if not tag_string:
        return "waypoint"
    for keywords, poi_type in _TAG_TO_TYPE:
        if any(k in tag_string for k in keywords):
            return poi_type
    return "waypoint"


async def _baidu_search(
    params: dict[str, Any],
) -> List[Dict[str, Any]]:
    """Low-level Baidu Maps API search helper.

    Handles API key injection, HTTP request, and response validation.
    Returns a list of parsed POI dicts, or empty list on failure.
    """
    ak = settings.BAIDU_MAP_AK
    if not ak:
        logger.warning("BAIDU_MAP_AK not configured")
        return []

    params.setdefault("ak", ak)
    params.setdefault("output", "json")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(BAIDU_PLACE_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != 0:
            logger.error(
                f"Baidu Maps API error: status={data.get('status')}, "
                f"message={data.get('message', 'unknown')}"
            )
            return []

        pois = []
        for item in data.get("results", []):
            location = item.get("location", {})
            lat = float(location.get("lat", 0))
            lng = float(location.get("lng", 0))

            detail_info = item.get("detail_info", {}) or {}
            tag = detail_info.get("tag", "") or ""
            poi_type = _map_baidu_tag(tag)

            pois.append({
                "uid": item.get("uid", ""),
                "name": item.get("name", ""),
                "lat": lat,
                "lng": lng,
                "type": poi_type,
                "address": item.get("address", ""),
                "province": item.get("province", ""),
                "city": item.get("city", ""),
                "area": item.get("area", ""),
                "rating": float(detail_info.get("overall_rating", 0) or 0),
                "price": float(detail_info.get("price", 0) or 0),
                "shop_hours": detail_info.get("shop_hours", "") or "",
                "tag": tag,
                "telephone": item.get("telephone", ""),
                "distance": str(item.get("detail_info", {}).get("distance", "")),
            })

        return pois

    except Exception as e:
        logger.error(f"Baidu Maps search error: {e}")
        return []


async def search_poi(
    city: str,
    keyword: str,
    types: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[Dict[str, Any]]:
    """Search Points of Interest via Baidu Maps Place API (text search).

    Args:
        city: City name (e.g., "北京")
        keyword: Search keyword (e.g., "故宫", "餐厅")
        types: Internal POI type filter ("scenic", "restaurant", "hotel", etc.)
        page: Page number (1-based, Baidu uses 0-based internally)
        page_size: Results per page (Baidu max: 20)

    Returns:
        List of POI dicts with unified schema
    """
    params: dict[str, Any] = {
        "query": keyword,
        "region": city,
        "page_num": max(0, page - 1),
        "page_size": min(page_size, 20),
    }

    # If an internal type filter is given, pass the corresponding Baidu tag
    if types and types in _TYPE_TO_BAIDU_TAG:
        params["tag"] = _TYPE_TO_BAIDU_TAG[types]

    return await _baidu_search(params)


async def search_poi_around(
    city: str,
    keyword: str,
    lat: float,
    lng: float,
    radius: int = 1000,
) -> List[Dict[str, Any]]:
    """Search POIs around a specific location using Baidu Maps Place API.

    The same /place/v2/search endpoint is used with 'location' and 'radius'
    parameters instead of 'region'.

    Args:
        city: City name (used for logging only; not passed to API in around mode)
        keyword: Search keyword
        lat: Latitude of center point
        lng: Longitude of center point
        radius: Search radius in meters (default: 1000)

    Returns:
        List of POI dicts with unified schema
    """
    params: dict[str, Any] = {
        "query": keyword,
        "location": f"{lat},{lng}",
        "radius": radius,
        "page_size": 20,
    }

    result = await _baidu_search(params)
    return result
