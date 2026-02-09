# AI Meeting Automation System
## Self-Hosted Command & Control Platform

**Version**: 1.0.0  
**Status**: In Development  

---

## Overview

A self-hosted, sovereign software appliance for deploying automated agents into video meetings. Think of it as a piece of high-tech military hardware that you control entirely—no external dependencies, no cloud subscriptions.

### Core Capabilities

- 🤖 **Automated Meeting Attendance**: Bot joins Google Meet, Zoom, and Teams as an authenticated user
- 🎭 **Digital Personas**: Manage multiple bot identities with session persistence
- 📊 **Command Center Dashboard**: Web-based control interface for scheduling and monitoring
- 📡 **Live Telemetry**: Real-time streaming of bot status during meetings
- 🛑 **Kill Switch**: Manual override to abort missions instantly
- 🔒 **Air-Gapped Security**: No external API calls except for AI processing (optional)

---

## Project Structure

```
E:\AI Meeter\
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models and session
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   │   ├── bot/        # Bot automation logic
│   │   │   ├── processing/ # Audio/video processing
│   │   │   └── personas/   # Persona management
│   │   └── workers/        # Celery workers
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test suite
│   ├── requirements.txt    # Python dependencies
│   └── main.py             # Application entry point
├── frontend/               # Next.js frontend (temporary)
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── services/       # API client
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Utility functions
│   └── package.json        # Node dependencies
├── docs/                   # Documentation
├── recordings/             # Meeting recordings storage
├── logs/                   # Application logs
├── scripts/                # Utility scripts
├── .env.example            # Environment variables template
└── README.md              # This file
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20 LTS
- PostgreSQL 15+
- Redis
- FFmpeg

**See `docs/Development_Environment_Setup.md` for detailed setup instructions.**

---

### Installation

**1. Clone the repository**
```bash
cd "E:\AI Meeter"
```

**2. Set up backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**3. Configure environment**
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your configuration
# - DATABASE_URL
# - SECRET_KEY
# - ENCRYPTION_KEY
# - OPENAI_API_KEY (optional)
```

**4. Initialize database**
```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE aimeet;
CREATE USER aimeet_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aimeet TO aimeet_user;
\q

# Run migrations (to be created)
alembic upgrade head
```

**5. Start backend server**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**6. Set up frontend (temporary)**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**7. Access the application**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Frontend: http://localhost:3000

---

## Architecture

### Command Center (Dashboard)

- **Auth**: Bcrypt passwords, JWT sessions, admin-only access
- **Personas**: Manage bot identities with encrypted session storage
- **Mission Control**: Schedule meetings, assign personas
- **Live Monitor**: Real-time WebSocket telemetry from bots
- **Kill Switch**: Emergency abort for active missions

### Bot System

- **Playwright Automation**: Headless browser control
- **Session Persistence**: Reuse authenticated sessions via `storageState`
- **Isolated Workers**: Separate process per mission
- **Platform Support**: Google Meet, Zoom, Microsoft Teams

### Processing Pipeline

- **Transcription**: faster-whisper (GPU-accelerated)
- **Diarization**: pyannote.audio (speaker identification)
- **AI Understanding**: GPT-4 extraction (optional)
- **Storage**: PostgreSQL with full-text search

---

## Database Schema

### Core Tables

- `users` - Admin accounts
- `personas` - Bot identities with encrypted sessions
- `missions` - Scheduled meetings
- `meetings` - Completed meetings with transcripts
- `requirements` - Extracted meeting requirements
- `decisions` - Decisions made during meetings
- `action_items` - Tasks assigned during meetings

**See `docs/AI_Meeting_Automation_Master_Documentation.md` for complete schema.**

---

## Development Workflow

### Team Structure

- **Lead Developer**: Critical path (bot logic, integrations)
- **Junior Dev 1**: Backend (database, APIs, testing)
- **Junior Dev 2**: Automation (n8n workflows, frontend)

**See `docs/Team_Development_Plan_Phase1.md` for detailed task breakdown.**

---

### Daily Workflow

1. **9:00 AM**: Daily standup (15 min)
2. **Development**: Work on assigned tasks
3. **5:00 PM**: Create Pull Request
4. **Code Review**: Lead reviews within 24 hours
5. **Weekly Sync**: 1-hour demo and retrospective

---

## Security

- ✅ **Encrypted Session Storage**: AES-256 for persona cookies
- ✅ **No External Dependencies**: Operates fully offline (except AI API)
- ✅ **Local-Only Access**: Dashboard accessible only on local network
- ✅ **Database Encryption**: LUKS/BitLocker for data at rest
- ✅ **Secure Deletion**: Crypto-shred for persona removal

---

## Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
start htmlcov/index.html  # Windows
```

---

## Deployment

**Self-Hosting with Docker** (Coming Soon)

```bash
docker-compose up -d
```

**Manual Deployment**: See `docs/Development_Environment_Setup.md`

---

## Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Loguru**: Structured logging
- **Health Checks**: `/health` endpoint

---

## Documentation

- **Master Documentation**: `docs/AI_Meeting_Automation_Master_Documentation.md`
- **Environment Setup**: `docs/Development_Environment_Setup.md`
- **Team Plan**: `docs/Team_Development_Plan_Phase1.md`

---

## Roadmap

### Phase 1 (8 weeks) - MVP
- ✅ Project structure setup
- ⏳ Backend API development
- ⏳ Persona management system
- ⏳ Google Meet bot automation
- ⏳ Processing pipeline
- ⏳ Basic dashboard

### Phase 2 (8 weeks) - Full Features
- ⏳ Zoom and Teams support
- ⏳ Advanced dashboard UI
- ⏳ Real-time processing
- ⏳ WhatsApp notifications
- ⏳ Prototype generation

### Phase 3 (4 weeks) - Polish
- ⏳ Security hardening
- ⏳ Performance optimization
- ⏳ Docker deployment package
- ⏳ User documentation

---

## License

Proprietary - Internal Use Only

---

## Team

**Lead Developer**: VDK  
**Junior Developer 1**: Backend & Database  
**Junior Developer 2**: Automation & Frontend  

---

## Support

For issues and questions, contact the development team.

**Last Updated**: February 9, 2026
