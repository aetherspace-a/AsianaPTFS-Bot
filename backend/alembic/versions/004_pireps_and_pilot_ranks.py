"""pireps and pilot ranks

Revision ID: 004
Revises: 003
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("total_flight_minutes", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column(
            "pilot_rank",
            sa.Enum(
                "Trainee",
                "First Officer",
                "Captain",
                "Senior Captain",
                name="pilot_rank",
                native_enum=False,
            ),
            server_default="Trainee",
            nullable=False,
        ),
    )

    op.create_table(
        "pireps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("flight_id", sa.UUID(), nullable=False),
        sa.Column("flight_time_minutes", sa.Integer(), nullable=False),
        sa.Column("landing_rate_fpm", sa.Integer(), nullable=False),
        sa.Column("fuel_used_lbs", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("Pending", "Approved", "Rejected", name="pirep_status", native_enum=False),
            server_default="Pending",
            nullable=False,
        ),
        sa.Column("won_bonus", sa.Integer(), nullable=True),
        sa.Column("reviewed_by", sa.UUID(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["flight_id"], ["flights.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pireps_user_id", "pireps", ["user_id"])
    op.create_index("ix_pireps_flight_id", "pireps", ["flight_id"])
    op.create_index("ix_pireps_status", "pireps", ["status"])


def downgrade() -> None:
    op.drop_table("pireps")
    op.drop_column("users", "pilot_rank")
    op.drop_column("users", "total_flight_minutes")
