from datetime import datetime
from typing import List

from pydantic import BaseModel


class ServiceCategoryBase(BaseModel):
    name: str
    description: str | None = None


class ServiceCategoryCreate(ServiceCategoryBase):
    company_id: int


class ServiceCategoryRead(ServiceCategoryBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaxRateBase(BaseModel):
    name: str
    rate_percent: float
    is_default: bool = False


class TaxRateCreate(TaxRateBase):
    company_id: int


class TaxRateRead(TaxRateBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    name: str
    description: str | None = None
    unit_price: float
    tax_rate_id: int | None = None
    category_id: int | None = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    company_id: int


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    unit_price: float | None = None
    tax_rate_id: int | None = None
    category_id: int | None = None
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

