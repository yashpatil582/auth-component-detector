"""Scraper orchestrator — picks the right strategy and runs detection."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from models.schemas import ScrapeResponse
from services import static_scraper, js_scraper
from services.auth_detector import detect_auth_components, generate_summary


async def scrape_url(
    url: str,
    use_js_rendering: bool = False,
    timeout: int = 15,
) -> ScrapeResponse:
    """Scrape a URL and detect authentication components."""
    start = time.perf_counter()

    if use_js_rendering:
        html = await js_scraper.fetch_async(url, timeout)
        method = "javascript"
    else:
        html = static_scraper.fetch(url, timeout)
        method = "static"

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Extract page title
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Run auth detection
    components = detect_auth_components(html)
    summary = generate_summary(components)

    return ScrapeResponse(
        url=str(url),
        title=title,
        scraped_at=datetime.now(timezone.utc),
        rendering_method=method,
        auth_components=components,
        full_page_has_auth=len(components) > 0,
        detection_summary=summary,
        scrape_duration_ms=elapsed_ms,
    )
