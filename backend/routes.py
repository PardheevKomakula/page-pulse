"""
routes.py — FastAPI route handler for the Page Pulse audit API.

Orchestrates the validator → fetcher → parser pipeline and maps all
outcomes (success, invalid URL, timeout, DNS failure, non-HTML content,
unexpected exceptions) to consistently-shaped AuditResponse JSON.
"""

import logging

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fetcher import fetch_url
from models import AuditRequest, AuditResponse
from parser import parse_html
from validator import validate_url

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/audit")
async def audit_url(request: AuditRequest) -> AuditResponse:
    """
    Orchestrates URL validation, fetching, and HTML parsing.

    Always returns a well-formed AuditResponse — never exposes raw
    exceptions or stack traces to the caller.

    HTTP status codes returned:
        200  — successful audit or non-HTML content
        400  — invalid/malformed URL
        500  — unexpected server error
        502  — DNS / connection failure (target unreachable)
        504  — target did not respond within 10 seconds
    """
    try:
        # ------------------------------------------------------------------
        # 1. Validate URL
        # ------------------------------------------------------------------
        is_valid, error_msg = validate_url(request.url)
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content=AuditResponse(
                    url=request.url,
                    error=error_msg,
                ).model_dump(),
            )

        # ------------------------------------------------------------------
        # 2. Fetch URL  — map typed httpx exceptions to gateway errors
        # ------------------------------------------------------------------
        try:
            fetch_result = await fetch_url(request.url)
        except httpx.TimeoutException:
            return JSONResponse(
                status_code=504,
                content=AuditResponse(
                    url=request.url,
                    error="Request timed out after 10 seconds",
                ).model_dump(),
            )
        except httpx.ConnectError:
            return JSONResponse(
                status_code=502,
                content=AuditResponse(
                    url=request.url,
                    error="Could not connect to the server",
                ).model_dump(),
            )

        # ------------------------------------------------------------------
        # 3. Guard: only parse HTML content
        # ------------------------------------------------------------------
        if "text/html" not in fetch_result.content_type:
            return JSONResponse(
                status_code=200,
                content=AuditResponse(
                    url=request.url,
                    status_code=fetch_result.status_code,
                    response_time_ms=fetch_result.response_time_ms,
                    error="Non-HTML content — cannot audit",
                ).model_dump(),
            )

        # ------------------------------------------------------------------
        # 4. Parse HTML and assemble the full response
        # ------------------------------------------------------------------
        parse_result = parse_html(fetch_result.body or "")

        # Detect likely JS-rendered pages: successful fetch but no visible
        # content — warn the user rather than silently returning empty fields.
        warning: str | None = None
        if (
            fetch_result.status_code == 200
            and parse_result.word_count == 0
            and parse_result.title is None
        ):
            warning = (
                "This page may rely heavily on JavaScript — the audit only sees "
                "server-rendered HTML, so results may be incomplete."
            )

        return AuditResponse(
            url=request.url,
            status_code=fetch_result.status_code,
            response_time_ms=fetch_result.response_time_ms,
            title=parse_result.title,
            meta_description=parse_result.meta_description,
            h1_count=parse_result.h1_count,
            images_missing_alt=parse_result.images_missing_alt,
            word_count=parse_result.word_count,
            error=None,
            warning=warning,
        )

    # ----------------------------------------------------------------------
    # 5. Catch-all — log server-side, return generic 500 (no traceback leak)
    # ----------------------------------------------------------------------
    except Exception:
        logger.exception("Unexpected error while auditing %s", request.url)
        return JSONResponse(
            status_code=500,
            content=AuditResponse(
                url=request.url,
                error="An unexpected error occurred",
            ).model_dump(),
        )
