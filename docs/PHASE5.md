# Phase 5: Flight Operations and Pilot Progression

## Migration 004 — Schema

### `users` (new columns)

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `total_flight_minutes` | INTEGER | 0 | Approved PIREP time only |
| `pilot_rank` | ENUM | Trainee | Trainee → Senior Captain |

### `pireps` (new table)

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK → users | Pilot |
| `flight_id` | UUID FK → flights | Must match a booking |
| `flight_time_minutes` | INTEGER | Block time |
| `landing_rate_fpm` | INTEGER | Descent rate (fpm) |
| `fuel_used_lbs` | INTEGER NULL | Optional |
| `notes` | TEXT NULL | Optional |
| `status` | ENUM | Pending, Approved, Rejected |
| `won_bonus` | INTEGER NULL | Set on approval |
| `reviewed_by` | UUID FK NULL | Staff reviewer |
| `reviewed_at` | TIMESTAMPTZ NULL | |
| `rejection_reason` | VARCHAR(512) NULL | |
| `created_at` | TIMESTAMPTZ | |

### Transaction types (app layer)

- `Pirep` — WON payout on approval
- `RankPromotion` — audit log (amount 0) on rank change

---

## Rank requirements (`branding.json`)

```json
"pilot_ranks": [
  { "name": "Trainee", "min_hours": 0 },
  { "name": "First Officer", "min_hours": 10 },
  { "name": "Captain", "min_hours": 50 },
  { "name": "Senior Captain", "min_hours": 100 }
]
```

Discord role IDs: `discord.rank_role_ids` or env `DISCORD_ROLE_*`.

---

## API endpoints

### PIREPs (pilots)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/pireps/eligible-flights` | User | Booked flights for dropdown |
| GET | `/api/pireps/me` | User | Own PIREP history |
| POST | `/api/pireps` | User | Submit PIREP (Pending) |

### PIREPs (staff)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/pireps/admin/list?status=Pending` | Staff | Review queue |
| POST | `/api/pireps/admin/{id}/approve` | Staff | Hours + WON + rank |
| POST | `/api/pireps/admin/{id}/reject` | Staff | Reject with reason |

### Leaderboard (public)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/leaderboard` | None | Cached 60s — hours + wealth top 25 |

### Discord roles

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/bot/sync-roles` | Bot key | `{ discord_id, new_rank, old_rank? }` |

Called automatically on rank-up after PIREP approval (Discord REST API via `DISCORD_BOT_TOKEN`).

---

## WON bonus formula

```
bonus = (flight_time_hours × won_per_hour) × landing_multiplier(fpm)
```

Configured in `branding.json` → `pirep.won_per_hour`, `pirep.landing_multipliers`.

---

## Frontend routes

| Route | Purpose |
|-------|---------|
| `/dashboard/log-flight` | PIREP submission form |
| `/admin/pireps` | Staff approve/reject |
| `/leaderboard` | Public rankings |

---

## Apply migration

```bash
cd backend && alembic upgrade head
```
