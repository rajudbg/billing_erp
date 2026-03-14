from datetime import date
from typing import List

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_revenue: float
    total_invoices: int
    total_outstanding: float
    total_paid: float


class MonthlyRevenueItem(BaseModel):
    year: int
    month: int
    revenue: float


class OutstandingInvoiceItem(BaseModel):
    id: int
    invoice_number: str
    client_name: str
    issue_date: date
    due_date: date
    amount_due: float


class OutstandingInvoicesResponse(BaseModel):
    invoices: List[OutstandingInvoiceItem]

