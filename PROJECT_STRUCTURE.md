# Project Structure Guide

## Directory Overview

```
E:\AI Meeter\
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   │
│   │   ├── api/                     # API layer
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py           # API router aggregator
│   │   │       └── endpoints/       # Individual endpoint routers
│   │   │           ├── auth.py      # Authentication endpoints
│   │   │           ├── personas.py  # Persona management
│   │   │           ├── missions.py  # Mission scheduling & control
│   │   │           ├── meetings.py  # Meeting data retrieval
│   │   │           └── websocket.py # WebSocket telemetry
│   │   │
│   │   ├── core/                    # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Settings management
│   │   │   ├── security.py          # Auth utilities (JWT, hashing)
│   │   │   └── encryption.py        # Session encryption
│   │   │
│   │   ├── db/                      # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # SQLAlchemy base & mixins
│   │   │   └── session.py           # Async session factory
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # Admin users
│   │   │   ├── persona.py           # Bot identities
│   │   │   ├── mission.py           # Scheduled missions
│   │   │   ├── meeting.py           # Meeting records
│   │   │   ├── requirement.py
│   │   │   ├── decision.py
│   │   │   └── action_item.py
│   │   │
│   │   ├── schemas/                 # Pydantic models (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── persona.py
│   │   │   ├── mission.py
│   │   │   ├── meeting.py
│   │   │   └── token.py
│   │   │
│   │   ├── services/                # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── bot/                 # Bot automation services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── playwright_bot.py      # Browser automation
│   │   │   │   ├── google_meet.py         # Google Meet specific
│   │   │   │   ├── zoom.py                # Zoom specific
│   │   │   │   ├── teams.py               # Teams specific
│   │   │   │   └── session_manager.py     # Session health checks
│   │   │   │
│   │   │   ├── processing/          # Audio/video processing
│   │   │   │   ├── __init__.py
│   │   │   │   ├── transcription.py       # Whisper integration
│   │   │   │   ├── diarization.py         # pyannote.audio
│   │   │   │   └── pipeline.py            # Processing orchestration
│   │   │   │
│   │   │   └── personas/            # Persona management
│   │   │       ├── __init__.py
│   │   │       ├── crud.py                # CRUD operations
│   │   │       └── health_check.py        # Session validation
│   │   │
│   │   └── workers/                 # Celery background tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py        # Celery configuration
│   │       ├── bot_tasks.py         # Bot join/leave tasks
│   │       └── processing_tasks.py  # Transcription/processing
│   │
│   ├── alembic/                     # Database migrations
│   │   ├── versions/                # Migration scripts
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── tests/                       # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── test_api/
│   │   ├── test_models/
│   │   └── test_services/
│   │
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # Next.js React frontend
│   ├── public/                      # Static assets
│   │   ├── favicon.ico
│   │   └── logo.png
│   │
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Layout.tsx           # Main layout wrapper
│   │   │   ├── Navbar.tsx
│   │   │   ├── PersonaCard.tsx
│   │   │   ├── MissionCard.tsx
│   │   │   ├── LiveTerminal.tsx     # Real-time telemetry
│   │   │   └── KillSwitch.tsx
│   │   │
│   │   ├── pages/                   # Next.js pages
│   │   │   ├── index.tsx            # Dashboard overview
│   │   │   ├── login.tsx            # Authentication
│   │   │   ├── personas/
│   │   │   │   ├── index.tsx        # Persona list
│   │   │   │   └── new.tsx          # Create persona
│   │   │   ├── missions/
│   │   │   │   ├── index.tsx        # Mission list
│   │   │   │   ├── new.tsx          # Schedule mission
│   │   │   │   └── [id].tsx         # Mission detail
│   │   │   └── meetings/
│   │   │       ├── index.tsx        # Meeting history
│   │   │       └── [id].tsx         # Meeting detail
│   │   │
│   │   ├── services/                # API client
│   │   │   ├── api.ts               # Axios configuration
│   │   │   ├── auth.ts              # Auth API calls
│   │   │   ├── personas.ts
│   │   │   ├── missions.ts
│   │   │   ├── meetings.ts
│   │   │   └── websocket.ts         # WebSocket client
│   │   │
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── usePersonas.ts
│   │   │
│   │   ├── utils/                   # Utility functions
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   │
│   │   └── styles/                  # CSS/Tailwind
│   │       └── globals.css
│   │
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docs/                            # Documentation
│   ├── AI_Meeting_Automation_Master_Documentation.md
│   ├── Development_Environment_Setup.md
│   ├── Team_Development_Plan_Phase1.md
│   └── ... (other architecture docs)
│
├── recordings/                      # Meeting recordings (gitignored)
│   └── {year}/{month}/{meeting_id}/
│       ├── recording.webm
│       ├── audio.wav
│       └── metadata.json
│
├── logs/                            # Application logs (gitignored)
│   ├── app.log
│   ├── bot.log
│   └── celery.log
│
├── scripts/                         # Utility scripts
│   ├── init_db.py                   # Database initialization
│   ├── create_admin.py              # Create first admin user
│   └── health_check.py              # System health check
│
├── .env.example                     # Environment variables template
├── .env                             # Actual env vars (gitignored)
├── .gitignore                       # Git ignore rules
├── README.md                        # Project overview
├── PROJECT_STRUCTURE.md             # This file
└── docker-compose.yml               # Docker setup (to be created)
```

