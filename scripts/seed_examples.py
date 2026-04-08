#!/usr/bin/env python3
"""Pre-scrape 5 demo websites and save results to backend/data/examples.json."""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.static_scraper import fetch as static_fetch
from services.js_scraper import fetch_async as js_fetch
from services.auth_detector import detect_auth_components, generate_summary
from models.schemas import ScrapeResponse
from bs4 import BeautifulSoup

DEMO_SITES = [
    {
        "url": "https://github.com/login",
        "name": "GitHub",
        "js": False,
    },
    {
        "url": "https://parabank.parasoft.com/parabank/index.htm",
        "name": "ParaBank (Banking Demo)",
        "js": False,
    },
    {
        "url": "https://www.saucedemo.com/",
        "name": "SauceDemo",
        "js": True,
    },
    {
        "url": "https://demo.testfire.net/login.jsp",
        "name": "Altoro Mutual (TestFire)",
        "js": False,
    },
    {
        "url": "https://practicetestautomation.com/practice-test-login/",
        "name": "Practice Test Automation",
        "js": False,
    },
]

OUTPUT_FILE = Path(__file__).parent.parent / "backend" / "data" / "examples.json"


async def scrape_site(site: dict) -> dict | None:
    url = site["url"]
    use_js = site.get("js", False)
    method = "javascript" if use_js else "static"
    print(f"  Scraping {site['name']} ({url}) [{method}]...")
    try:
        start = time.perf_counter()
        if use_js:
            html = await js_fetch(url, timeout=20)
        else:
            html = static_fetch(url, timeout=20)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else site["name"]

        components = detect_auth_components(html)
        summary = generate_summary(components)

        result = ScrapeResponse(
            url=url,
            title=title,
            scraped_at=datetime.now(timezone.utc),
            rendering_method=method,
            auth_components=components,
            full_page_has_auth=len(components) > 0,
            detection_summary=summary,
            scrape_duration_ms=elapsed_ms,
        )
        print(f"    Found {len(components)} component(s) in {elapsed_ms}ms")
        return result.model_dump(mode="json")

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


async def async_main():
    print("Seeding example data from 5 demo sites...\n")
    results = []

    for site in DEMO_SITES:
        result = await scrape_site(site)
        if result:
            results.append(result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved {len(results)} results to {OUTPUT_FILE}")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
