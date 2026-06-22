"""Article aggregation service - DuckDuckGo search + BeautifulSoup scraping + AI fallback."""

import logging
from typing import List, Optional, Dict, Any

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


async def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search articles via DuckDuckGo HTML search (no API key needed)."""
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": f"{query} 自驾游 攻略"}

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(url, data=params, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        results = []

        for result in soup.select(".result")[:max_results]:
            title_el = result.select_one(".result__title a")
            snippet_el = result.select_one(".result__snippet")

            if title_el:
                title = title_el.get_text(strip=True)
                link = title_el.get("href", "")

                # DuckDuckGo wraps links in redirect
                if "uddg=" in link:
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(link)
                    qs = parse_qs(parsed.query)
                    link = qs.get("uddg", [""])[0]

                snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "source": "duckduckgo",
                })

        return results

    except Exception as e:
        logger.error(f"DuckDuckGo search error for '{query}': {e}")
        return []


async def fetch_article_content(url: str) -> Optional[str]:
    """Fetch and extract text content from an article URL."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove unwanted elements
        for tag in soup.select("script, style, nav, header, footer, aside, .ad, .sidebar"):
            tag.decompose()

        # Try to get article content
        article = soup.find("article")
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            # Fallback to body text
            body = soup.find("body")
            text = body.get_text(separator="\n", strip=True) if body else ""

        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines[:200])  # First 200 lines max

        return text[:5000] if text else None

    except Exception as e:
        logger.error(f"Error fetching article content from {url}: {e}")
        return None


async def search_articles(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search for travel articles related to the query."""
    results = await search_duckduckgo(query, max_results)

    # Attempt to fetch content for top results
    for article in results[:3]:
        content = await fetch_article_content(article.get("url", ""))
        if content:
            article["content"] = content[:2000]  # Truncate to ~2000 chars

    return results
