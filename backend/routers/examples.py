"""GET /api/examples — pre-scraped demo site results."""

import json
from pathlib import Path

from fastapi import APIRouter

from models.schemas import ScrapeResponse

router = APIRouter()

DATA_FILE = Path(__file__).parent.parent / "data" / "examples.json"


@router.get("/examples", response_model=list[ScrapeResponse])
async def get_examples():
    """Return pre-scraped authentication component results for 5 demo sites."""
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE) as f:
        data = json.load(f)

    return [ScrapeResponse(**item) for item in data]
