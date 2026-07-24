# Requirements Document

## Introduction

Page Pulse is a full-stack web application that audits any given URL and returns a structured report covering HTTP status, response time, and key SEO signals (title, meta description, H1 count, images missing alt text, and word count). The backend is built with Python and FastAPI; the frontend is a React (Vite) single-page application styled with Tailwind CSS. Error conditions — invalid URLs, timeouts, DNS failures, and non-HTML content — are handled distinctly and surfaced clearly in the UI.

---

## Glossary

- **System**: The Page Pulse application as a whole (backend + frontend).
- **Backend**: The FastAPI Python service that processes audit requests.
- **Frontend**: The React/Vite single-page application served to the user.
- **Validator**: The `validator.py` module responsible for URL validation.
- **Fetcher**: The `fetcher.py` module responsible for asynchronous HTTP fetching via httpx.
- **Parser**: The `parser.py` module responsible for HTML parsing via BeautifulSoup4.
- **Route_Handler**: The `routes.py` module that wires Validator, Fetcher, and Parser together and returns the API response.
- **AuditRequest**: The JSON request body `{ "url": "..." }` sent to `POST /api/audit`.
- **AuditResponse**: The unified JSON response shape always returned by the API.
- **Target_URL**: The URL submitted by the user for auditing.

---

## Requirements

### Requirement 1: API Endpoint Contract

**User Story:** As a frontend developer, I want a single well-defined POST endpoint, so that I can reliably send audit requests and parse responses.

#### Acceptance Criteria

1. THE Backend SHALL expose a `POST /api/audit` endpoint that accepts an `AuditRequest` JSON body.
2. THE Backend SHALL always return a response whose JSON shape matches `AuditResponse` (all nine fields present), regardless of success or error.
3. THE Backend SHALL enable CORS so that the Frontend can call the API from a different origin.

---

### Requirement 2: URL Validation

**User Story:** As a user, I want immediate feedback when my URL is malformed, so that I know to correct it before waiting for a network fetch.

#### Acceptance Criteria

1. WHEN a submitted URL has no scheme or a non-HTTP/HTTPS scheme, THE Validator SHALL reject the request and THE Backend SHALL return a `400` response with a descriptive `error` field.
2. WHEN a submitted URL has an empty or missing hostname, THE Validator SHALL reject the request and THE Backend SHALL return a `400` response with a descriptive `error` field.
3. WHEN an empty string is submitted as the URL, THE Validator SHALL reject the request and THE Backend SHALL return a `400` response with `error` set to a non-empty message.
4. WHEN a URL passes all validation checks, THE Validator SHALL return a success result and THE Route_Handler SHALL pass the URL to the Fetcher.

---

### Requirement 3: HTTP Fetching

**User Story:** As a user, I want the tool to fetch the page on my behalf and report real performance data, so that I see an accurate picture of that page's availability and speed.

#### Acceptance Criteria

1. WHEN a valid URL is fetched, THE Fetcher SHALL use a realistic `User-Agent` header and follow redirects.
2. WHEN a valid URL is fetched successfully, THE Fetcher SHALL return the HTTP status code of the Target_URL response.
3. WHEN a valid URL is fetched successfully, THE Fetcher SHALL return the elapsed response time in milliseconds as a non-negative number.
4. WHEN the Target_URL does not respond within 10 seconds, THE Fetcher SHALL raise a timeout exception and THE Route_Handler SHALL return a `504` response with `error` set to `"Request timed out after 10 seconds"`.
5. WHEN a DNS resolution or TCP connection failure occurs, THE Fetcher SHALL raise a connection error and THE Route_Handler SHALL return a `502` response with a descriptive `error` field.
6. WHEN the Target_URL response `Content-Type` is not HTML, THE Route_Handler SHALL return a `200` response with `error` set to `"Non-HTML content — cannot audit"` and all metric fields set to `null`.

---

### Requirement 4: HTML Parsing

**User Story:** As a user, I want SEO and quality signals extracted from the page, so that I can identify issues at a glance.

