from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.branding import load_branding
from app.models.booking import Booking, SeatClass
from app.models.flight import Flight, FlightStatus
from app.models.transaction import TransactionType
from app.schemas.booking import SeatMapResponse, SeatMapSeat
from app.services.economy import EconomyError, get_user_for_update, record_transaction

SEAT_PRICES: dict[SeatClass, int] = {
    SeatClass.ECONOMY: 1000,
    SeatClass.BUSINESS: 2500,
    SeatClass.FIRST: 5000,
}


def seat_price(seat_class: SeatClass) -> int:
    return SEAT_PRICES.get(seat_class, 1000)


def generate_seat_numbers(rows: int, seats_per_row: int) -> list[str]:
    seats: list[str] = []
    cols = "ABCDEF"[:seats_per_row]
    for row in range(1, rows + 1):
        for col in cols:
            seats.append(f"{row}{col}")
    return seats


async def get_flight_or_404(session: AsyncSession, flight_id: UUID) -> Flight:
    flight = await session.get(Flight, flight_id)
    if not flight:
        raise EconomyError("Flight not found", "not_found")
    return flight


async def build_seatmap(session: AsyncSession, flight_id: UUID) -> SeatMapResponse:
    branding = load_branding()
    rows = int(branding.flights.get("default_seat_rows", 30))
    seats_per_row = int(branding.flights.get("default_seats_per_row", 6))

    await get_flight_or_404(session, flight_id)

    result = await session.execute(
        select(Booking).where(Booking.flight_id == flight_id)
    )
    booked = {b.seat_number: b for b in result.scalars().all()}

    seats: list[SeatMapSeat] = []
    for seat_num in generate_seat_numbers(rows, seats_per_row):
        booking = booked.get(seat_num)
        seats.append(
            SeatMapSeat(
                seat_number=seat_num,
                seat_class=booking.seat_class if booking else None,
                available=booking is None,
                booked_by=booking.user_id if booking else None,
            )
        )

    return SeatMapResponse(
        flight_id=flight_id,
        rows=rows,
        seats_per_row=seats_per_row,
        seats=seats,
    )


async def create_booking(
    session: AsyncSession,
    user_id: UUID,
    flight_id: UUID,
    seat_number: str,
    seat_class: SeatClass,
) -> Booking:
    flight = await get_flight_or_404(session, flight_id)
    if flight.status == FlightStatus.LANDED:
        raise EconomyError("Cannot book a landed flight", "flight_closed")

    seat_number = seat_number.upper()
    existing = await session.execute(
        select(Booking).where(
            Booking.flight_id == flight_id,
            Booking.seat_number == seat_number,
        )
    )
    if existing.scalar_one_or_none():
        raise EconomyError("Seat already booked", "seat_taken")

    price = seat_price(seat_class)
    user = await get_user_for_update(session, user_id)

    booking = Booking(
        user_id=user_id,
        flight_id=flight_id,
        seat_number=seat_number,
        seat_class=seat_class,
        price_won=price,
    )
    session.add(booking)
    await session.flush()

    try:
        await record_transaction(
            session,
            user,
            -price,
            TransactionType.BOOKING,
            reference_id=booking.id,
        )
    except EconomyError:
        raise

    try:
        await session.flush()
    except IntegrityError as exc:
        raise EconomyError("Seat already booked", "seat_taken") from exc

    return booking
