# Phase 4: Operations and Immersion

## Migration 003 — `staff_shifts` + `bookings.boarding_pass_path`

### Table: `staff_shifts`

| Column       | Type              | Notes                                      |
|-------------|-------------------|--------------------------------------------|
| `id`        | UUID PK           | Default `uuid4`                            |
| `user_id`   | UUID FK → `users` | Staff/Admin who clocked in                 |
| `clock_in`  | TIMESTAMPTZ       | Shift start (required)                     |
| `clock_out` | TIMESTAMPTZ NULL  | `NULL` = currently on duty                 |
| `created_at`| TIMESTAMPTZ       | Row created                                |

**Indexes:** `user_id`, `clock_in`, `clock_out`

**Rules (application layer):**

- Only `Staff` / `Admin` roles may clock in/out
- At most one open shift per user (`clock_out IS NULL`)
- Duration = `clock_out - clock_in` (or `now - clock_in` if active)

### Column: `bookings.boarding_pass_path`

| Column                 | Type           | Notes                                |
|------------------------|----------------|--------------------------------------|
| `boarding_pass_path`   | VARCHAR(512)   | Filename e.g. `{booking_id}.png`     |

PNG files live on disk under `storage/boarding_passes/` (config: `BOARDING_PASSES_PATH`).

---

## Boarding pass — directory / file layout

```
asiana-ptfs-va/
├── storage/
│   └── boarding_passes/          # Generated PNGs (Docker volume)
│       └── {booking_id}.png
├── backend/
│   └── app/
│       └── services/
│           └── boarding_pass/
│               ├── __init__.py       # exports generate_boarding_pass
│               └── generator.py      # Pillow + qrcode rendering
```

### New / updated backend files

| File | Purpose |
|------|---------|
| `services/boarding_pass/generator.py` | Build 900×420 PNG with branding colors, fields, QR JSON payload |
| `services/discord_webhook.py` | POST embed to `DISCORD_WEBHOOK_URL` on status change |
| `services/duty.py` | `clock_in`, `clock_out`, `list_shifts`, duration helpers |
| `models/staff_shift.py` | SQLAlchemy model |
| `api/routes/bookings.py` | Generate on book; `GET /{id}/boarding-pass` download |
| `api/routes/flights.py` | Webhook after PATCH/POST status change |
| `api/routes/admin.py` | `GET /admin/staff/shifts`, `/admin/staff/summary` |
| `api/routes/bot.py` | `POST /bot/duty/clockin`, `clockout`, status |

### Dependencies

- `Pillow` — image canvas, fonts, shapes
- `qrcode` — QR encoding booking JSON

### API

- `POST /api/bookings` → generates pass, sets `boarding_pass_path`
- `GET /api/bookings/{booking_id}/boarding-pass` → `FileResponse` (owner or staff)

### Frontend

| File | Purpose |
|------|---------|
| `src/lib/api.ts` | `downloadFile()` for authenticated PNG download |
| `src/app/dashboard/page.tsx` | “Download boarding pass” per upcoming booking |
| `src/app/admin/staff/page.tsx` | Staff hours table + shift log |
| `bot/cogs/duty.py` | `/clockin`, `/clockout` slash commands |

### Environment

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
BOARDING_PASSES_PATH=/app/storage/boarding_passes
```

Run migration:

```bash
cd backend && alembic upgrade head
```