#### Acceptance Criteria

1. WHEN valid HTML is parsed, THE Parser SHALL return the text content of the first `<title>` tag, or `null` if no `<title>` tag is present.
2. WHEN valid HTML is parsed, THE Parser SHALL return the `content` attribute of the first `<meta name="description">` tag, or `null` if absent.
3. WHEN valid HTML is parsed, THE Parser SHALL return a non-negative integer count of all `<h1>` tags in the document.
4. WHEN valid HTML is parsed, THE Parser SHALL return a non-negative integer count of all `<img>` tags that have a missing or empty `alt` attribute.
5. WHEN valid HTML is parsed, THE Parser SHALL return a non-negative integer approximate word count of the visible text content after stripping all `<script>` and `<style>` tag contents.
6. THE Parser SHALL never raise an unhandled exception when given any string as input.

---

### Requirement 5: Error Response Contract

**User Story:** As a frontend developer, I want all error states to follow the same response shape, so that I can handle them uniformly without special-casing the JSON structure.

#### Acceptance Criteria

1. WHEN any error occurs (invalid URL, timeout, connection failure, non-HTML, or unexpected error), THE Backend SHALL return an `AuditResponse` with the `error` field populated and all metric fields (`status_code`, `response_time_ms`, `title`, `meta_description`, `h1_count`, `images_missing_alt`, `word_count`) set to `null`.
2. WHEN a request succeeds and HTML is parsed, THE Backend SHALL return an `AuditResponse` with `error` set to `null` and all metric fields populated with non-null values.
3. THE Backend SHALL never expose Python stack traces or unhandled exceptions in any API response body.
4. IF an unexpected internal error occurs, THEN THE Backend SHALL return a `500` response with `error` set to `"An unexpected error occurred"` and all metric fields set to `null`.

---

### Requirement 6: Frontend Input and Submission

**User Story:** As a user, I want a clean input form that validates my URL before sending it, so that I don't waste time waiting for a request I know will fail.

#### Acceptance Criteria

1. THE Frontend SHALL display a URL text input field and an "Audit" button on the main page.
2. WHEN the URL input is empty or contains only whitespace, THE Frontend SHALL prevent form submission and not call the API.
3. WHILE a request is in progress, THE Frontend SHALL display a loading indicator and disable the Audit button.

---

### Requirement 7: Audit Report Display

**User Story:** As a user, I want a structured, human-readable report, so that I can quickly understand the health and SEO quality of the audited page.

#### Acceptance Criteria

1. WHEN the API returns a successful `AuditResponse`, THE Frontend SHALL render all seven metric fields: status code, response time, title, meta description, H1 count, images missing alt, and word count.
2. WHEN displaying the HTTP status code, THE Frontend SHALL apply a green visual indicator for 2xx codes, yellow for 3xx codes, and red for 4xx or 5xx codes.
3. WHEN the API returns an `AuditResponse` with a non-null `error` field, THE Frontend SHALL display the error message in a distinctly styled error block.
4. THE Frontend SHALL never display raw JSON to the user.

---

### Requirement 8: Footer Attribution

**User Story:** As a project stakeholder, I want the footer to include a specific attribution link, so that the training task requirement is visibly satisfied.

#### Acceptance Criteria

1. THE Frontend SHALL display a footer containing the exact text `"Built for Digital Heroes Training Task"`.
2. THE Footer text SHALL be hyperlinked to `https://digitalheroesco.com`.

---

### Requirement 9: Project Structure and Deployment

**User Story:** As a developer, I want a clean monorepo structure with deployment configuration, so that I can set up and deploy the project easily.

#### Acceptance Criteria

1. THE System SHALL be organized as a monorepo with `/backend` and `/frontend` top-level directories.
2. THE System SHALL include a `README.md` at the repository root with setup and run instructions for both backend and frontend.
3. THE Backend SHALL be deployable to Render or Railway using standard Python/uvicorn configuration.
4. THE Frontend SHALL be deployable to Vercel or Netlify using standard Vite build output.
