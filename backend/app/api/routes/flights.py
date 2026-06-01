from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_staff
from app.db.session import get_db
from app.models.flight import Flight, FlightStatus
from app.models.user import User
from app.schemas.flight import FlightCreate, FlightResponse, FlightUpdate
from app.services.discord_webhook import notify_flight_status_change

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("", response_model=list[FlightResponse])
async def list_flights(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: FlightStatus | None = Query(None, alias="status"),
    active_only: bool = False,
):
    q = select(Flight).order_by(Flight.departure_time.asc())
    if status_filter:
        q = q.where(Flight.status == status_filter)
    if active_only:
        q = q.where(
            Flight.status.in_(
                [FlightStatus.BOARDING, FlightStatus.IN_AIR, FlightStatus.SCHEDULED]
            )
        )
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight(
    flight_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flight not found")
    return flight


@router.post("", response_model=FlightResponse, status_code=status.HTTP_201_CREATED)
async def create_flight(
    payload: FlightCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    staff: Annotated[User, Depends(require_staff)],
):
    flight = Flight(**payload.model_dump())
    db.add(flight)
    await db.commit()
    await db.refresh(flight)

    if flight.status != FlightStatus.SCHEDULED:
        await notify_flight_status_change(
            flight,
            FlightStatus.SCHEDULED,
            flight.status,
            updated_by=staff.username,
        )
    return flight


@router.patch("/{flight_id}", response_model=FlightResponse)
async def update_flight(
    flight_id: UUID,
    payload: FlightUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    staff: Annotated[User, Depends(require_staff)],
):
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flight not found")

    previous_status = flight.status
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(flight, key, value)

    await db.commit()
    await db.refresh(flight)

    if "status" in updates and flight.status != previous_status:
        await notify_flight_status_change(
            flight,
            previous_status,
            flight.status,
            updated_by=staff.username,
        )
    return flight


@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(
    flight_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flight not found")
    await db.delete(flight)
    await db.commit()
