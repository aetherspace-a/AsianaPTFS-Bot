"""staff shifts and boarding pass paths

Revision ID: 003
Revises: 002
Create Date: 2026-06-01

Staff Duty Tracking:
  - staff_shifts: records clock-in/clock-out for Staff/Admin users

Boarding Passes:
  - bookings.boarding_pass_path: relative path to generated PNG on disk

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "staff_shifts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("clock_in", sa.DateTime(timezone=True), nullable=False),
        sa.Column("clock_out", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_staff_shifts_user_id", "staff_shifts", ["user_id"])
    op.create_index("ix_staff_shifts_clock_in", "staff_shifts", ["clock_in"])
    op.create_index("ix_staff_shifts_clock_out", "staff_shifts", ["clock_out"])

    op.add_column(
        "bookings",
        sa.Column("boarding_pass_path", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bookings", "boarding_pass_path")
    op.drop_table("staff_shifts")
