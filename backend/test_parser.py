"""
test_parser.py — pytest suite for backend/parser.py

Covers the happy path plus edge/failure cases for HTML parsing:
title/meta extraction, h1 counting, missing-alt image detection,
word counting with script/style stripping, and graceful handling
of malformed or empty input.
"""

import pytest

from parser import ParseResult, parse_html


class TestParseHtmlHappyPath:
    """Full, well-formed HTML with every field populated."""

    def test_full_html_all_fields(self):
        html = (
            "<html><head>"
            "<title>  Hello World  </title>"
            '<meta name="description" content="A test page">'
            "</head><body>"
            "<h1>First</h1><h1>Second</h1>"
            '<img src="a.png">'
            '<img src="b.png" alt="">'
            '<img src="c.png" alt="ok">'
            "<script>var x = 'hidden words';</script>"
            "<style>body { color: red; }</style>"
            "<p>visible words here</p>"
            "</body></html>"
        )

        result = parse_html(html)

        assert result.title == "Hello World"
        assert result.meta_description == "A test page"
        assert result.h1_count == 2
        assert result.images_missing_alt == 2
        # get_text() runs over the full document, so <title> text is
        # included alongside body text: "Hello World" + "First Second"
        # + "visible words here" = 7 words
        assert result.word_count == 7

    def test_case_insensitive_meta_name(self):
        result = parse_html('<meta name="Description" content="caps test">')
        assert result.meta_description == "caps test"

    def test_all_images_have_alt(self):
        html = (
            '<html><body><img src="x.png" alt="logo">'
            '<img src="y.png" alt="photo"></body></html>'
        )
        result = parse_html(html)
        assert result.images_missing_alt == 0

    def test_script_and_style_excluded_from_word_count(self):
        html = (
            "<html><body>"
            "<script>var a = 'lots of script words';</script>"
            "<style>.x { color: blue; font-size: 12px; }</style>"
            "<p>one two</p>"
            "</body></html>"
        )
        result = parse_html(html)
        assert result.word_count == 2


class TestParseHtmlMissingFields:
    """Individual fields absent — should degrade to None/0, never raise."""

    def test_missing_title_returns_none(self):
        result = parse_html("<html><body><p>hi</p></body></html>")
        assert result.title is None

    def test_missing_meta_description_returns_none(self):
        result = parse_html("<html><head></head><body></body></html>")
        assert result.meta_description is None

    def test_no_h1_tags_returns_zero(self):
        result = parse_html("<html><body><h2>Only h2</h2></body></html>")
        assert result.h1_count == 0


class TestParseHtmlFailureCases:
    """Malformed, empty, or unexpected input — must never raise."""

    def test_empty_string_returns_default_result(self):
        result = parse_html("")
        assert result == ParseResult(None, None, 0, 0, 0)

    def test_none_like_garbage_input_does_not_raise(self):
        # Not valid HTML at all — parser must degrade gracefully, not crash
        result = parse_html("<<<not>>valid&&html!!!")
        assert isinstance(result, ParseResult)
        assert result.h1_count >= 0
        assert result.images_missing_alt >= 0
        assert result.word_count >= 0

    def test_unclosed_tags_do_not_raise(self):
        html = "<html><head><title>Unclosed<body><h1>Oops<p>text"
        result = parse_html(html)
        assert isinstance(result, ParseResult)


class TestParseHtmlEdgeCases:
    """Boundary conditions worth locking down explicitly."""

    def test_multiple_meta_tags_only_description_matched(self):
        html = (
            '<meta name="viewport" content="width=device-width">'
            '<meta name="description" content="the real one">'
            '<meta name="author" content="someone">'
        )
        result = parse_html(html)
        assert result.meta_description == "the real one"

    def test_title_with_nested_whitespace_is_stripped(self):
        html = "<title>\n   Spaced Out Title   \n</title>"
        result = parse_html(html)
        assert result.title == "Spaced Out Title"

    def test_empty_alt_and_missing_alt_both_count(self):
        html = (
            '<img src="a.png">'
            '<img src="b.png" alt="">'
            '<img src="c.png" alt="  ">'  # whitespace-only alt is still present, not missing
        )
        result = parse_html(html)
        # a.png (missing) + b.png (empty) = 2 missing;
        # c.png has non-empty alt attribute content and should not count
        assert result.images_missing_alt == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
