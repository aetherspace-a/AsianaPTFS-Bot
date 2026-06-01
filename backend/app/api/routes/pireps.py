from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_staff
from app.db.session import get_db
from app.models.booking import Booking
from app.models.pirep import Pirep, PirepStatus
from app.models.user import User
from app.schemas.pirep import (
    EligibleFlightOption,
    PirepCreate,
    PirepDetailResponse,
    PirepReject,
    PirepResponse,
)
from app.services.pirep import (
    PirepError,
    approve_pirep,
    calculate_won_bonus,
    reject_pirep,
    submit_pirep,
)

router = APIRouter(prefix="/pireps", tags=["pireps"])


def _pirep_response(p: Pirep, include_estimate: bool = False) -> PirepResponse:
    est = None
    if include_estimate and p.status == PirepStatus.PENDING:
        est = calculate_won_bonus(p.flight_time_minutes, p.landing_rate_fpm)
    return PirepResponse(
        id=p.id,
        user_id=p.user_id,
        flight_id=p.flight_id,
        flight_time_minutes=p.flight_time_minutes,
        landing_rate_fpm=p.landing_rate_fpm,
        fuel_used_lbs=p.fuel_used_lbs,
        notes=p.notes,
        status=p.status,
        won_bonus=p.won_bonus,
        reviewed_by=p.reviewed_by,
        reviewed_at=p.reviewed_at,
        rejection_reason=p.rejection_reason,
        created_at=p.created_at,
        estimated_bonus=est,
    )


@router.get("/eligible-flights", response_model=list[EligibleFlightOption])
async def eligible_flights(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user.id)
        .options(selectinload(Booking.flight))
        .order_by(Booking.booked_at.desc())
    )
    options: list[EligibleFlightOption] = []
    for b in result.scalars().all():
        if not b.flight:
            continue
        options.append(
            EligibleFlightOption(
                flight_id=b.flight_id,
                flight_number=b.flight.flight_number,
                departure=b.flight.departure,
                arrival=b.flight.arrival,
                booking_id=b.id,
                seat_number=b.seat_number,
            )
        )
    return options


@router.get("/me", response_model=list[PirepDetailResponse])
async def my_pireps(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Pirep)
        .where(Pirep.user_id == user.id)
        .options(selectinload(Pirep.flight))
        .order_by(Pirep.created_at.desc())
    )
    return [
        PirepDetailResponse(
            **_pirep_response(p).model_dump(),
            flight=p.flight,
        )
        for p in result.scalars().all()
    ]


@router.post("", response_model=PirepResponse, status_code=status.HTTP_201_CREATED)
async def create_pirep(
    payload: PirepCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    minutes = payload.total_minutes()
    if minutes < 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Flight time must be at least 1 minute")
    try:
        pirep = await submit_pirep(
            db,
            user,
            payload.flight_id,
            minutes,
            payload.landing_rate_fpm,
            payload.fuel_used_lbs,
            payload.notes,
        )
        await db.commit()
        await db.refresh(pirep)
    except PirepError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return _pirep_response(pirep, include_estimate=True)


@router.get("/admin/list", response_model=list[PirepDetailResponse])
async def admin_list_pireps(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
    status_filter: PirepStatus | None = Query(None, alias="status"),
):
    q = (
        select(Pirep)
        .options(selectinload(Pirep.flight), selectinload(Pirep.user))
        .order_by(Pirep.created_at.desc())
        .limit(100)
    )
    if status_filter:
        q = q.where(Pirep.status == status_filter)
    result = await db.execute(q)
    return [
        PirepDetailResponse(
            **_pirep_response(p, include_estimate=True).model_dump(),
            flight=p.flight,
            user=p.user,
        )
        for p in result.scalars().all()
    ]


@router.post("/admin/{pirep_id}/approve", response_model=PirepResponse)
async def admin_approve_pirep(
    pirep_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    reviewer: Annotated[User, Depends(require_staff)],
):
    try:
        pirep = await approve_pirep(db, pirep_id, reviewer)
        await db.commit()
        await db.refresh(pirep)
    except PirepError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return _pirep_response(pirep)


@router.post("/admin/{pirep_id}/reject", response_model=PirepResponse)
async def admin_reject_pirep(
    pirep_id: UUID,
    payload: PirepReject,
    db: Annotated[AsyncSession, Depends(get_db)],
    reviewer: Annotated[User, Depends(require_staff)],
):
    try:
        pirep = await reject_pirep(db, pirep_id, reviewer, payload.reason)
        await db.commit()
        await db.refresh(pirep)
    except PirepError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return _pirep_response(pirep)
