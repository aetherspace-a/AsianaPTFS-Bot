import random
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.branding import load_branding
from app.models.transaction import Transaction, TransactionType
from app.models.user import User


class EconomyError(Exception):
    def __init__(self, message: str, code: str = "economy_error"):
        self.message = message
        self.code = code
        super().__init__(message)


async def get_user_for_update(session: AsyncSession, user_id: UUID) -> User:
    result = await session.execute(
        select(User).where(User.id == user_id).with_for_update()
    )
    user = result.scalar_one_or_none()
    if not user:
        raise EconomyError("User not found", "not_found")
    return user


async def get_user_by_discord_for_update(
    session: AsyncSession, discord_id: str
) -> User:
    result = await session.execute(
        select(User).where(User.discord_id == discord_id).with_for_update()
    )
    user = result.scalar_one_or_none()
    if not user:
        raise EconomyError("User not found", "not_found")
    return user


async def record_transaction(
    session: AsyncSession,
    user: User,
    amount: int,
    tx_type: TransactionType,
    reference_id: UUID | None = None,
) -> Transaction:
    if amount == 0 and tx_type != TransactionType.RANK_PROMOTION:
        raise EconomyError("Transaction amount cannot be zero")
    if amount != 0:
        new_balance = user.won_balance + amount
        if new_balance < 0:
            raise EconomyError("Insufficient WON balance", "insufficient_funds")
        user.won_balance = new_balance
    tx = Transaction(
        user_id=user.id,
        amount=amount,
        type=tx_type,
        reference_id=reference_id,
    )
    session.add(tx)
    return tx


async def adjust_balance(
    session: AsyncSession,
    user_id: UUID,
    amount: int,
    tx_type: TransactionType,
    reference_id: UUID | None = None,
) -> User:
    user = await get_user_for_update(session, user_id)
    await record_transaction(session, user, amount, tx_type, reference_id)
    return user


async def transfer_won(
    session: AsyncSession,
    from_user_id: UUID,
    to_user_id: UUID,
    amount: int,
) -> tuple[User, User]:
    if amount <= 0:
        raise EconomyError("Transfer amount must be positive")
    if from_user_id == to_user_id:
        raise EconomyError("Cannot pay yourself")

    first_id, second_id = sorted([from_user_id, to_user_id])
    first = await get_user_for_update(session, first_id)
    second = await get_user_for_update(session, second_id)

    sender = first if first.id == from_user_id else second
    receiver = second if sender.id == from_user_id else first

    await record_transaction(session, sender, -amount, TransactionType.PAY)
    await record_transaction(session, receiver, amount, TransactionType.PAY)
    return sender, receiver


async def get_last_work_time(session: AsyncSession, user_id: UUID) -> datetime | None:
    result = await session.execute(
        select(Transaction.timestamp)
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.WORK,
        )
        .order_by(Transaction.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def perform_work(session: AsyncSession, user_id: UUID) -> tuple[int, int]:
    branding = load_branding()
    eco = branding.economy
    cooldown = int(eco.get("work_cooldown_seconds", 3600))
    reward_min = int(eco.get("work_reward_min", 500))
    reward_max = int(eco.get("work_reward_max", 1500))

    user = await get_user_for_update(session, user_id)
    last_work = await get_last_work_time(session, user_id)
    if last_work:
        elapsed = (datetime.now(UTC) - last_work).total_seconds()
        if elapsed < cooldown:
            remaining = int(cooldown - elapsed)
            raise EconomyError(
                f"Work cooldown active ({remaining}s remaining)",
                "cooldown",
            )

    earned = random.randint(reward_min, reward_max)
    await record_transaction(session, user, earned, TransactionType.WORK)
    return earned, user.won_balance


async def perform_coinflip(
    session: AsyncSession,
    user_id: UUID,
    bet: int,
    choice: str,
) -> tuple[bool, int, int, str]:
    branding = load_branding()
    min_bet = int(branding.economy.get("gamble_min_bet", 100))
    max_bet = int(branding.economy.get("gamble_max_bet", 10000))

    if bet < min_bet or bet > max_bet:
        raise EconomyError(f"Bet must be between {min_bet} and {max_bet} WON")

    choice_norm = choice.lower().strip()
    if choice_norm not in ("heads", "tails"):
        raise EconomyError("Choice must be heads or tails")

    result = random.choice(["heads", "tails"])
    user = await get_user_for_update(session, user_id)
    won = choice_norm == result

    if won:
        await record_transaction(session, user, bet, TransactionType.GAMBLE)
        payout = bet
    else:
        await record_transaction(session, user, -bet, TransactionType.GAMBLE)
        payout = -bet

    return won, user.won_balance, result, payout


def work_cooldown_remaining(last_work: datetime | None) -> int:
    if not last_work:
        return 0
    branding = load_branding()
    cooldown = int(branding.economy.get("work_cooldown_seconds", 3600))
    elapsed = (datetime.now(UTC) - last_work).total_seconds()
    return max(0, int(cooldown - elapsed))
