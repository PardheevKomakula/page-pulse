from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, str | None]:
    """
    Validates that the given URL is well-formed and uses http/https.

    Returns:
        (True, None) if the URL is valid.
        (False, error_message) if the URL is invalid.

    Never raises an exception for any string input.
    """
    try:
        # Reject empty or whitespace-only strings
        if not url or not url.strip():
            return (False, "URL must not be empty")

        parsed = urlparse(url)

        # Scheme must be present and must be http or https
        if parsed.scheme not in ("http", "https"):
            return (False, "Invalid URL: missing scheme")

        # Hostname must be non-empty
        if not parsed.hostname:
            return (False, "Invalid URL: missing hostname")

        return (True, None)
    except Exception:
        # Catch any unexpected parsing errors to guarantee no exceptions escape
        return (False, "Invalid URL: missing scheme")
