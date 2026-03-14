from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    Company,
    Client,
    Currency,
    Invoice,
    InvoiceItem,
    InvoiceStatusEnum,
    Payment,
    PaymentAllocation,
    Service,
    TaxRate,
)


def create_test_data(db: Session) -> None:
    company = db.query(Company).filter_by(name="Demo Company").first()
    if not company:
        raise RuntimeError("Demo Company not found. Run seed_data first.")

    currency = db.query(Currency).filter_by(code="INR").first()
    if not currency:
        raise RuntimeError("INR currency not found. Run seed_data first.")

    tax_rate = (
        db.query(TaxRate)
        .filter(TaxRate.company_id == company.id, TaxRate.is_default.is_(True))
        .first()
    )
    if not tax_rate:
        raise RuntimeError("Default tax rate not found. Run seed_data first.")

    # Clients
    client_names = ["Acme Corp", "Beta Industries", "Charlie LLC"]
    clients: list[Client] = []
    for name in client_names:
        client = db.query(Client).filter_by(company_id=company.id, name=name).first()
        if not client:
            client = Client(
                company_id=company.id,
                name=name,
                billing_email=f"billing+{name.replace(' ', '').lower()}@example.com",
                country="India",
                is_active=True,
            )
            db.add(client)
            db.flush()
        clients.append(client)

    # Services
    services: list[Service] = []
    service_defs = [
        ("Monthly Retainer", Decimal("25000.00")),
        ("Implementation Work", Decimal("15000.00")),
        ("Support Hours", Decimal("5000.00")),
    ]
    for name, price in service_defs:
        service = (
            db.query(Service)
            .filter(Service.company_id == company.id, Service.name == name)
            .first()
        )
        if not service:
            service = Service(
                company_id=company.id,
                name=name,
                description=name,
                unit_price=price,
                tax_rate_id=tax_rate.id,
                is_active=True,
            )
            db.add(service)
            db.flush()
        services.append(service)

    today = date.today()

    def make_invoice(
        client: Client,
        days_offset: int,
        status: InvoiceStatusEnum,
        fully_paid: bool = False,
        partially_paid: bool = False,
    ) -> Invoice:
        issue = today + timedelta(days=days_offset)
        due = issue + timedelta(days=14)
        invoice = (
            db.query(Invoice)
            .filter(
                Invoice.company_id == company.id,
                Invoice.client_id == client.id,
                Invoice.issue_date == issue,
                Invoice.status == status.value,
            )
            .first()
        )
        if invoice:
            return invoice

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")

        invoice = Invoice(
            company_id=company.id,
            client_id=client.id,
            currency_id=currency.id,
            invoice_number=f"TEST-{client.id}-{issue.isoformat()}",
            issue_date=issue,
            due_date=due,
            status=status.value,
            subtotal_amount=0,
            tax_amount=0,
            total_amount=0,
            amount_paid=0,
            amount_due=0,
        )
        db.add(invoice)
        db.flush()

        for idx, service in enumerate(services[:2]):
            qty = Decimal("1")
            unit_price = Decimal(str(service.unit_price))
            line_sub = qty * unit_price
            line_tax = (line_sub * Decimal(str(tax_rate.rate_percent))) / Decimal("100")
            line_total = line_sub + line_tax
            subtotal += line_sub
            tax_total += line_tax

            item = InvoiceItem(
                invoice_id=invoice.id,
                service_id=service.id,
                description=service.name,
                quantity=qty,
                unit_price=unit_price,
                tax_rate_percent=tax_rate.rate_percent,
                line_subtotal=line_sub,
                line_tax_amount=line_tax,
                line_total=line_total,
                sort_order=idx,
            )
            db.add(item)

        total = subtotal + tax_total
        invoice.subtotal_amount = subtotal
        invoice.tax_amount = tax_total
        invoice.total_amount = total
        invoice.amount_due = total

        db.flush()

        # Payments
        if fully_paid:
            payment = Payment(
                company_id=company.id,
                client_id=client.id,
                currency_id=currency.id,
                payment_date=issue + timedelta(days=5),
                amount=total,
                payment_method="bank_transfer",
            )
            db.add(payment)
            db.flush()

            alloc = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                allocated_amount=total,
            )
            db.add(alloc)
            invoice.amount_paid = total
            invoice.amount_due = Decimal("0.00")
            invoice.status = InvoiceStatusEnum.PAID.value

        elif partially_paid:
            half = (total / 2).quantize(Decimal("0.01"))
            payment = Payment(
                company_id=company.id,
                client_id=client.id,
                currency_id=currency.id,
                payment_date=issue + timedelta(days=3),
                amount=half,
                payment_method="bank_transfer",
            )
            db.add(payment)
            db.flush()

            alloc = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                allocated_amount=half,
            )
            db.add(alloc)
            invoice.amount_paid = half
            invoice.amount_due = total - half
            invoice.status = InvoiceStatusEnum.PARTIALLY_PAID.value

        db.commit()
        db.refresh(invoice)
        return invoice

    # Create invoices with different statuses
    make_invoice(clients[0], days_offset=-30, status=InvoiceStatusEnum.PAID, fully_paid=True)
    make_invoice(clients[1], days_offset=-10, status=InvoiceStatusEnum.PARTIALLY_PAID, partially_paid=True)
    make_invoice(clients[2], days_offset=0, status=InvoiceStatusEnum.SENT, fully_paid=False)


def main() -> None:
    db = SessionLocal()
    try:
        create_test_data(db)
        print("Test data created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

