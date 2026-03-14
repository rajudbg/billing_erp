from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.config import get_settings
from app.models.invoice import Invoice


settings = get_settings()


def ensure_output_dir() -> Path:
    output_dir = Path(settings.invoice_pdf_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def render_invoice_pdf(invoice: Invoice) -> str:
    """
    Generate a simple PDF for the given invoice and return the file path.
    """
    output_dir = ensure_output_dir()
    filename = f"invoice_{invoice.invoice_number}.pdf"
    output_path = output_dir / filename

    company = invoice.company
    client = invoice.client

    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    y = height - 30 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, company.name or "Company")
    y -= 10 * mm

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Invoice: {invoice.invoice_number}")
    y -= 5 * mm
    c.drawString(20 * mm, y, f"Issue date: {invoice.issue_date}")
    y -= 5 * mm
    c.drawString(20 * mm, y, f"Due date: {invoice.due_date}")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y, "Bill To:")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, client.name or "")
    y -= 5 * mm
    if client.billing_email:
        c.drawString(20 * mm, y, f"Email: {client.billing_email}")
        y -= 5 * mm

    y -= 8 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Description")
    c.drawString(90 * mm, y, "Qty")
    c.drawString(110 * mm, y, "Unit Price")
    c.drawString(140 * mm, y, "GST %")
    c.drawString(165 * mm, y, "Total")
    y -= 4 * mm
    c.line(20 * mm, y, 190 * mm, y)
    y -= 4 * mm

    c.setFont("Helvetica", 10)
    for item in invoice.items:
        if y < 40 * mm:
            c.showPage()
            y = height - 30 * mm
            c.setFont("Helvetica", 10)
        c.drawString(20 * mm, y, item.description[:40])
        c.drawRightString(100 * mm, y, f"{float(item.quantity):.2f}")
        c.drawRightString(130 * mm, y, f"{float(item.unit_price):.2f}")
        c.drawRightString(155 * mm, y, f"{float(item.tax_rate_percent):.2f}")
        c.drawRightString(190 * mm, y, f"{float(item.line_total):.2f}")
        y -= 5 * mm

    y -= 8 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(155 * mm, y, "Subtotal:")
    c.drawRightString(190 * mm, y, f"{float(invoice.subtotal_amount):.2f}")
    y -= 5 * mm
    c.drawRightString(155 * mm, y, "GST:")
    c.drawRightString(190 * mm, y, f"{float(invoice.tax_amount):.2f}")
    y -= 5 * mm
    c.drawRightString(155 * mm, y, "Total:")
    c.drawRightString(190 * mm, y, f"{float(invoice.total_amount):.2f}")
    y -= 5 * mm
    c.drawRightString(155 * mm, y, "Amount Paid:")
    c.drawRightString(190 * mm, y, f"{float(invoice.amount_paid):.2f}")
    y -= 5 * mm
    c.drawRightString(155 * mm, y, "Amount Due:")
    c.drawRightString(190 * mm, y, f"{float(invoice.amount_due):.2f}")

    c.showPage()
    c.save()

    return str(output_path)

