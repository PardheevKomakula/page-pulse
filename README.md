# Page Pulse — URL Audit Tool

Page Pulse is a full-stack web application that audits any public URL and returns a structured report of key SEO and quality signals: HTTP status, response time, page title, meta description, H1 count, images missing alt text, and word count.

**Tech stack:** Python + FastAPI (backend) · React + Vite + Tailwind CSS (frontend) · httpx · BeautifulSoup4

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
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins. Set to your frontend URL in production (e.g. `https://page-pulse.vercel.app`). |
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
4. Add the environment variable `CORS_ORIGINS` set to your deployed frontend URL (e.g. `https://page-pulse.vercel.app`).
5. Python version is pinned in `backend/runtime.txt` (`python-3.11.9`).

### Frontend — Vercel or Netlify

**Vercel:**
1. Import the repo and set the **root directory** to `frontend`.
2. Vercel auto-detects Vite; the `vercel.json` config handles the SPA rewrite rule.
3. Add the environment variable `VITE_API_BASE_URL` set to your deployed backend URL.

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
