import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.config import get_settings
from app.api.v1.router import api_router
from app.core.logging import configure_logging
from app.db.session import SessionLocal, engine
from app.db.seed_data import seed
from app.models import Base, User


configure_logging()
logger = logging.getLogger("erp.billing")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Serve generated invoice PDFs
pdf_dir = Path(settings.invoice_pdf_dir)
pdf_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/generated_invoices",
    StaticFiles(directory=str(pdf_dir)),
    name="generated_invoices",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_v1_prefix)


def _create_tables() -> None:
    """Create all tables if they do not exist (e.g. first run or fresh DB)."""
    Base.metadata.create_all(bind=engine)


def _ensure_seed() -> None:
    """Create seed data (admin user, company, etc.) if the database is empty."""
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            seed(db)
            logger.info("Seed data created (admin@example.com / admin123)")
    finally:
        db.close()


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("ERP Billing API starting up")
    await asyncio.to_thread(_create_tables)
    await asyncio.to_thread(_ensure_seed)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTP error %s on %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

