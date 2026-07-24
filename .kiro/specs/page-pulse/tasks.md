# Implementation Plan: Page Pulse — URL Audit Tool

## Overview

Build the Page Pulse monorepo from scratch: a FastAPI backend with modular URL validation, HTTP fetching, and HTML parsing, paired with a React/Vite frontend that presents the audit report. Tasks proceed from project scaffolding → backend modules → API route → frontend components → wiring → deployment config and README.

---

## Tasks

- [x] 1. Scaffold the monorepo structure
  - Create `/backend` and `/frontend` top-level directories
  - Add root-level `.gitignore` covering Python (`__pycache__`, `.venv`, `*.pyc`) and Node (`node_modules`, `dist`)
  - _Requirements: 9.1_

- [x] 2. Set up the backend project
  - [x] 2.1 Initialise Python environment and dependencies
    - Create `backend/requirements.txt` pinning: `fastapi`, `uvicorn[standard]`, `httpx`, `beautifulsoup4`, `pydantic`, `pytest`, `pytest-asyncio`, `hypothesis`
    - Create `backend/main.py` that instantiates the FastAPI app, registers the router from `routes.py`, and adds `CORSMiddleware` allowing all origins (configurable via env var)
    - _Requirements: 1.1, 1.3_
  - [ ]* 2.2 Write smoke test for app startup
    - Verify `POST /api/audit` route exists and returns a parseable JSON body
    - _Requirements: 1.1_

- [x] 3. Implement URL Validator (`backend/validator.py`)
  - [x] 3.1 Write `validate_url(url: str) -> tuple[bool, str | None]`
    - Return `(False, "URL must not be empty")` for empty/whitespace strings
    - Return `(False, "Invalid URL: missing scheme")` when scheme is absent or not `http`/`https`
    - Return `(False, "Invalid URL: missing hostname")` when hostname is empty
    - Return `(True, None)` for valid URLs
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ]* 3.2 Write property test for URL Validator
    - **Property 1: Valid URL acceptance implies structural correctness**
    - *For any* URL string accepted by `validate_url` as valid, it must contain a non-empty `http`/`https` scheme and a non-empty hostname
    - Use `hypothesis` strategies to generate URL-like strings; assert structural properties on accepted inputs
    - **Validates: Requirements 2.1, 2.2, 2.4**
  - [ ]* 3.3 Write unit tests for `validate_url`
    - Parametrize over: empty string, whitespace, `"not-a-url"`, `"ftp://example.com"`, `"http://"`, `"https://example.com"`, `"http://localhost:8000/path?q=1"`
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Implement HTTP Fetcher (`backend/fetcher.py`)
  - [x] 4.1 Define `FetchResult` dataclass and `fetch_url` async function
    - Fields: `status_code: int`, `response_time_ms: float`, `content_type: str`, `body: str | None`, `error: str | None`
    - Set `User-Agent` to a realistic browser string (e.g. Chrome 120 on Windows)
    - Follow redirects, enforce 10-second total timeout via `httpx.Timeout(10.0)`
    - Measure wall-clock time with `time.monotonic()` before and after the request
    - Catch `httpx.TimeoutException` → re-raise for caller to map to 504
    - Catch `httpx.ConnectError` → re-raise for caller to map to 502
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [ ]* 4.2 Write unit tests for `fetch_url` using mocked httpx transport
    - Test 200 OK with HTML content-type: verify `status_code`, `response_time_ms >= 0`, `content_type`, `body` populated
    - Test timeout: mock `httpx.TimeoutException`, verify exception propagates
    - Test DNS failure: mock `httpx.ConnectError`, verify exception propagates
    - Test non-HTML content-type: verify `content_type` returned correctly
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [ ]* 4.3 Write property test for response time non-negativity
    - **Property 4: Response time non-negativity**
    - *For any* successful fetch result, `response_time_ms` must be ≥ 0
    - Use hypothesis to generate mock response parameters; assert `response_time_ms >= 0`
    - **Validates: Requirements 3.3**

