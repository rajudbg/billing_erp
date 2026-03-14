from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    Company,
    Currency,
    Role,
    User,
    ServiceCategory,
    Service,
    TaxRate,
)
from app.core.security import get_password_hash


def seed(db: Session) -> None:
    # Currency
    inr = db.query(Currency).filter_by(code="INR").first()
    if not inr:
        inr = Currency(code="INR", name="Indian Rupee", symbol="₹")
        db.add(inr)
        db.flush()

    # Company
    company = db.query(Company).filter_by(name="Demo Company").first()
    if not company:
        company = Company(
            name="Demo Company",
            gst_number="29ABCDE1234F2Z5",
            address_line1="123 Demo Street",
            city="Bengaluru",
            state="Karnataka",
            country="India",
            postal_code="560001",
            email="billing@example.com",
            phone="+91-99999-00000",
            default_currency_id=inr.id,
        )
        db.add(company)
        db.flush()

    # Roles
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator")
        db.add(admin_role)

    finance_role = db.query(Role).filter_by(name="finance").first()
    if not finance_role:
        finance_role = Role(name="finance", description="Finance user")
        db.add(finance_role)

    db.flush()

    # Admin user
    admin_email = "admin@example.com"
    admin_user = db.query(User).filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            full_name="Admin User",
            password_hash=get_password_hash("admin123"),
            is_active=True,
            role=admin_role,
        )
        db.add(admin_user)

    # Default GST tax rate
    gst = (
        db.query(TaxRate)
        .filter(
            TaxRate.company_id == company.id,
            TaxRate.rate_percent == 18,
        )
        .first()
    )
    if not gst:
        gst = TaxRate(
            company_id=company.id,
            name="GST 18%",
            rate_percent=18,
            is_default=True,
        )
        db.add(gst)

    # Sample service category
    category = (
        db.query(ServiceCategory)
        .filter(ServiceCategory.company_id == company.id, ServiceCategory.name == "Consulting")
        .first()
    )
    if not category:
        category = ServiceCategory(
            company_id=company.id,
            name="Consulting",
            description="Consulting services",
        )
        db.add(category)
        db.flush()

    # Sample service
    service = (
        db.query(Service)
        .filter(Service.company_id == company.id, Service.name == "Consulting Services")
        .first()
    )
    if not service:
        service = Service(
            company_id=company.id,
            category_id=category.id,
            name="Consulting Services",
            description="Hourly consulting services",
            unit_price=5000,
            tax_rate_id=gst.id,
            is_active=True,
        )
        db.add(service)

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Seed data created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

