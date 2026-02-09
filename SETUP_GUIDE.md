# AI Meeting Automation - Quick Setup Guide

## Backend Setup

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install Playwright
```bash
playwright install chromium
```

### 4. Configure Environment
```bash
# Copy example env file
copy ..\.env.example ..\.env

# Edit .env and set:
# - SECRET_KEY=your-random-secret-key-here
# - ENCRYPTION_KEY=another-random-key-here
# - DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aimeet
```

### 5. Setup Database
```bash
# Using psql
psql -U postgres

# Inside psql:
CREATE DATABASE aimeet;
\q
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

## Running the Application

### Terminal 1 - Backend
```bash
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Access the Application

1. **Open browser**: http://localhost:3000
2. **First time**: You'll be prompted to create an admin account
3. **After registration**: You'll be automatically logged in and redirected to the dashboard

## Test the API

Visit: http://localhost:8000/api/docs

You'll see:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- GET /api/v1/auth/check-first-user

## Troubleshooting

**Issue**: Database connection error
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env

**Issue**: Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check browser console for errors

**Issue**: Module not found errors
- Make sure both venv is activated (backend)
- Make sure npm install completed (frontend)
