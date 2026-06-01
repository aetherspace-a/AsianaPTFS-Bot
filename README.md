# Asiana Airlines PTFS — Virtual Airline Management System

High-performance, white-label virtual airline platform for Pilot Training Flight Simulator (PTFS).

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, Tailwind, TypeScript |
| Backend | FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL |
| Bot | discord.py, gTTS, FFmpeg |
| Infra | Docker Compose, GitHub Actions CI |

## Quick start (local)

### Database

```bash
docker compose up -d db
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Discord bot

```bash
pip install -r bot/requirements.txt
set DISCORD_BOT_TOKEN=your_token
set BOT_API_KEY=dev-bot-key-change-me
python bot/main.py
```

## Docker (full stack)

Core services (DB + API + Web):

```bash
docker compose up --build
```

Include Discord bot:

```bash
docker compose --profile full up --build
```

| Service | URL |
|---------|-----|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Static assets | http://localhost:8000/assets/logos/ |

**Note:** `NEXT_PUBLIC_API_URL` must be reachable from the **browser** (typically `http://localhost:8000`), not the internal Docker hostname `api`.

## Phase 5 features

| Feature | Description |
|---------|-------------|
| **PIREPs** | Pilots log flights at `/dashboard/log-flight`; staff approve at `/admin/pireps` |
| **Ranks** | Trainee → Senior Captain by approved hours (`branding.json`) |
| **Discord roles** | Auto-sync rank roles on promotion (`DISCORD_BOT_TOKEN` + role IDs) |
| **Leaderboard** | Public `/leaderboard` — hours & WON (60s API cache) |

See [docs/PHASE5.md](docs/PHASE5.md).

## Phase 4 features

| Feature | Description |
|---------|-------------|
| **Discord webhooks** | Flight status changes from admin dispatcher → `#flight-updates` embed (`DISCORD_WEBHOOK_URL`) |
| **Boarding passes** | PNG with passenger, flight, seat, class, QR — download from dashboard |
| **Staff duty** | `/clockin` / `/clockout` (Discord) → `staff_shifts` table → `/admin/staff` |

See [docs/PHASE4.md](docs/PHASE4.md) for schema and file layout details.

## Phase 3 features

### Staff admin UI

| Route | Purpose |
|-------|---------|
| `/admin` | Analytics overview |
| `/admin/flights` | Flight dispatcher — schedule, aircraft, live status |
| `/admin/users` | WON adjustments, roles, transaction history |

### Assets

- Source of truth: `assets/logos/` at repo root
- Next.js serves copies from `frontend/public/assets/`
- FastAPI serves `GET /assets/*` from the same folder
- `BrandLogo` component falls back to `placeholder.svg` on load error

### CI/CD

GitHub Actions (`.github/workflows/ci.yml`):

- Python: Black, Flake8, pytest, Alembic against ephemeral Postgres
- Next.js: ESLint, Prettier, TypeScript, production build

### Linting locally

```bash
# Backend
cd backend && pip install -r requirements-dev.txt
black app tests scripts
flake8 app tests scripts

# Frontend
cd frontend && npm run lint && npm run format:check
```

## Configuration

- **branding.json** — airline identity, colors, logo paths, economy tuning
- **.env** — secrets and URLs (see `.env.example`)

### Discord OAuth

Redirect URI: `http://localhost:8000/api/auth/discord/callback`

### Promote staff

```sql
UPDATE users SET role = 'Staff' WHERE discord_id = 'YOUR_DISCORD_ID';
```

## API overview

| Endpoint | Description |
|----------|-------------|
| `GET /api/branding` | White-label config |
| `GET /assets/logos/*` | Static logos & banners |
| `GET /api/admin/users` | List users (staff) |
| `GET /api/admin/users/{id}/transactions` | User ledger (staff) |
| `PATCH /api/admin/users/{id}/role` | Set role (admin) |
| `POST /api/users/{id}/balance` | WON adjust (staff) |
| `GET/POST/PATCH/DELETE /api/flights` | Flight CRUD |

## Monorepo layout

```
asiana-ptfs-va/
├── branding.json
├── assets/logos/          # Shared static assets
├── docker-compose.yml
├── .github/workflows/ci.yml
├── frontend/              # Next.js + Dockerfile
├── backend/               # FastAPI + Dockerfile
└── bot/                   # discord.py + Dockerfile (ffmpeg)
```
