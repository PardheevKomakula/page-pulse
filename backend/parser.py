from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class ParseResult:
    title: str | None
    meta_description: str | None
    h1_count: int
    images_missing_alt: int
    word_count: int


def parse_html(body: str) -> ParseResult:
    """
    Parses an HTML body string and returns SEO/quality signals.

    - Extracts <title> text (stripped), None if absent.
    - Extracts <meta name="description"> content attribute, None if absent.
    - Counts all <h1> elements (any depth).
    - Counts <img> elements where alt is missing or an empty string.
    - Strips <script> and <style> elements before computing word count.
    - Returns ParseResult(None, None, 0, 0, 0) on any exception.
    """
    try:
        soup = BeautifulSoup(body, "html.parser")

        # --- title ---
        title_tag = soup.find("title")
        title: str | None = title_tag.get_text().strip() if title_tag else None

        # --- meta description (case-insensitive name match) ---
        meta_description: str | None = None
        for tag in soup.find_all("meta"):
            name_attr = tag.get("name", "")
            if isinstance(name_attr, str) and name_attr.lower() == "description":
                content = tag.get("content")
                if content is not None:
                    meta_description = str(content)
                break

        # --- h1 count ---
        h1_count: int = len(soup.find_all("h1"))

        # --- images missing alt ---
        images_missing_alt: int = 0
        for img in soup.find_all("img"):
            alt = img.get("alt")
            # alt is missing (None) or is an empty string
            if alt is None or alt == "":
                images_missing_alt += 1

        # --- word count (strip script/style first) ---
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()

        visible_text = soup.get_text(separator=" ")
        word_count: int = len([token for token in visible_text.split() if token])

    except Exception:
        return ParseResult(None, None, 0, 0, 0)

    return ParseResult(
        title=title,
        meta_description=meta_description,
        h1_count=h1_count,
        images_missing_alt=images_missing_alt,
        word_count=word_count,
    )
