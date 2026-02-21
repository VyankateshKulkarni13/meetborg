# MeetBorg — Complete Setup Guide

## Prerequisites

| Tool | Purpose | Download |
|---|---|---|
| **Git** | Clone the repo | [git-scm.com](https://git-scm.com) |
| **Docker Desktop** | Runs Postgres, Redis, Frontend | [docker.com/get-started](https://www.docker.com/get-started) |
| **Python 3.11+** | Runs the backend locally | [python.org](https://www.python.org/downloads/) |
| **Google Chrome** | Browser automation (Zoom/Teams/Meet) | Already installed? ✅ |

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/VyankateshKulkarni13/meetborg.git
cd meetborg
```

---

## Step 2 — Configure Environment

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set at minimum:
```env
SECRET_KEY=<generate a random 32-char string>
DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/aimeet
REDIS_URL=redis://localhost:6379/0
```

> Everything else is optional for basic usage.

---

## Step 3 — Start Docker Services (Postgres + Redis + Frontend)

**First, open Docker Desktop and wait for it to fully start (whale icon stops animating).**

Then:
```bash
docker compose up -d
```

Expected output:
```
✔ postgres   Started
✔ redis      Started
✔ frontend   Started
```

Frontend will be available at → **http://localhost:3000**

---

## Step 4 — Set Up Python Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt
```

---

## Step 5 — Install Playwright Browser

The bot needs a real Chrome browser to automate meetings:

```bash
playwright install chrome
```

---

## Step 6 — Start the Backend

```bash
# (inside backend/ with venv activated)
uvicorn app.main:app --reload
```

Backend will be at → **http://localhost:8000**  
API docs at → **http://localhost:8000/api/docs**

---

## Step 7 — Create Admin User

On **first run only**, create a login account:

```bash
# (inside backend/ with venv activated)
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def create():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@meetborg.local',
            hashed_password=get_password_hash('admin123'),
            is_active=True
        )
        db.add(user)
        await db.commit()
        print('✅ Admin user created!')

asyncio.run(create())
"
```

Login with: **username:** `admin` / **password:** `admin123`

---

## Step 8 — Open the App

Go to **http://localhost:3000**, log in, and add your first meeting!

---

## Daily Usage (After First Setup)

```bash
# 1. Start Docker services
docker compose up -d

# 2. Start backend (in /backend with venv active)
uvicorn app.main:app --reload
```

That's it. Open **http://localhost:3000**.

---

## Common Commands

| Task | Command |
|---|---|
| Start all services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| View container logs | `docker compose logs -f` |
| Rebuild frontend after code changes | `docker compose build frontend && docker compose up -d frontend` |
| Full reset (wipe DB) | `docker compose down -v` |

---

## Troubleshooting

**"Docker Desktop not running"**
→ Open Docker Desktop, wait for whale icon to stop animating

**"Cannot connect to database"**
→ Run `docker compose up -d` first, then start backend

**"playwright: chrome not found"**
→ Run `playwright install chrome` inside the venv

**Frontend shows API errors**
→ Make sure backend is running on port 8000
