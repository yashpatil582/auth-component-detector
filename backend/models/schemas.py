from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class ScrapeRequest(BaseModel):
    url: HttpUrl
    use_js_rendering: bool = False
    timeout: int = Field(default=15, ge=5, le=30)


class AuthComponent(BaseModel):
    component_type: str = Field(
        description="Type: login_form, password_field, username_field, oauth_button, forgot_password_link"
    )
    html_snippet: str = Field(description="Raw HTML of the detected component")
    selector: str = Field(description="CSS selector path to the element")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")
    attributes: dict[str, str] = Field(
        default_factory=dict, description="Key attributes (name, id, type, etc.)"
    )


class ScrapeResponse(BaseModel):
    url: str
    title: str | None = None
    scraped_at: datetime
    rendering_method: str = Field(description="'static' or 'javascript'")
    auth_components: list[AuthComponent] = Field(default_factory=list)
    full_page_has_auth: bool = False
    detection_summary: str = ""
    scrape_duration_ms: int = 0


class ScrapeError(BaseModel):
    error: str
    detail: str
    url: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    playwright_available: bool = False
