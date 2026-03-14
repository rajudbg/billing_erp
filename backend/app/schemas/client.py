from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class ClientContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    position: str | None = None
    is_primary: bool = False


class ClientContactRead(ClientContactCreate):
    id: int

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str
    gst_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    billing_email: EmailStr | None = None
    is_active: bool = True


class ClientCreate(ClientBase):
    company_id: int
    contacts: List[ClientContactCreate] | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    gst_number: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    billing_email: EmailStr | None = None
    is_active: bool | None = None


class ClientRead(ClientBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    contacts: List[ClientContactRead] = []

    class Config:
        from_attributes = True

