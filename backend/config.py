import os


CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,https://yashpatil582.github.io"
).split(",")
DEFAULT_TIMEOUT = 15
MAX_TIMEOUT = 30
RATE_LIMIT = "10/minute"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
