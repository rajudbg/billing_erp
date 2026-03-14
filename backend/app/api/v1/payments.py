from decimal import Decimal
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.invoice import Invoice, InvoiceStatusEnum
from app.models.payment import Payment, PaymentAllocation
from app.schemas.payment import (
    PaymentAllocationCreate,
    PaymentCreate,
    PaymentRead,
)


logger = logging.getLogger("erp.billing.payments")

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(deps.get_current_active_user)],
)


def _recalculate_invoice_payment_status(db: Session, invoice: Invoice) -> None:
    total_allocated = (
        db.query(PaymentAllocation)
        .filter(PaymentAllocation.invoice_id == invoice.id)
        .with_entities(PaymentAllocation.allocated_amount)
        .all()
    )
    total_paid = sum(Decimal(str(row[0])) for row in total_allocated)
    invoice.amount_paid = total_paid
    invoice.amount_due = Decimal(str(invoice.total_amount)) - total_paid

    if invoice.amount_due <= 0:
        invoice.status = InvoiceStatusEnum.PAID.value
        invoice.amount_due = 0
    elif invoice.amount_paid > 0:
        invoice.status = InvoiceStatusEnum.PARTIALLY_PAID.value
    else:
        invoice.status = InvoiceStatusEnum.SENT.value


@router.get("/", response_model=List[PaymentRead])
def list_payments(
    db: Session = Depends(deps.get_db),
) -> List[PaymentRead]:
    payments = db.query(Payment).order_by(Payment.payment_date.desc()).all()
    return payments


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(deps.get_db),
) -> PaymentRead:
    total_allocated = sum(a.allocated_amount for a in payment_in.allocations)
    if total_allocated > payment_in.amount + 1e-6:  # small epsilon
        raise HTTPException(
            status_code=400,
            detail="Allocated amount cannot be greater than payment amount",
        )

    if payment_in.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero",
        )

    payment = Payment(
        company_id=payment_in.company_id,
        client_id=payment_in.client_id,
        currency_id=payment_in.currency_id,
        payment_date=payment_in.payment_date,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        reference=payment_in.reference,
        notes=payment_in.notes,
    )
    db.add(payment)
    db.flush()

    for alloc_in in payment_in.allocations:
        if alloc_in.allocated_amount <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Allocated amount for invoice {alloc_in.invoice_id} must be greater than zero",
            )
        invoice = db.get(Invoice, alloc_in.invoice_id)
        if not invoice:
            raise HTTPException(status_code=400, detail=f"Invoice {alloc_in.invoice_id} not found")
        if invoice.client_id != payment_in.client_id:
            raise HTTPException(
                status_code=400,
                detail=f"Invoice {alloc_in.invoice_id} does not belong to the client",
            )

        if alloc_in.allocated_amount > invoice.amount_due + 1e-6:
            raise HTTPException(
                status_code=400,
                detail=f"Allocated amount for invoice {alloc_in.invoice_id} exceeds invoice amount due",
            )

        allocation = PaymentAllocation(
            payment_id=payment.id,
            invoice_id=alloc_in.invoice_id,
            allocated_amount=alloc_in.allocated_amount,
        )
        db.add(allocation)

    db.commit()
    db.refresh(payment)

    # Recalculate invoice statuses
    for alloc in payment.allocations:
        invoice = alloc.invoice
        _recalculate_invoice_payment_status(db, invoice)
    db.commit()
    db.refresh(payment)

    logger.info(
        "Payment recorded | id=%s | company_id=%s | client_id=%s | amount=%s",
        payment.id,
        payment.company_id,
        payment.client_id,
        payment.amount,
    )

    return payment

