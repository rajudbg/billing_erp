from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal
from app.models.invoice import Invoice


settings = get_settings()
logger = logging.getLogger("erp.billing.email")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def _build_invoice_email(invoice: Invoice) -> EmailMessage:
    company = invoice.company
    client = invoice.client

    to_email = client.billing_email or (client.contacts[0].email if client.contacts else None)
    if not to_email:
        raise ValueError("Client has no billing email configured")

    template = env.get_template("invoice_email.html")
    body_html = template.render(invoice=invoice, company=company, client=client)

    msg = EmailMessage()
    msg["Subject"] = f"Invoice {invoice.invoice_number} from {company.name}"
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    msg.set_content("Please see the attached invoice.")
    msg.add_alternative(body_html, subtype="html")

    if invoice.pdf_path and Path(invoice.pdf_path).exists():
        with open(invoice.pdf_path, "rb") as f:
            pdf_data = f.read()
        msg.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(invoice.pdf_path),
        )

    return msg


def send_email_message(msg: EmailMessage) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("SMTP configuration is not set")

    if settings.smtp_use_tls:
        logger.info("Sending email via SMTP with TLS | to=%s", msg["To"])
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    else:
        logger.info("Sending email via SMTP | to=%s", msg["To"])
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)


def send_invoice_email(invoice_id: int, db: Session) -> None:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    msg = _build_invoice_email(invoice)
    try:
        send_email_message(msg)
        logger.info("Invoice email sent | invoice_id=%s | to=%s", invoice_id, msg["To"])
    except Exception:
        logger.exception("Failed to send invoice email | invoice_id=%s", invoice_id)
        raise


def send_invoice_email_background(invoice_id: int) -> None:
    db = SessionLocal()
    try:
        send_invoice_email(invoice_id, db)
    finally:
        db.close()

