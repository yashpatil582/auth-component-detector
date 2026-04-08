"""Static HTML scraper using requests + BeautifulSoup."""

import requests
from config import USER_AGENT


def fetch(url: str, timeout: int = 15) -> str:
    """Fetch a page's HTML using a simple HTTP GET request.

    Works for server-rendered pages. Will not execute JavaScript.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.exceptions.SSLError:
        # Retry without SSL verification as fallback
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
    response.raise_for_status()
    return response.text
