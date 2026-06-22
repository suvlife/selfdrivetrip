"""Image search service - Unsplash API with Lorem Picsum fallback."""

import logging
from typing import List, Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def search_unsplash(query: str, per_page: int = 9) -> Optional[List[Dict[str, Any]]]:
    """Search images via Unsplash API."""
    api_key = settings.UNSPLASH_ACCESS_KEY
    if not api_key:
        return None

    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": query, "per_page": min(per_page, 30), "orientation": "landscape"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            urls = item.get("urls", {})
            results.append({
                "id": item.get("id", ""),
                "url": urls.get("regular", ""),
                "thumb": urls.get("thumb", ""),
                "small": urls.get("small", ""),
                "alt": item.get("alt_description", query),
                "source": "unsplash",
                "attribution": {
                    "name": item.get("user", {}).get("name", ""),
                    "username": item.get("user", {}).get("username", ""),
                    "link": f"https://unsplash.com/@{item.get('user', {}).get('username', '')}",
                },
            })

        return results

    except Exception as e:
        logger.error(f"Unsplash API error for '{query}': {e}")
        return None


async def search_images(query: str, per_page: int = 9) -> List[Dict[str, Any]]:
    """Search images. Tries Unsplash first, falls back to Lorem Picsum."""
    # Try Unsplash
    result = await search_unsplash(query, per_page)
    if result:
        return result

    # Fallback to Lorem Picsum (generates random images, not query-based)
    logger.info(f"Using Lorem Picsum fallback for '{query}'")
    fallback = []
    for i in range(min(per_page, 9)):
        # Lorem Picsum with seed for consistency
        width, height = 800, 600
        fallback.append({
            "id": f"picsum_{i}",
            "url": f"https://picsum.photos/seed/{query.replace(' ', '_')}_{i}/{width}/{height}",
            "thumb": f"https://picsum.photos/seed/{query.replace(' ', '_')}_{i}/200/150",
            "small": f"https://picsum.photos/seed/{query.replace(' ', '_')}_{i}/400/300",
            "alt": query,
            "source": "picsum",
            "attribution": None,
        })

    return fallback