- [x] 5. Implement HTML Parser (`backend/parser.py`)
  - [x] 5.1 Define `ParseResult` dataclass and `parse_html` function
    - Fields: `title: str | None`, `meta_description: str | None`, `h1_count: int`, `images_missing_alt: int`, `word_count: int`
    - Extract `<title>` text; return `None` if tag absent
    - Extract `<meta name="description">` `content` attribute; return `None` if absent
    - Count `<h1>` tags
    - Count `<img>` tags where `alt` attribute is missing or empty string
    - Strip `<script>` and `<style>` tags+contents before computing word count; split on whitespace
    - Wrap entire function body in a broad `try/except` to satisfy Requirement 4.6
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - [ ]* 5.2 Write property test for Parser never raises
    - **Property 2: Parser never raises on arbitrary HTML**
    - *For any* string passed to `parse_html`, the function must return a `ParseResult` without raising, with `h1_count`, `images_missing_alt`, and `word_count` all ≥ 0
    - Use `hypothesis.strategies.text()` as input
    - **Validates: Requirements 4.3, 4.4, 4.5, 4.6**
  - [ ]* 5.3 Write property test for word count stability under script/style injection
    - **Property 5: Word count stability under script/style stripping**
    - *For any* HTML document, adding additional `<script>` or `<style>` blocks must not increase `word_count`
    - Generate base HTML, record `word_count`, inject script/style blocks, assert count does not increase
    - **Validates: Requirements 4.5**
  - [ ]* 5.4 Write unit tests for `parse_html` with static HTML fixtures
    - Cover: no `<title>` tag, no meta description, zero `<h1>`, multiple `<h1>`, `<img>` with and without `alt`, page with `<script>`/`<style>` blocks, empty string input
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 6. Implement Route Handler (`backend/routes.py`)
  - [x] 6.1 Define `AuditRequest` and `AuditResponse` Pydantic models
    - `AuditRequest`: `url: str`
    - `AuditResponse`: all nine fields with correct types and `Optional`/`None` defaults
    - _Requirements: 1.1, 1.2_
  - [x] 6.2 Implement `POST /api/audit` endpoint
    - Call `validate_url`; on failure return `JSONResponse(status_code=400, content=AuditResponse(url=url, error=msg, ...nulls).dict())`
    - Call `fetch_url`; catch `TimeoutException` → 504, `ConnectError` → 502
    - Check `content_type`; if not `text/html` → return 200 with `error="Non-HTML content — cannot audit"`
    - Call `parse_html`; assemble full `AuditResponse` with all metric fields
    - Wrap entire handler in `try/except Exception` fallback → return 500 with generic error message
    - _Requirements: 1.2, 2.1, 2.2, 3.4, 3.5, 3.6, 5.1, 5.2, 5.3, 5.4_
  - [ ]* 6.3 Write property test for Response shape mutual exclusivity
    - **Property 3: Response shape mutual exclusivity**
    - *For any* `AuditResponse`, either `error` is `None` and all metric fields are non-null, OR `error` is a non-empty string and all metric fields are `None`
    - Construct `AuditResponse` objects from both success and error paths; assert mutual exclusivity holds
    - **Validates: Requirements 5.1, 5.2**
  - [ ]* 6.4 Write integration tests for the full route using FastAPI TestClient
    - Happy path: mock `fetch_url` returning valid HTML → assert all metric fields non-null, `error` null, HTTP 200
    - Invalid URL: assert HTTP 400, `error` non-null, metrics null
    - Timeout: mock `TimeoutException` → assert HTTP 504
    - DNS failure: mock `ConnectError` → assert HTTP 502
    - Non-HTML: mock `content_type="application/pdf"` → assert HTTP 200, `error` non-null
    - Assert CORS header `Access-Control-Allow-Origin` present on all responses
    - Assert no response body contains a Python stack trace (`"Traceback"` string)
    - _Requirements: 1.2, 1.3, 5.1, 5.2, 5.3, 5.4_

- [x] 7. Checkpoint — Backend complete
  - Run `pytest backend/` and ensure all tests pass
  - Verify `uvicorn backend.main:app --reload` starts without errors and `POST /api/audit` returns valid JSON
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Scaffold the frontend project
  - [x] 8.1 Initialise Vite + React + TypeScript project inside `/frontend`
    - Run `npm create vite@latest frontend -- --template react-ts` (or equivalent)
    - Install Tailwind CSS and configure `tailwind.config.js` and `postcss.config.js`
    - Remove boilerplate files (`App.css`, default SVG assets)
    - _Requirements: 7.1_
  - [x] 8.2 Add TypeScript types
    - Create `frontend/src/types.ts` with `AuditRequest`, `AuditResponse`, and `AppState` interfaces as defined in the design
    - _Requirements: 1.2_
  - [x] 8.3 Add API client helper
    - Create `frontend/src/api.ts` with an `auditUrl(url: string): Promise<AuditResponse>` function that POSTs to the backend `/api/audit` and parses the JSON response
    - Throw a typed error on network failure
    - _Requirements: 1.1_

