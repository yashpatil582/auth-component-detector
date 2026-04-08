"""POST /api/scrape — on-demand URL scraping endpoint."""

from fastapi import APIRouter, HTTPException
from requests.exceptions import RequestException, Timeout

from models.schemas import ScrapeRequest, ScrapeResponse
from services.scraper import scrape_url
from services import js_scraper

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    """Scrape a URL and detect authentication components."""
    url = str(request.url)

    if request.use_js_rendering and not js_scraper.is_available():
        raise HTTPException(
            status_code=422,
            detail="JavaScript rendering requested but Playwright is not installed.",
        )

    try:
        result = await scrape_url(
            url=url,
            use_js_rendering=request.use_js_rendering,
            timeout=request.timeout,
        )
        return result

    except Timeout:
        raise HTTPException(
            status_code=408,
            detail=f"Request timed out after {request.timeout}s for {url}",
        )
    except RequestException as e:
        # Clean up verbose error messages for the user
        msg = str(e)
        if "NameResolutionError" in msg or "Failed to resolve" in msg:
            msg = "Domain could not be resolved. Check the URL and try again."
        elif "SSLError" in msg or "CERTIFICATE_VERIFY_FAILED" in msg:
            msg = "SSL certificate error. The site may have an invalid certificate."
        elif "ConnectionError" in msg:
            msg = "Could not connect to the server. The site may be down."
        elif "Max retries" in msg:
            msg = "Could not reach the site after multiple attempts."
        raise HTTPException(
            status_code=422,
            detail=f"Could not reach {url}: {msg}",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        msg = str(e)
        if "Playwright" in msg or "BrowserType" in msg or "chromium" in msg.lower():
            msg = "JavaScript rendering is not available on this server. Try disabling the JS rendering option, or run the app locally with Playwright installed."
        raise HTTPException(
            status_code=422,
            detail=msg,
        )
