"""Seed sample flights. Run from backend/: python -m scripts.seed"""
import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from app.db.session import async_session_maker
from app.models.flight import Flight, FlightStatus


async def main() -> None:
    async with async_session_maker() as session:
        now = datetime.now(UTC)
        samples = [
            Flight(
                id=uuid.uuid4(),
                flight_number="OZ204",
                departure="RKSI",
                arrival="RJTT",
                aircraft="A350-900",
                status=FlightStatus.BOARDING,
                departure_time=now + timedelta(hours=2),
            ),
            Flight(
                id=uuid.uuid4(),
                flight_number="OZ741",
                departure="RKSI",
                arrival="WSSS",
                aircraft="B777-200ER",
                status=FlightStatus.SCHEDULED,
                departure_time=now + timedelta(hours=6),
            ),
            Flight(
                id=uuid.uuid4(),
                flight_number="OZ562",
                departure="RJTT",
                arrival="RKSI",
                aircraft="A321-200",
                status=FlightStatus.IN_AIR,
                departure_time=now - timedelta(minutes=30),
            ),
        ]
        session.add_all(samples)
        await session.commit()
        print(f"Seeded {len(samples)} flights.")


if __name__ == "__main__":
    asyncio.run(main())
