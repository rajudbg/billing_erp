from __future__ import annotations

from decimal import Decimal
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.payment import Payment
from app.schemas.dashboard import (
    DashboardSummary,
    MonthlyRevenueItem,
    OutstandingInvoiceItem,
)


def get_dashboard_summary(db: Session) -> DashboardSummary:
    total_revenue = (
        db.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).scalar() or Decimal("0")
    )
    total_invoices = db.query(func.count(Invoice.id)).scalar() or 0
    total_outstanding = (
        db.query(func.coalesce(func.sum(Invoice.amount_due), 0)).scalar() or Decimal("0")
    )
    total_paid = total_revenue

    return DashboardSummary(
        total_revenue=float(total_revenue),
        total_invoices=int(total_invoices),
        total_outstanding=float(total_outstanding),
        total_paid=float(total_paid),
    )


def get_monthly_revenue(db: Session) -> List[MonthlyRevenueItem]:
    results = (
        db.query(
            func.extract("year", Payment.payment_date).label("year"),
            func.extract("month", Payment.payment_date).label("month"),
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    items: List[MonthlyRevenueItem] = []
    for year, month, revenue in results:
        items.append(
            MonthlyRevenueItem(
                year=int(year),
                month=int(month),
                revenue=float(revenue),
            )
        )
    return items


def get_outstanding_invoices(db: Session) -> List[OutstandingInvoiceItem]:
    invoices = (
        db.query(Invoice)
        .filter(Invoice.amount_due > 0)
        .order_by(Invoice.due_date.asc())
        .all()
    )

    items: List[OutstandingInvoiceItem] = []
    for inv in invoices:
        items.append(
            OutstandingInvoiceItem(
                id=inv.id,
                invoice_number=inv.invoice_number,
                client_name=inv.client.name,
                issue_date=inv.issue_date,
                due_date=inv.due_date,
                amount_due=float(inv.amount_due),
            )
        )
    return items

