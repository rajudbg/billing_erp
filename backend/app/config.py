from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "ERP Billing API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Security
    secret_key: str
    access_token_expires_minutes: int = 60 * 8
    algorithm: str = "HS256"

    # Database
    database_url: str

    # Files
    invoice_pdf_dir: str = "generated_invoices"

    # CORS
    backend_cors_origins: list[str] = []

    # Email (for invoice sending, reminders)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_use_tls: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # allow SECRET_KEY from env to match secret_key


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]

