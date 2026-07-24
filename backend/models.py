"""Pydantic v2 request and response models for the Page Pulse audit API."""

from pydantic import BaseModel


class AuditRequest(BaseModel):
    """Represents an incoming audit request containing the URL to be audited."""

    url: str


class AuditResponse(BaseModel):
    """Represents the structured audit result returned to the client.

    All fields except ``url`` default to ``None`` so that partial responses
    (e.g. on fetch errors or invalid URLs) can be constructed without needing
    every metric to be populated.
    """

    url: str
    status_code: int | None = None
    response_time_ms: float | None = None
    title: str | None = None
    meta_description: str | None = None
    h1_count: int | None = None
    images_missing_alt: int | None = None
    word_count: int | None = None
    error: str | None = None
    warning: str | None = None
