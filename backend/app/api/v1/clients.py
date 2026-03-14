from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.client import Client, ClientContact
from app.schemas.client import (
    ClientCreate,
    ClientRead,
    ClientUpdate,
    ClientContactCreate,
)


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(deps.get_current_active_user)],
)


@router.get("/", response_model=List[ClientRead])
def list_clients(
    db: Session = Depends(deps.get_db),
) -> List[ClientRead]:
    clients = db.query(Client).order_by(Client.created_at.desc()).all()
    return clients


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(deps.get_db),
) -> ClientRead:
    client = Client(
        company_id=client_in.company_id,
        name=client_in.name,
        gst_number=client_in.gst_number,
        address_line1=client_in.address_line1,
        address_line2=client_in.address_line2,
        city=client_in.city,
        state=client_in.state,
        country=client_in.country,
        postal_code=client_in.postal_code,
        billing_email=client_in.billing_email,
        is_active=client_in.is_active,
    )
    if client_in.contacts:
        for contact_in in client_in.contacts:
            contact = ClientContact(
                name=contact_in.name,
                email=contact_in.email,
                phone=contact_in.phone,
                position=contact_in.position,
                is_primary=contact_in.is_primary,
            )
            client.contacts.append(contact)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(deps.get_db),
) -> ClientRead:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: Session = Depends(deps.get_db),
) -> ClientRead:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    data = client_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(client, field, value)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(deps.get_db),
) -> None:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return None

