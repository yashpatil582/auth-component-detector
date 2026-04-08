"""JavaScript-capable scraper using Playwright."""

from __future__ import annotations

import asyncio

_PLAYWRIGHT_AVAILABLE = True
try:
    from playwright.async_api import async_playwright
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False


def is_available() -> bool:
    return _PLAYWRIGHT_AVAILABLE


async def fetch_async(url: str, timeout: int = 15) -> str:
    """Fetch a page's HTML after JavaScript execution using Playwright."""
    if not _PLAYWRIGHT_AVAILABLE:
        raise RuntimeError(
            "Playwright is not installed. Install with: pip install playwright && playwright install chromium"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
            # Wait a bit for any late-rendering JS
            await page.wait_for_timeout(1000)
            html = await page.content()
        finally:
            await browser.close()
    return html


def fetch(url: str, timeout: int = 15) -> str:
    """Synchronous wrapper for fetch_async."""
    return asyncio.run(fetch_async(url, timeout))
