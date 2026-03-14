from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models import Company, Currency, Client, Service, Invoice, PaymentAllocation


client = TestClient(app)


def get_db() -> Session:
  return SessionLocal()


def get_auth_token() -> str:
  resp = client.post(
      "/api/v1/auth/login-json",
      json={"email": "admin@example.com", "password": "admin123"},
  )
  assert resp.status_code == 200
  return resp.json()["access_token"]


def auth_headers() -> dict[str, str]:
  token = get_auth_token()
  return {"Authorization": f"Bearer {token}"}


def test_invoice_creation_and_totals() -> None:
  db = get_db()
  try:
    company = db.query(Company).first()
    currency = db.query(Currency).first()
    test_client = db.query(Client).first()
    service = db.query(Service).first()
    assert company and currency and test_client and service

    payload = {
        "company_id": company.id,
        "client_id": test_client.id,
        "currency_id": currency.id,
        "issue_date": date.today().isoformat(),
        "due_date": date.today().isoformat(),
        "items": [
            {
                "service_id": service.id,
                "description": "Test line",
                "quantity": 2,
                "unit_price": float(service.unit_price),
                "tax_rate_percent": 18.0,
            }
        ],
    }

    resp = client.post("/api/v1/invoices", json=payload, headers=auth_headers())
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["total_amount"] == round(data["subtotal_amount"] + data["tax_amount"], 2)
    assert data["amount_due"] == data["total_amount"]
  finally:
    db.close()


def test_payment_allocation_updates_invoice() -> None:
  db = get_db()
  try:
    invoice = (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .first()
    )
    assert invoice is not None

    half = float(invoice.total_amount) / 2
    payload = {
        "company_id": invoice.company_id,
        "client_id": invoice.client_id,
        "currency_id": invoice.currency_id,
        "payment_date": date.today().isoformat(),
        "amount": half,
        "payment_method": "bank_transfer",
        "allocations": [
            {"invoice_id": invoice.id, "allocated_amount": half},
        ],
    }
    resp = client.post("/api/v1/payments", json=payload, headers=auth_headers())
    assert resp.status_code == 201, resp.text

    db.refresh(invoice)
    assert float(invoice.amount_paid) >= half - 0.01
    assert float(invoice.amount_due) <= float(invoice.total_amount)
  finally:
    db.close()


def test_dashboard_summary_endpoint() -> None:
  resp = client.get("/api/v1/dashboard/summary", headers=auth_headers())
  assert resp.status_code == 200
  data = resp.json()
  assert "total_revenue" in data
  assert "total_invoices" in data
  assert "total_outstanding" in data
  assert "total_paid" in data

