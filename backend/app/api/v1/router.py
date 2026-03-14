from fastapi import APIRouter

from app.api.v1 import auth, clients, services, invoices, payments, dashboard


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(services.router)
api_router.include_router(invoices.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)

