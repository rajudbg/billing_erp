from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class InvoiceItemCreate(BaseModel):
    service_id: int | None = None
    description: str
    quantity: float
    unit_price: float
    tax_rate_percent: float


class InvoiceItemRead(InvoiceItemCreate):
    id: int
    line_subtotal: float
    line_tax_amount: float
    line_total: float
    sort_order: int

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    company_id: int
    client_id: int
    currency_id: int
    issue_date: date
    due_date: date
    notes: str | None = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceRead(InvoiceBase):
    id: int
    invoice_number: str
    status: str
    subtotal_amount: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    amount_due: float
    pdf_path: str | None
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemRead]

    class Config:
        from_attributes = True

