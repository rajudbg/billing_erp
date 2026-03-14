from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.dashboard import (
    DashboardSummary,
    MonthlyRevenueItem,
    OutstandingInvoiceItem,
)
from app.services.dashboard_service import (
    get_dashboard_summary,
    get_monthly_revenue,
    get_outstanding_invoices,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(deps.get_current_active_user)],
)


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(deps.get_db)) -> DashboardSummary:
    return get_dashboard_summary(db)


@router.get("/monthly-revenue", response_model=List[MonthlyRevenueItem])
def dashboard_monthly_revenue(db: Session = Depends(deps.get_db)) -> List[MonthlyRevenueItem]:
    return get_monthly_revenue(db)


@router.get("/outstanding-invoices", response_model=List[OutstandingInvoiceItem])
def dashboard_outstanding_invoices(
    db: Session = Depends(deps.get_db),
) -> List[OutstandingInvoiceItem]:
    return get_outstanding_invoices(db)