- [x] 9. Implement frontend components
  - [x] 9.1 Implement `AuditForm.tsx`
    - Controlled URL text input bound to local state
    - "Audit" button disabled when input is empty or only whitespace
    - Call `onSubmit(url)` prop on valid submission
    - _Requirements: 6.1, 6.2_
  - [x] 9.2 Implement `AuditReport.tsx`
    - Accept `AuditResponse` as props
    - Render all seven metric fields with labels
    - Apply Tailwind classes: `text-green-600` for 2xx, `text-yellow-500` for 3xx, `text-red-600` for 4xx/5xx status badge
    - _Requirements: 7.1, 7.2_
  - [x] 9.3 Implement `ErrorBlock.tsx`
    - Accept `message: string` prop
    - Render a styled block (red border, red background tint) displaying the message as plain text
    - Never render raw JSON
    - _Requirements: 7.3, 7.4_
  - [x] 9.4 Implement `Footer.tsx`
    - Render a `<footer>` containing an `<a>` tag with exact text `"Built for Digital Heroes Training Task"` and `href="https://digitalheroesco.com"`
    - _Requirements: 8.1, 8.2_
  - [ ]* 9.5 Write unit tests for frontend components (Vitest + React Testing Library)
    - `AuditForm`: submit blocked when input empty; `onSubmit` called with trimmed URL when valid
    - `AuditReport`: assert `text-green-600` class for status 200, `text-yellow-500` for 301, `text-red-600` for 404 and 500
    - `ErrorBlock`: renders message string; does not render raw JSON object notation
    - `Footer`: renders exact link text and correct href
    - _Requirements: 6.1, 6.2, 7.2, 7.3, 8.1, 8.2_

- [x] 10. Wire frontend components together in `App.tsx`
  - [x] 10.1 Implement `App.tsx` with `AppState` state machine
    - State transitions: `idle` → `loading` (on submit) → `success` | `error` (on API response)
    - Render `AuditForm` in all states (pre-filled URL retained)
    - Render loading spinner/text while `phase === "loading"`; disable form
    - Render `AuditReport` when `phase === "success"` and `data.error === null`
    - Render `ErrorBlock` when `phase === "error"` OR when `phase === "success"` and `data.error !== null`
    - Render `Footer` always
    - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4_
  - [ ]* 10.2 Write property test for status code colour mapping
    - **Property from design: status code colour classification**
    - *For any* integer status code, the colour classification function must return `"green"` for 200–299, `"yellow"` for 300–399, and `"red"` for 400–599
    - Extract the classification function from `AuditReport`; use `hypothesis.strategies.integers` to test all ranges
    - **Validates: Requirements 7.2**
  - [ ]* 10.3 Write property test for empty/whitespace input blocking
    - **Property: Whitespace-only URLs are always blocked**
    - *For any* string composed entirely of whitespace characters, the `AuditForm` submit handler must not be called
    - **Validates: Requirements 6.2**

- [x] 11. Checkpoint — Frontend complete
  - Run `npm run build` in `/frontend` and confirm no TypeScript or build errors
  - Run `npm test -- --run` (Vitest) and ensure all tests pass
  - Manually verify the form, report, and error block render correctly against a running backend
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Add deployment configuration
  - [x] 12.1 Backend deployment config
    - Add `backend/Procfile` with `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
    - Add `backend/runtime.txt` specifying Python version (e.g. `python-3.11.x`)
    - Ensure `CORS_ORIGINS` is read from an environment variable with a sensible default
    - _Requirements: 9.3_
  - [x] 12.2 Frontend deployment config
    - Add `frontend/vercel.json` (or confirm `vite.config.ts` outputs to `dist/`) so Vercel/Netlify picks up the build correctly
    - Add `frontend/.env.example` documenting `VITE_API_BASE_URL` environment variable
    - Update `api.ts` to read `import.meta.env.VITE_API_BASE_URL` as the base URL
    - _Requirements: 9.4_

- [x] 13. Write README.md
  - Create root `README.md` covering:
    - Project overview (1 paragraph)
    - Prerequisites (Python 3.11+, Node 18+)
    - Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
    - Frontend: `cd frontend && npm install && npm run dev`
    - Environment variables: `CORS_ORIGINS` (backend), `VITE_API_BASE_URL` (frontend)
    - Deployment notes for Render/Railway (backend) and Vercel/Netlify (frontend)
  - _Requirements: 9.2_

- [x] 14. Final checkpoint — full stack integration
  - Run all backend tests (`pytest backend/`)
  - Run all frontend tests (`npm test -- --run` in `/frontend`)
  - Confirm `POST /api/audit` returns correct shape for at least one real URL
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use `hypothesis` on the backend and Vitest + custom generators on the frontend
- Checkpoints at tasks 7, 11, and 14 ensure incremental validation before moving to the next layer
- The backend `CORS_ORIGINS` env var should be set to the deployed frontend URL in production

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1"] },
    { "wave": 2, "tasks": ["2"] },
    { "wave": 3, "tasks": ["3", "4", "5"] },
    { "wave": 4, "tasks": ["6"] },
    { "wave": 5, "tasks": ["7"] },
    { "wave": 6, "tasks": ["8"] },
    { "wave": 7, "tasks": ["9"] },
    { "wave": 8, "tasks": ["10"] },
    { "wave": 9, "tasks": ["11"] },
    { "wave": 10, "tasks": ["12", "13"] },
    { "wave": 11, "tasks": ["14"] }
  ]
}
```
