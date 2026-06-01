import asyncio
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_staff
from app.core.config import get_settings
from app.db.session import get_db
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingDetailResponse, BookingResponse, SeatMapResponse
from app.services.boarding_pass import generate_boarding_pass
from app.services.booking import build_seatmap, create_booking
from app.services.economy import EconomyError

router = APIRouter(prefix="/bookings", tags=["bookings"])
settings = get_settings()


def _booking_response(b: Booking) -> BookingResponse:
    return BookingResponse(
        id=b.id,
        user_id=b.user_id,
        flight_id=b.flight_id,
        seat_number=b.seat_number,
        seat_class=b.seat_class,
        price_won=b.price_won,
        booked_at=b.booked_at,
        boarding_pass_path=b.boarding_pass_path,
        has_boarding_pass=bool(b.boarding_pass_path),
    )


def _pass_file_path(booking: Booking) -> Path:
    if booking.boarding_pass_path:
        name = Path(booking.boarding_pass_path).name
    else:
        name = f"{booking.id}.png"
    return Path(settings.boarding_passes_path) / name


@router.get("/me", response_model=list[BookingDetailResponse])
async def my_bookings(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user.id)
        .options(selectinload(Booking.flight))
        .order_by(Booking.booked_at.desc())
    )
    bookings = result.scalars().all()
    return [
        BookingDetailResponse(
            **_booking_response(b).model_dump(),
            flight=b.flight,
        )
        for b in bookings
    ]


@router.get("/flight/{flight_id}/seatmap", response_model=SeatMapResponse)
async def flight_seatmap(
    flight_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await build_seatmap(db, flight_id)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_seat(
    payload: BookingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    try:
        booking = await create_booking(
            db,
            user.id,
            payload.flight_id,
            payload.seat_number,
            payload.seat_class,
        )
        flight = await db.get(Flight, booking.flight_id)
        if flight:
            await asyncio.to_thread(generate_boarding_pass, booking, user, flight)
            booking.boarding_pass_path = f"{booking.id}.png"
        await db.commit()
        await db.refresh(booking)
    except EconomyError as exc:
        await db.rollback()
        code = status.HTTP_400_BAD_REQUEST
        if exc.code == "seat_taken":
            code = status.HTTP_409_CONFLICT
        elif exc.code == "insufficient_funds":
            code = status.HTTP_402_PAYMENT_REQUIRED
        raise HTTPException(code, exc.message) from exc
    return _booking_response(booking)


@router.get("/{booking_id}/boarding-pass")
async def download_boarding_pass(
    booking_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    if booking.user_id != user.id and user.role.value not in ("Staff", "Admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your booking")

    file_path = _pass_file_path(booking)
    if not file_path.is_file():
        flight = await db.get(Flight, booking.flight_id)
        owner = await db.get(User, booking.user_id)
        if flight and owner:
            await asyncio.to_thread(generate_boarding_pass, booking, owner, flight)
            booking.boarding_pass_path = f"{booking.id}.png"
            await db.commit()
        if not file_path.is_file():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Boarding pass not found")

    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"boarding-pass-{booking.id}.png",
    )


@router.get("", response_model=list[BookingResponse])
async def list_all_bookings(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    result = await db.execute(select(Booking).order_by(Booking.booked_at.desc()))
    return [_booking_response(b) for b in result.scalars().all()]
