from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.service import Service, ServiceCategory, TaxRate
from app.schemas.service import (
    ServiceCategoryCreate,
    ServiceCategoryRead,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
    TaxRateCreate,
    TaxRateRead,
)


router = APIRouter(
    prefix="/services",
    tags=["services"],
    dependencies=[Depends(deps.get_current_active_user)],
)


@router.get("/categories", response_model=List[ServiceCategoryRead])
def list_categories(db: Session = Depends(deps.get_db)) -> List[ServiceCategoryRead]:
    return db.query(ServiceCategory).order_by(ServiceCategory.name).all()


@router.post("/categories", response_model=ServiceCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: ServiceCategoryCreate,
    db: Session = Depends(deps.get_db),
) -> ServiceCategoryRead:
    category = ServiceCategory(
        company_id=category_in.company_id,
        name=category_in.name,
        description=category_in.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/tax-rates", response_model=List[TaxRateRead])
def list_tax_rates(db: Session = Depends(deps.get_db)) -> List[TaxRateRead]:
    return db.query(TaxRate).order_by(TaxRate.rate_percent).all()


@router.post("/tax-rates", response_model=TaxRateRead, status_code=status.HTTP_201_CREATED)
def create_tax_rate(
    tax_in: TaxRateCreate,
    db: Session = Depends(deps.get_db),
) -> TaxRateRead:
    tax = TaxRate(
        company_id=tax_in.company_id,
        name=tax_in.name,
        rate_percent=tax_in.rate_percent,
        is_default=tax_in.is_default,
    )
    if tax.is_default:
        db.query(TaxRate).filter(
            TaxRate.company_id == tax_in.company_id, TaxRate.is_default.is_(True)
        ).update({TaxRate.is_default: False})

    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


@router.get("/", response_model=List[ServiceRead])
def list_services(db: Session = Depends(deps.get_db)) -> List[ServiceRead]:
    return db.query(Service).order_by(Service.name).all()


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(deps.get_db),
) -> ServiceRead:
    service = Service(
        company_id=service_in.company_id,
        category_id=service_in.category_id,
        name=service_in.name,
        description=service_in.description,
        unit_price=service_in.unit_price,
        tax_rate_id=service_in.tax_rate_id,
        is_active=service_in.is_active,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
) -> ServiceRead:
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(deps.get_db),
) -> ServiceRead:
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    data = service_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(service, field, value)

    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
) -> None:
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return None

