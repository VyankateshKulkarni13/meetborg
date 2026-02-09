# AI Meeting Automation System
## Development Environment Setup Guide

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Platform**: Windows 11/10  
**Estimated Setup Time**: 1-2 hours

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Core Programming Languages](#core-programming-languages)
4. [Browser Automation](#browser-automation)
5. [Audio/Video Processing](#audiovideo-processing)
6. [AI/ML Tools](#aiml-tools)
7. [Backend Framework](#backend-framework)
8. [Database Tools](#database-tools)
9. [Redis Cache](#redis-cache)
10. [n8n Workflow Automation](#n8n-workflow-automation)
11. [Version Control](#version-control)
12. [Code Editors & IDEs](#code-editors--ides)
13. [API Testing Tools](#api-testing-tools)
14. [Docker & Containerization](#docker--containerization)
15. [Python Environment Management](#python-environment-management)
16. [GPU Support](#gpu-support-optional)
17. [Essential Python Packages](#essential-python-packages)
18. [API Keys & Accounts](#api-keys--accounts)
19. [Project Structure Setup](#project-structure-setup)
20. [Quick Installation Script](#quick-installation-script)
21. [Verification Checklist](#verification-checklist)
22. [Next Steps](#next-steps)
23. [Troubleshooting](#troubleshooting)

---

## Overview

This guide will help you set up a complete development environment for the AI Meeting Automation System on Windows. By the end of this setup, you'll have all the tools needed to build, test, and deploy the system.

**What You'll Install**:
- Python 3.11+ (primary language)
- Node.js 20 LTS (for Playwright)
- PostgreSQL 15+ (database)
- Redis (cache & message broker)
- FFmpeg (audio processing)
- Playwright (browser automation)
- OpenAI Whisper & pyannote.audio (AI models)
- Docker (containerization)
- n8n (workflow automation)

---

## Prerequisites

**System Requirements**:
- Windows 10 or Windows 11 (64-bit)
- 16GB RAM minimum (32GB recommended)
- 100GB+ free disk space
- NVIDIA GPU (optional but recommended for 10x faster processing)
- Stable internet connection

**Administrator Access**: Required for installing some tools

---

## Core Programming Languages

### 1. Python 3.11+

**Primary language for bot and processing modules**

#### Installation

**Method 1: Using winget (Recommended)**
```powershell
winget install Python.Python.3.11
```

**Method 2: Manual Download**
1. Visit: https://www.python.org/downloads/
2. Download Python 3.11.x (latest stable)
3. Run installer
4. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation

#### Verification
```powershell
python --version
# Expected: Python 3.11.x

pip --version
# Expected: pip 23.x or higher
```

#### Upgrade pip
```powershell
python -m pip install --upgrade pip
```

---

### 2. Node.js 20 LTS

**Required for Playwright browser automation**

#### Installation

**Method 1: Using winget**
```powershell
winget install OpenJS.NodeJS.LTS
```

**Method 2: Manual Download**
1. Visit: https://nodejs.org/
2. Download "LTS" version (20.x)
3. Run installer (default options are fine)

#### Verification
```powershell
node --version
# Expected: v20.x.x

npm --version
# Expected: 10.x.x
```

---

## Browser Automation

### 3. Playwright

**Framework for automated browser control**

#### Installation
```powershell
# Install Python package
pip install playwright

# Install browser binaries (Chromium, Firefox, WebKit)
playwright install chromium

# Optional: Install all browsers
playwright install
```

#### Verification
```powershell
playwright --version
# Expected: Version 1.40+
```

#### Stealth Plugin (Bot detection bypass)
```powershell
pip install playwright-stealth
```

---

## Audio/Video Processing

### 4. FFmpeg

**Universal multimedia framework for audio manipulation**

#### Installation

**Method 1: Using winget**
```powershell
winget install Gyan.FFmpeg
```

**Method 2: Using Chocolatey**
```powershell
choco install ffmpeg
```

**Method 3: Manual Download**
1. Visit: https://ffmpeg.org/download.html
2. Download Windows build (full version)
3. Extract to `C:\ffmpeg`
4. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" under System variables
   - Add `C:\ffmpeg\bin`
   - Click OK

#### Verification
```powershell
ffmpeg -version
# Expected: ffmpeg version 5.0+ or higher
```

---

### 5. Python Audio Libraries

```powershell
pip install librosa soundfile
```

**Purpose**:
- `librosa`: Audio analysis and feature extraction
- `soundfile`: Audio file I/O

---

## AI/ML Tools

### 6. OpenAI Whisper (Transcription)

#### faster-whisper (Recommended - 5x faster)
```powershell
pip install faster-whisper
```

#### Standard Whisper (Alternative)
```powershell
pip install openai-whisper
```

**Note**: faster-whisper provides identical accuracy with significantly better performance.

---

### 7. pyannote.audio (Speaker Diarization)

```powershell
pip install pyannote.audio
```

**Requirements**:
- Hugging Face account (free)
- Model license acceptance (see API Keys section)

---

### 8. SentenceTransformers

**For semantic similarity and embeddings**

```powershell
pip install sentence-transformers
```

---

### 9. OpenAI Python Client

**For GPT-4 API access**

```powershell
pip install openai
```

---

## Backend Framework

### 10. FastAPI

**Modern Python API framework**

```powershell
pip install fastapi uvicorn[standard]
```

**Components**:
- `fastapi`: The framework itself
- `uvicorn`: ASGI server for running FastAPI

---

### 11. Celery

**Distributed task queue for background processing**

```powershell
pip install celery
```

**Use Case**: Schedule bot joins, queue processing tasks

---

## Database Tools

### 12. PostgreSQL 15+

**Primary relational database**

#### Installation

**Option 1: Official Installer (Recommended)**
1. Visit: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Download PostgreSQL 15.x for Windows
3. Run installer
4. During installation:
   - Set password for `postgres` superuser (remember this!)
   - Port: Leave as 5432 (default)
   - Locale: Default (English)
   - ✅ Install pgAdmin 4 (GUI tool)
   - ✅ Install Stack Builder (skip for now)

**Option 2: Using winget**
```powershell
winget install PostgreSQL.PostgreSQL
```

#### Verification
```powershell
psql --version
# Expected: psql (PostgreSQL) 15.x
```

#### First-Time Setup
```powershell
# Connect to PostgreSQL (password prompt will appear)
psql -U postgres

# Inside psql, create the project database
CREATE DATABASE aimeet;

# Create a dedicated user (optional but recommended)
CREATE USER aimeet_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aimeet TO aimeet_user;

# Exit
\q
```

---

### 13. DBeaver (GUI Database Client)

**Optional but highly recommended for visual database management**

#### Installation
1. Visit: https://dbeaver.io/download/
2. Download Community Edition (free)
3. Install with default options

**Usage**:
- Connect to PostgreSQL with credentials
- Visual schema design
- Query builder
- Data browsing

---

### 14. Python PostgreSQL Driver

```powershell
pip install psycopg2-binary
```

**Note**: `psycopg2-binary` includes compiled binaries (no need for build tools).

---

## Redis Cache

### 15. Redis

**In-memory database for caching and message broker**

#### Option A: Memurai (Native Windows - Recommended)

1. Visit: https://www.memurai.com/
2. Download Memurai (Redis-compatible for Windows)
3. Install as Windows service
4. Free for development use

**Verification**:
```powershell
memurai-cli ping
# Expected: PONG
```

#### Option B: WSL2 + Redis (Linux-based)

**Install WSL2**:
```powershell
# Enable WSL2
wsl --install

# Restart computer (required)
```

**Install Redis in WSL Ubuntu**:
```powershell
# Enter WSL
wsl

# Inside Ubuntu
sudo apt update
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Test
redis-cli ping
# Expected: PONG

# Exit WSL
exit
```

**Access from Windows**:
- Redis URL: `redis://localhost:6379`

---

### 16. Python Redis Client

```powershell
pip install redis
```

---

## n8n Workflow Automation

### 17. n8n

**Visual workflow automation platform**

#### Option A: n8n Cloud (Easiest - Recommended for MVP)

1. Visit: https://n8n.cloud
2. Sign up for free account
3. No installation needed
4. Access via browser

**Pros**:
- No setup required
- Managed hosting
- Automatic updates

**Cons**:
- Requires internet
- Limited free tier (5 active workflows)

---

#### Option B: Self-Hosted n8n (Docker)

**Prerequisites**: Docker Desktop (see Docker section)

**Run n8n**:
```powershell
docker run -it --rm `
  --name n8n `
  -p 5678:5678 `
  -v ${PWD}/.n8n:/home/node/.n8n `
  n8nio/n8n
```

**Access**: http://localhost:5678

**Persistent Setup** (docker-compose.yml):
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - 5678:5678
    volumes:
      - ./.n8n:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_password
```

**Run**:
```powershell
docker-compose up -d
```

---

## Version Control

### 18. Git

#### Installation

**Method 1: Using winget**
```powershell
winget install Git.Git
```

**Method 2: Manual Download**
1. Visit: https://git-scm.com/download/win
2. Download and install
3. Use default options

#### Configuration
```powershell
git --version
# Expected: git version 2.40+

# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git config --list
```

---

### 19. GitHub Desktop (Optional)

**GUI alternative to command-line Git**

```powershell
winget install GitHub.GitHubDesktop
```

---

## Code Editors & IDEs

### 20. Visual Studio Code

**Recommended code editor**

#### Installation
```powershell
winget install Microsoft.VisualStudioCode
```

#### Essential Extensions

**Install via VS Code Extensions panel**:
1. **Python** (by Microsoft) - Python language support
2. **Pylance** (by Microsoft) - Fast Python IntelliSense
3. **Playwright Test for VSCode** - Playwright debugging
4. **PostgreSQL** (by cweijan) - Database management
5. **Docker** (by Microsoft) - Container management
6. **Markdown All in One** - Documentation editing
7. **GitLens** - Enhanced Git integration
8. **Thunder Client** - API testing (Postman alternative)

#### VS Code Settings for Python

**Create `.vscode/settings.json` in project**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## API Testing Tools

### 21. Postman

**API development and testing**

```powershell
winget install Postman.Postman
```

**Alternative**: Thunder Client (VS Code extension - lightweight)

---

## Docker & Containerization

### 22. Docker Desktop

**Container platform for deployment**

#### Installation
```powershell
winget install Docker.DockerDesktop
```

**Manual Download**: https://www.docker.com/products/docker-desktop/

#### Post-Installation Setup
1. Open Docker Desktop
2. Settings → General → ✅ Use WSL 2 based engine
3. Settings → Resources → Adjust CPU/Memory allocation
4. Restart Docker

#### Verification
```powershell
docker --version
# Expected: Docker version 24.x+

docker-compose --version
# Expected: Docker Compose version v2.x+

# Test run
docker run hello-world
# Expected: Hello from Docker message
```

---

## Python Environment Management

### 23. Virtual Environment (venv)

**Isolate project dependencies**

#### Create Virtual Environment
```powershell
cd "E:\AI Meeter"

# Create venv
python -m venv venv
```

#### Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat

# You'll see (venv) prefix in terminal
```

#### Deactivate
```powershell
deactivate
```

---

### 24. Conda (Alternative)

**If you prefer Anaconda/Miniconda**

```powershell
winget install Anaconda.Miniconda3

# Create environment
conda create -n aimeet python=3.11

# Activate
conda activate aimeet

# Deactivate
conda deactivate
```

---

## GPU Support (Optional)

### 25. NVIDIA CUDA Toolkit

**For 10x faster transcription and AI processing**

#### Check GPU Availability
```powershell
nvidia-smi
# If this works, you have an NVIDIA GPU
```

#### Install CUDA

1. Visit: https://developer.nvidia.com/cuda-downloads
2. Select:
   - OS: Windows
   - Architecture: x86_64
   - Version: Your Windows version
   - Installer Type: exe (local)
3. Download and install CUDA 11.8 or 12.1
4. Restart computer

#### Install cuDNN (Optional, for better performance)
1. Visit: https://developer.nvidia.com/cudnn
2. Sign up for free NVIDIA Developer account
3. Download cuDNN for your CUDA version
4. Extract and copy files to CUDA directory

#### Install PyTorch with CUDA
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Verification
```powershell
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Expected:
# CUDA Available: True
# GPU: NVIDIA GeForce RTX 3060 (or your GPU model)
```

**Performance Impact**:
- CPU-only: 1-hour meeting = 30-40 minutes to transcribe
- With GPU: 1-hour meeting = 3-5 minutes to transcribe

---

## Essential Python Packages

### 26. Install All Dependencies

#### Create requirements.txt

**Create file**: `E:\AI Meeter\requirements.txt`

```
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
celery==5.3.4
redis==5.0.1
python-dotenv==1.0.0
pydantic==2.5.3
python-multipart==0.0.6

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.25

# Browser Automation
playwright==1.41.0
playwright-stealth==1.0.6

# Audio/Video Processing
librosa==0.10.1
soundfile==0.12.1

# AI/ML
faster-whisper==0.10.0
pyannote.audio==3.1.1
sentence-transformers==2.2.2
openai==1.10.0
torch==2.1.2
transformers==4.36.2

# Utilities
requests==2.31.0
httpx==0.26.0
aiohttp==3.9.1
```

#### Install All
```powershell
pip install -r requirements.txt
```

---

## API Keys & Accounts

### 27. OpenAI API

**For GPT-4 access**

#### Setup
1. Visit: https://platform.openai.com/signup
2. Create account (verify email)
3. Go to: https://platform.openai.com/account/billing
4. Add payment method
5. Add $10 credit minimum (unlocks Tier 1 - 200 req/min)
6. Go to: https://platform.openai.com/api-keys
7. Click "Create new secret key"
8. Copy key (starts with `sk-...`)
9. ⚠️ Save securely - it won't be shown again

#### Configure Data Retention
1. Go to: https://platform.openai.com/account/data-controls
2. Enable "Zero Data Retention"
3. This prevents your data from being used for training

#### Cost Management
- Set billing alert at $50/month
- Expected cost: ~$0.25 per meeting

---

### 28. Hugging Face

**For pyannote.audio models**

#### Setup
1. Visit: https://huggingface.co/join
2. Create free account
3. Go to: https://huggingface.co/pyannote/speaker-diarization
4. Click "Accept" on model license
5. Go to: https://huggingface.co/settings/tokens
6. Create "Read" access token
7. Copy token

---

### 29. Bot Accounts

**For meeting attendance**

#### Google Account (for Google Meet)
- Create dedicated Gmail: `aimeet.bot@gmail.com` (or your domain)
- Enable 2FA
- Create app-specific password if needed

#### Microsoft Account (for Teams)
- Create Microsoft account
- Join Azure for Developers (free)

#### Zoom Account
- Sign up for free Zoom account
- Apply for Meeting SDK (free for development)

---

## Project Structure Setup

### 30. Initialize Project

```powershell
cd "E:\AI Meeter"

# Create directory structure
mkdir src, src\bot, src\processing, src\workflows, src\api, tests, recordings, logs

# Create .env file
New-Item -Path ".env" -ItemType File

# Create .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Recordings
recordings/
*.wav
*.webm
*.mp4

# Environment
.env
*.env

# Database
*.db
*.sqlite

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
```

---

### 31. Configure Environment Variables

**Edit `.env` file**:
```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Hugging Face
HUGGINGFACE_TOKEN=hf_your-token-here

# Database
DATABASE_URL=postgresql://aimeet_user:your_password@localhost:5432/aimeet

# Redis
REDIS_URL=redis://localhost:6379

# Bot Credentials
GOOGLE_BOT_EMAIL=aimeet.bot@gmail.com
GOOGLE_BOT_PASSWORD=your_bot_password

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# n8n Webhooks
N8N_WEBHOOK_BASE_URL=https://your-n8n-instance.com/webhook

# Environment
ENVIRONMENT=development
```

**⚠️ Security**: Never commit `.env` to version control!

---

## Quick Installation Script

### 32. Automated Setup

**Create**: `setup.ps1`

```powershell
# AI Meeting Automation - Quick Setup Script
# Run with: .\setup.ps1

Write-Host "`n=== AI Meeting Automation Setup ===" -ForegroundColor Cyan

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install Python packages
Write-Host "`nInstalling Python packages..." -ForegroundColor Green
pip install -r requirements.txt

# Install Playwright browsers
Write-Host "`nInstalling Playwright browsers..." -ForegroundColor Green
playwright install chromium

# Verify installations
Write-Host "`n=== Verification ===" -ForegroundColor Cyan

Write-Host "`nPython:" -ForegroundColor Yellow
python --version

Write-Host "`nNode.js:" -ForegroundColor Yellow
node --version

Write-Host "`nPlaywright:" -ForegroundColor Yellow
playwright --version

Write-Host "`nFFmpeg:" -ForegroundColor Yellow
ffmpeg -version 2>$null | Select-Object -First 1

Write-Host "`nPostgreSQL:" -ForegroundColor Yellow
psql --version

Write-Host "`nDocker:" -ForegroundColor Yellow
docker --version

Write-Host "`nRedis:" -ForegroundColor Yellow
redis-cli ping 2>$null

Write-Host "`n=== GPU Check ===" -ForegroundColor Cyan
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your .env file with API keys"
Write-Host "2. Initialize database: python scripts/init_db.py"
Write-Host "3. Start development server: uvicorn src.api.main:app --reload"
```

**Run**:
```powershell
.\setup.ps1
```

---

## Verification Checklist

### 33. Complete System Check

```powershell
# 1. Python
python --version
pip list

# 2. Node.js
node --version
npm --version

# 3. Playwright
playwright --version
playwright install --list

# 4. FFmpeg
ffmpeg -version

# 5. PostgreSQL
psql --version
psql -U postgres -c "SELECT version();"

# 6. Redis (if WSL)
wsl redis-cli ping

# 7. Docker
docker --version
docker ps

# 8. Git
git --version

# 9. Python packages
python -c "from faster_whisper import WhisperModel; print('Whisper: OK')"
python -c "from pyannote.audio import Pipeline; print('pyannote: OK')"
python -c "import openai; print('OpenAI: OK')"
python -c "from playwright.sync_api import sync_playwright; print('Playwright: OK')"

# 10. GPU (if available)
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

**Expected**: All commands should execute without errors.

---

## Next Steps

### 34. Post-Setup Actions

#### 1. Initialize Git Repository
```powershell
git init
git add .
git commit -m "Initial project setup with development environment"
```

#### 2. Create GitHub Repository (Optional)
```powershell
# On GitHub.com, create new private repository
# Then:
git remote add origin https://github.com/yourusername/ai-meeting-automation.git
git branch -M main
git push -u origin main
```

#### 3. Test Database Connection
```powershell
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:your_password@localhost:5432/aimeet'); print('Database: Connected'); conn.close()"
```

#### 4. Test OpenAI API
```powershell
python -c "import openai; openai.api_key='your-key'; print('OpenAI: Authenticated')"
```

#### 5. Ready to Code!
- Module 1: Meeting Bot (Playwright automation)
- Module 2: Processing Pipeline (Whisper + pyannote)
- Module 3: n8n Workflows (LLM extraction)
- Module 4: Post-Meeting Automation

---

## Troubleshooting

### Common Issues

#### Issue 1: `python` command not found
**Solution**: 
- Reinstall Python with "Add to PATH" checked
- Or manually add to PATH: `C:\Users\YourUser\AppData\Local\Programs\Python\Python311`

#### Issue 2: `playwright install` fails
**Solution**:
```powershell
# Run as administrator
playwright install --with-deps chromium
```

#### Issue 3: FFmpeg not found
**Solution**:
- Verify PATH contains FFmpeg bin directory
- Restart terminal after PATH change

#### Issue 4: PostgreSQL connection refused
**Solution**:
```powershell
# Check if service is running
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-15
```

#### Issue 5: CUDA not detected
**Solution**:
- Update NVIDIA drivers
- Reinstall CUDA toolkit
- Verify environment variables (CUDA_PATH)

#### Issue 6: Redis connection failed (WSL)
**Solution**:
```powershell
wsl
sudo service redis-server start
exit
```

#### Issue 7: pip install fails with "dependency conflict"
**Solution**:
```powershell
# Create fresh virtual environment
rmdir venv -Recurse
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Support Resources

**Documentation**:
- Python: https://docs.python.org/3/
- Playwright: https://playwright.dev/python/
- FastAPI: https://fastapi.tiangolo.com/
- PostgreSQL: https://www.postgresql.org/docs/

**Community**:
- Stack Overflow: Tag questions with relevant technology
- Discord: Join AI/ML and FastAPI communities

**Project-Specific**:
- GitHub Issues: Report bugs or request features
- Team Slack: #aimeet-dev channel

---

## Document History

- **v1.0** (Feb 7, 2026): Initial release

**Maintained by**: VDK Development Team  
**Last Review**: February 7, 2026
