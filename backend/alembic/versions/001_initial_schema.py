"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("discord_id", sa.String(length=32), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("won_balance", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "role",
            sa.Enum("User", "Staff", "Admin", name="user_role", native_enum=False),
            server_default="User",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_discord_id", "users", ["discord_id"], unique=True)

    op.create_table(
        "flights",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("flight_number", sa.String(length=16), nullable=False),
        sa.Column("departure", sa.String(length=8), nullable=False),
        sa.Column("arrival", sa.String(length=8), nullable=False),
        sa.Column(
            "status",
            sa.Enum("Scheduled", "Boarding", "In-Air", "Landed", name="flight_status", native_enum=False),
            server_default="Scheduled",
            nullable=False,
        ),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_flights_flight_number", "flights", ["flight_number"])
    op.create_index("ix_flights_status", "flights", ["status"])
    op.create_index("ix_flights_departure_time", "flights", ["departure_time"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("flight_id", sa.UUID(), nullable=False),
        sa.Column("seat_number", sa.String(length=8), nullable=False),
        sa.Column(
            "seat_class",
            sa.Enum("Economy", "Business", "First", name="seat_class", native_enum=False),
            nullable=False,
        ),
        sa.Column("price_won", sa.Integer(), nullable=False),
        sa.Column("booked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("flight_id", "seat_number", name="uq_booking_flight_seat"),
    )
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])
    op.create_index("ix_bookings_flight_id", "bookings", ["flight_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("Work", "Gamble", "Booking", "Admin", "Pay", name="transaction_type", native_enum=False),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reference_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_type", "transactions", ["type"])
    op.create_index("ix_transactions_timestamp", "transactions", ["timestamp"])


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("bookings")
    op.drop_table("flights")
    op.drop_table("users")
