# Page Pulse — URL Audit Tool

Page Pulse is a full-stack web application that audits any public URL and returns a structured report of key SEO and quality signals: HTTP status, response time, page title, meta description, H1 count, images missing alt text, and word count.

**Tech stack:** Python + FastAPI (backend) · React + Vite + Tailwind CSS (frontend) · httpx · BeautifulSoup4

**Live app:** `<https://page-pulse-eta-six.vercel.app/>`
**Backend API:** `<https://page-pulse-dalo.onrender.com/>`

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.11 |
| Node.js | 18 |
| npm | 9 |

---

## Local Development

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server (hot-reload)
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
Health check: `GET http://localhost:8000/`
Audit endpoint: `POST http://localhost:8000/api/audit`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment config and set the backend URL
cp .env.example .env.local
# Edit .env.local if your backend is not on localhost:8000

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173` (or the next available port).

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins. Set to your frontend URL in production (e.g. `https://page-pulse-eta-six.vercel.app`). |
| `PORT` | `8000` | Port for uvicorn (used automatically by Render/Railway). |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL of the backend API. Set to your deployed backend URL before building for production. |

---

## Running Tests

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test -- --run
```

---

## Production Build

```bash
cd frontend
npm run build
# Output is in frontend/dist/
```

---

## Deployment

### Backend — Render or Railway

1. Connect your GitHub repo to [Render](https://render.com) or [Railway](https://railway.app).
2. Set the **root directory** to `backend`.
3. Set the **start command** to `uvicorn main:app --host 0.0.0.0 --port $PORT` (the `Procfile` handles this automatically on Render).
4. Add the environment variable `CORS_ORIGINS` set to your deployed frontend URL — no trailing slash (e.g. `https://page-pulse-eta-six.vercel.app`).
5. Python version is pinned in `backend/runtime.txt` (`python-3.11.9`).

### Frontend — Vercel or Netlify

**Vercel:**
1. Import the repo and set the **root directory** to `frontend`.
2. Vercel auto-detects Vite; the `vercel.json` config handles the SPA rewrite rule.
3. Add the environment variable `VITE_API_BASE_URL` set to your deployed backend URL — no trailing slash.
4. Redeploy after any environment variable change — Vite bakes env vars in at build time.

**Netlify:**
1. Import the repo, set **base directory** to `frontend`, **build command** to `npm run build`, **publish directory** to `dist`.
2. Add the environment variable `VITE_API_BASE_URL` in Site Settings → Environment Variables.
3. Add a `_redirects` file to `frontend/public/` with `/* /index.html 200` for SPA routing.

---

## Project Structure

```
/
├── backend/
│   ├── main.py          # FastAPI app, CORS setup
│   ├── routes.py        # POST /api/audit handler
│   ├── validator.py     # URL validation
│   ├── fetcher.py       # httpx async fetcher
│   ├── parser.py        # BeautifulSoup4 HTML parser
│   ├── models.py        # Pydantic request/response models
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── components/
│   │       ├── AuditForm.tsx
│   │       ├── AuditReport.tsx
│   │       ├── ErrorBlock.tsx
│   │       └── Footer.tsx
│   ├── vercel.json
│   └── .env.example
└── README.md
```

---

## API Reference

### `POST /api/audit`

**Request body:**
```json
{ "url": "https://example.com" }
```

**Response** (always the same shape):
```json
{
  "url": "https://example.com",
  "status_code": 200,
  "response_time_ms": 342,
  "title": "Example Domain",
  "meta_description": null,
  "h1_count": 1,
  "images_missing_alt": 0,
  "word_count": 21,
  "error": null
}
```

| HTTP status | Meaning |
|-------------|---------|
| `200` | Successful audit (or non-HTML content — check `error` field) |
| `400` | Invalid or malformed URL |
| `502` | DNS failure or connection refused |
| `504` | Request timed out (> 10 seconds) |
| `500` | Unexpected server error |

---

## Design Decisions

**1. Plain HTTP fetch over headless browser rendering**
Page Pulse fetches raw server-rendered HTML rather than running a full headless browser (e.g. Playwright/Puppeteer). This keeps the tool fast, lightweight, and deployable on a free tier with no extra system dependencies or cold-start overhead. The tradeoff is real: JavaScript-heavy sites that render their content client-side (e.g. amazon.in) return incomplete or empty audits, since the tool never executes their JS. This surfaced directly during testing — Amazon returned a 200 status but zero words and no title. Rather than hide this, the app flags it with a soft warning when a 200 response comes back with suspiciously empty content, so the limitation is visible instead of silently wrong. A v2 would add an optional "render mode" using a headless browser for sites that need it.

**2. Distinct error codes instead of one generic failure**
Rather than collapsing every failure into a single "something went wrong" message, the API distinguishes invalid URLs (400), unreachable hosts / DNS failures (502), and timeouts (504) from unexpected server errors (500). This makes the API genuinely debuggable for a frontend consumer — the UI can react differently to "you typed a bad URL" versus "the target site is down" instead of showing the same unhelpful message for both.

**3. A single, consistent response shape for success and failure**
Every response — success or failure — returns the exact same JSON structure. Either every metric field is populated and `error` is `null`, or every metric field is `null` and `error` holds a message. This means the frontend never needs separate success/failure response types or branching parse logic; it just checks one field.

---

## AI Usage

I used Claude for parts of the backend — mainly to help scaffold the initial project structure and get unstuck on concepts I hadn't worked with before, like handling async HTTP timeouts properly with `httpx` and structuring FastAPI error responses consistently. I also used it to debug a CORS/deployment issue I ran into while connecting the deployed frontend (Vercel) to the deployed backend (Render), which turned out to be a trailing-slash mismatch in the environment variables. I reviewed and adjusted the generated code — including the parsing logic, error handling flow, and the JS-rendering warning I added after noticing incomplete results on sites like Amazon — rather than using it as-is.