---

## File Naming Conventions

### Python (Backend)
- **Modules**: `snake_case.py` (e.g., `google_meet.py`)
- **Classes**: `PascalCase` (e.g., `class PlaywrightBot`)
- **Functions**: `snake_case` (e.g., `def join_meeting()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CONCURRENT_BOTS`)

### TypeScript/React (Frontend)
- **Components**: `PascalCase.tsx` (e.g., `PersonaCard.tsx`)
- **Pages**: `kebab-case.tsx` OR `[id].tsx` (dynamic routes)
- **Utilities**: `camelCase.ts` (e.g., `formatDate.ts`)
- **Hooks**: `useCamelCase.ts` (e.g., `useAuth.ts`)

---

## Key Architectural Patterns

### Backend (FastAPI)

**Layered Architecture**:
1. **API Layer** (`api/v1/endpoints/`) - HTTP request/response handling
2. **Service Layer** (`services/`) - Business logic
3. **Data Layer** (`models/`, `db/`) - Database access

**Dependency Injection**:
```python
# In endpoints
async def get_missions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ...
```

**Repository Pattern** (optional):
- CRUD operations in `services/{entity}/crud.py`
- Reusable across endpoints

### Frontend (Next.js)

**Component Structure**:
- **Pages**: Route handlers (in `pages/`)
- **Components**: Reusable UI (in `components/`)
- **Services**: API communication (in `services/`)
- **Hooks**: Shared state logic (in `hooks/`)

**State Management**: Zustand (lightweight alternative to Redux)

---

## Development Guidelines

### Adding a New Feature

**Example: Add "Mission Tags" feature**

1. **Update Models** (`backend/app/models/mission.py`):
   ```python
   class Mission(Base, TimestampMixin):
       tags = Column(ARRAY(String), default=[])
   ```

2. **Create Migration** (`alembic`):
   ```bash
   alembic revision -m "Add tags to missions"
   alembic upgrade head
   ```

3. **Update Schemas** (`backend/app/schemas/mission.py`):
   ```python
   class MissionCreate(BaseModel):
       tags: list[str] = []
   ```

4. **Update Service** (`backend/app/services/missions/crud.py`):
   ```python
   async def create_mission(..., tags: list[str]):
       ...
   ```

5. **Update API** (`backend/app/api/v1/endpoints/missions.py`):
   ```python
   @router.post("/")
   async def create_mission(mission: MissionCreate, ...):
       ...
   ```

6. **Update Frontend** (`frontend/src/pages/missions/new.tsx`):
   ```tsx
   <TagInput value={tags} onChange={setTags} />
   ```

---

## Testing Strategy

### Backend Tests

**Structure**:
```
tests/
├── test_api/               # Endpoint tests
│   └── test_missions.py
├── test_models/            # Model validation
│   └── test_mission.py
└── test_services/          # Business logic
    └── test_bot_service.py
```

**Example Test**:
```python
@pytest.mark.asyncio
async def test_create_mission(client, test_user):
    response = await client.post(
        "/api/v1/missions",
        json={"meeting_url": "https://meet.google.com/abc"}
    )
    assert response.status_code == 201
```

---

## Environment Setup

**Required `.env` variables** (see `.env.example`):

**Critical**:
- `SECRET_KEY` - JWT signing
- `DATABASE_URL` - PostgreSQL connection
- `ENCRYPTION_KEY` - Session cookie encryption

**Optional**:
- `OPENAI_API_KEY` - For LLM extraction
- `N8N_WEBHOOK_BASE_URL` - For workflow integration

---

## Common Tasks

### Start Development Servers

**Backend**:
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev
```

**Celery Workers**:
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

**Redis** (if using WSL):
```bash
wsl sudo service redis-server start
```

### Database Operations

**Create Migration**:
```bash
alembic revision -m "Description of changes"
```

**Apply Migrations**:
```bash
alembic upgrade head
```

**Rollback**:
```bash
alembic downgrade -1
```

### Run Tests

**All tests**:
```bash
pytest
```

**Specific test**:
```bash
pytest tests/test_api/test_missions.py
```

**With coverage**:
```bash
pytest --cov=app --cov-report=html
```

---

## Next Steps

1. ✅ Project structure created
2. ⏳ Implement database models
3. ⏳ Create API endpoints
4. ⏳ Build bot services
5. ⏳ Develop frontend components

**See `docs/Team_Development_Plan_Phase1.md` for detailed task breakdown.**

---

**Last Updated**: February 9, 2026
