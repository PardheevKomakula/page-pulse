"""
fetcher.py — Async HTTP fetcher for Page Pulse.

Fetches a target URL using httpx, captures status code, response time,
content type, and body. Re-raises typed httpx exceptions for the route
handler to map to appropriate HTTP error codes.
"""

import time
from dataclasses import dataclass

import httpx

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_TIMEOUT = httpx.Timeout(10.0)
_MAX_REDIRECTS = 10


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    status_code: int
    response_time_ms: float
    content_type: str
    body: str | None
    error: str | None


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


async def fetch_url(url: str) -> FetchResult:
    """
    Fetch *url* asynchronously with a realistic browser User-Agent.

    Returns a :class:`FetchResult` populated with all fields on success.

    Raises:
        httpx.TimeoutException: When the request exceeds the 10-second timeout.
            Caller should map this to HTTP 504.
        httpx.ConnectError: When the host cannot be reached (DNS failure,
            connection refused, etc.).  Caller should map this to HTTP 502.
    """
    headers = {"User-Agent": _USER_AGENT}

    async with httpx.AsyncClient(
        timeout=_TIMEOUT,
        follow_redirects=True,
        max_redirects=_MAX_REDIRECTS,
    ) as client:
        start = time.monotonic()
        # httpx.TimeoutException and httpx.ConnectError are intentionally
        # allowed to propagate so the route handler can map them correctly.
        response = await client.get(url, headers=headers)
        elapsed_ms = (time.monotonic() - start) * 1000.0

    # Strip parameters from content-type, e.g.
    # "text/html; charset=utf-8" → "text/html"
    raw_content_type = response.headers.get("content-type", "")
    content_type = raw_content_type.split(";")[0].strip()

    return FetchResult(
        status_code=response.status_code,
        response_time_ms=elapsed_ms,
        content_type=content_type,
        body=response.text,
        error=None,
    )
