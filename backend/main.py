import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------
# Set CORS_ORIGINS to a comma-separated list of allowed origins in production.
# Defaults to "*" (allow all) for local development.
_cors_origins_env = os.getenv("CORS_ORIGINS", "*")
cors_origins: list[str] = (
    [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
    if _cors_origins_env != "*"
    else ["*"]
)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Page Pulse",
    description="URL audit tool — SEO and quality metrics for any public page.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the audit router (defines POST /api/audit)
app.include_router(router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
async def health_check() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}
