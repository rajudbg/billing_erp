from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class PaymentAllocationCreate(BaseModel):
    invoice_id: int
    allocated_amount: float


class PaymentAllocationRead(PaymentAllocationCreate):
    id: int

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    company_id: int
    client_id: int
    currency_id: int
    payment_date: date
    amount: float
    payment_method: str
    reference: str | None = None
    notes: str | None = None


class PaymentCreate(PaymentBase):
    allocations: List[PaymentAllocationCreate]


class PaymentRead(PaymentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    allocations: List[PaymentAllocationRead]

    class Config:
        from_attributes = True

