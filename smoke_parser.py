"""Smoke test for backend/parser.py"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "parser_mod", r"d:\DigitalHeroes\backend\parser.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["parser_mod"] = mod  # register before exec so dataclass __module__ resolves
spec.loader.exec_module(mod)

parse_html = mod.parse_html
ParseResult = mod.ParseResult

# 1. Full HTML — all fields present
html = (
    "<html><head>"
    "<title>  Hello World  </title>"
    '<meta name="description" content="A test page">'
    "</head><body>"
    "<h1>First</h1><h1>Second</h1>"
    '<img src="a.png">'           # missing alt → count
    '<img src="b.png" alt="">'    # empty alt → count
    '<img src="c.png" alt="ok">'  # valid alt → skip
    "<script>var x = 'hidden words';</script>"
    "<style>body { color: red; }</style>"
    "<p>visible words here</p>"
    "</body></html>"
)

r = parse_html(html)
assert r.title == "Hello World", f"title: {r.title!r}"
assert r.meta_description == "A test page", f"meta: {r.meta_description!r}"
assert r.h1_count == 2, f"h1_count: {r.h1_count}"
assert r.images_missing_alt == 2, f"images_missing_alt: {r.images_missing_alt}"
# visible text after stripping: "First Second visible words here" = 5 words
assert r.word_count == 5, f"word_count: {r.word_count}"
print("Test 1 passed: full HTML")

# 2. Missing <title> → None
r2 = parse_html("<html><body><p>hi</p></body></html>")
assert r2.title is None, f"title should be None, got {r2.title!r}"
print("Test 2 passed: missing title")

# 3. Missing meta description → None
r3 = parse_html("<html><head></head><body></body></html>")
assert r3.meta_description is None, f"meta should be None, got {r3.meta_description!r}"
print("Test 3 passed: missing meta")

# 4. Empty string → no exception, all zeros/None
r4 = parse_html("")
assert r4 == ParseResult(None, None, 0, 0, 0), f"empty: {r4}"
print("Test 4 passed: empty input")

# 5. Case-insensitive meta name match
r5 = parse_html('<meta name="Description" content="caps test">')
assert r5.meta_description == "caps test", f"meta case: {r5.meta_description!r}"
print("Test 5 passed: case-insensitive meta")

# 6. No <h1> tags → 0
r6 = parse_html("<html><body><h2>Only h2</h2></body></html>")
assert r6.h1_count == 0, f"h1_count: {r6.h1_count}"
print("Test 6 passed: no h1 tags")

# 7. All images have non-empty alt → 0 missing
r7 = parse_html('<html><body><img src="x.png" alt="logo"><img src="y.png" alt="photo"></body></html>')
assert r7.images_missing_alt == 0, f"images_missing_alt: {r7.images_missing_alt}"
print("Test 7 passed: all images have alt")

# 8. Script/style content not counted in word_count
html8 = "<html><body><script>var a = 'lots of script words';</script><p>one two</p></body></html>"
r8 = parse_html(html8)
assert r8.word_count == 2, f"word_count should be 2, got {r8.word_count}"
print("Test 8 passed: script content excluded from word count")

print("\nAll smoke tests passed!")
