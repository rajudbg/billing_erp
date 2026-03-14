from datetime import date
from decimal import Decimal
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatusEnum
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceRead,
    InvoiceItemCreate,
)
from app.pdf.generator import render_invoice_pdf
from app.emailing.mailer import send_invoice_email_background


logger = logging.getLogger("erp.billing.invoices")

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    dependencies=[Depends(deps.get_current_active_user)],
)


def _generate_invoice_number(db: Session, company_id: int, issue_date: date) -> str:
    # Format: INV-YYYY-0001 per company per year
    year = issue_date.year

    last_invoice = (
        db.query(Invoice)
        .filter(Invoice.company_id == company_id, Invoice.issue_date.between(date(year, 1, 1), date(year, 12, 31)))
        .order_by(Invoice.id.desc())
        .first()
    )
    if not last_invoice:
        return f"INV-{year}-0001"

    try:
        last_seq_str = last_invoice.invoice_number.split("-")[-1]
        last_seq = int(last_seq_str)
    except (IndexError, ValueError):
        last_seq = last_invoice.id

    next_seq = last_seq + 1
    return f"INV-{year}-{next_seq:04d}"


def _calculate_totals(
    db: Session,
    company_id: int,
    items_in: List[InvoiceItemCreate],
) -> tuple[Decimal, Decimal, Decimal, List[InvoiceItem]]:
    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")
    items: List[InvoiceItem] = []

    for idx, item_in in enumerate(items_in):
        quantity = Decimal(str(item_in.quantity))
        unit_price = Decimal(str(item_in.unit_price))
        tax_rate_percent = Decimal(str(item_in.tax_rate_percent))

        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Line {idx + 1}: quantity must be greater than zero",
            )
        if unit_price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Line {idx + 1}: unit_price cannot be negative",
            )
        if tax_rate_percent < 0 or tax_rate_percent > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Line {idx + 1}: tax_rate_percent must be between 0 and 100",
            )

        line_subtotal = quantity * unit_price
        line_tax_amount = (line_subtotal * tax_rate_percent) / Decimal("100")
        line_total = line_subtotal + line_tax_amount

        subtotal += line_subtotal
        tax_total += line_tax_amount

        invoice_item = InvoiceItem(
            service_id=item_in.service_id,
            description=item_in.description,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate_percent=tax_rate_percent,
            line_subtotal=line_subtotal,
            line_tax_amount=line_tax_amount,
            line_total=line_total,
            sort_order=idx,
        )
        items.append(invoice_item)

    total = subtotal + tax_total
    return subtotal, tax_total, total, items


@router.get("/", response_model=List[InvoiceRead])
def list_invoices(
    db: Session = Depends(deps.get_db),
) -> List[InvoiceRead]:
    invoices = db.query(Invoice).order_by(Invoice.issue_date.desc()).all()
    return invoices


@router.post("/", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_in: InvoiceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> InvoiceRead:
    if invoice_in.due_date < invoice_in.issue_date:
        raise HTTPException(status_code=400, detail="Due date cannot be before issue date")

    invoice_number = _generate_invoice_number(db, invoice_in.company_id, invoice_in.issue_date)

    subtotal, tax_total, total, items = _calculate_totals(
        db, invoice_in.company_id, invoice_in.items
    )

    invoice = Invoice(
        company_id=invoice_in.company_id,
        client_id=invoice_in.client_id,
        currency_id=invoice_in.currency_id,
        invoice_number=invoice_number,
        issue_date=invoice_in.issue_date,
        due_date=invoice_in.due_date,
        status=InvoiceStatusEnum.DRAFT.value,
        subtotal_amount=subtotal,
        tax_amount=tax_total,
        total_amount=total,
        amount_paid=0,
        amount_due=total,
        notes=invoice_in.notes,
    )
    for item in items:
        invoice.items.append(item)

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    logger.info(
        "Invoice created | id=%s | number=%s | company_id=%s | client_id=%s | total=%s",
        invoice.id,
        invoice.invoice_number,
        invoice.company_id,
        invoice.client_id,
        invoice.total_amount,
    )

    # Generate PDF and update invoice
    pdf_path = render_invoice_pdf(invoice)
    invoice.pdf_path = pdf_path
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


@router.post("/{invoice_id}/send-email", status_code=status.HTTP_202_ACCEPTED)
def send_invoice_email(
    invoice_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> dict:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    logger.info("Queueing invoice email | invoice_id=%s", invoice_id)
    background_tasks.add_task(send_invoice_email_background, invoice_id)
    return {"status": "queued"}


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(deps.get_db),
) -> InvoiceRead:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

