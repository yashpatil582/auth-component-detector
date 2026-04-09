"""GET /api/examples — live-scraped demo site results."""

import asyncio
import logging

from fastapi import APIRouter

from models.schemas import ScrapeResponse
from services.scraper import scrape_url

logger = logging.getLogger(__name__)

router = APIRouter()

DEMO_SITES = [
    {"url": "https://github.com/login", "js": False},
    {"url": "https://parabank.parasoft.com/parabank/index.htm", "js": False},
    {"url": "https://www.saucedemo.com/", "js": False},
    {"url": "https://demo.testfire.net/login.jsp", "js": False},
    {"url": "https://practicetestautomation.com/practice-test-login/", "js": False},
]


async def _scrape_site(site: dict) -> ScrapeResponse | None:
    """Scrape a single demo site, return None on failure."""
    try:
        return await scrape_url(
            url=site["url"],
            use_js_rendering=site["js"],
            timeout=15,
        )
    except Exception as e:
        logger.warning(f"Failed to scrape {site['url']}: {e}")
        return None


@router.get("/examples", response_model=list[ScrapeResponse])
async def get_examples():
    """Scrape 5 demo websites live and return authentication component results."""
    tasks = [_scrape_site(site) for site in DEMO_SITES]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
