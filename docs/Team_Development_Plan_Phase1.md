# AI Meeting Automation System
## Team Development Plan - Phase 1 (MVP)

**Team Structure**: 3 Developers  
**Timeline**: 8 weeks (56 days)  
**Goal**: Working MVP with Google Meet bot, transcription, and basic AI extraction  

---

## Team Composition

**Lead Developer (You)**:
- Overall architecture decisions
- Complex integration work
- Code review and quality assurance
- Team coordination and blockers resolution
- Critical path items

**Junior Developer 1 (Dev 1)**:
- Database schema implementation
- API endpoint development
- Testing and documentation
- Support tasks

**Junior Developer 2 (Dev 2)**:
- n8n workflow creation
- Email integration
- UI components (if needed)
- Testing and documentation

---

## Phase 1 Breakdown (8 Weeks)

### Week 1: Foundation Setup

#### Lead Developer Tasks (5 days)
**Priority**: Critical Path

**Day 1-2: Project Architecture Setup**
- ✅ Initialize Git repository with proper structure
- ✅ Create base FastAPI application skeleton
- ✅ Set up Docker Compose for local development
- ✅ Configure CI/CD pipeline basics (GitHub Actions)
- ✅ Create development, staging, production environment configs

**Day 3-4: Core Bot Framework**
- ✅ Design bot orchestration system architecture
- ✅ Implement Playwright wrapper with error handling
- ✅ Create meeting join/leave state machine
- ✅ Build recording capture foundation
- ✅ Test with simple Google Meet join (no recording yet)

**Day 5: Integration Setup**
- ✅ Set up Redis connection and Celery workers
- ✅ Create task queue infrastructure
- ✅ Implement basic API endpoint for bot scheduling
- ✅ Code review junior developers' work from Week 1

**Deliverable**: Working FastAPI server, bot can join Google Meet

---

#### Junior Developer 1 Tasks (5 days)

**Day 1-2: Database Setup**
- ✅ Install and configure PostgreSQL locally
- ✅ Create `meetings` table schema (SQL)
- ✅ Create `requirements` table schema
- ✅ Create `action_items` table schema
- ✅ Create `decisions` table schema
- ✅ Add indexes and foreign keys
- ✅ Write schema initialization script (`init_db.py`)

**Day 3-4: Database Models & ORM**
- ✅ Create SQLAlchemy models for all tables
- ✅ Implement database connection pooling
- ✅ Write CRUD operations (Create, Read, Update, Delete) for `meetings`
- ✅ Write unit tests for database operations
- ✅ Create sample data insertion script for testing

**Day 5: API Endpoints (Prep Work)**
- ✅ Create API route structure (`/api/v1/meetings`, `/api/v1/bot`)
- ✅ Implement GET `/meetings/{id}` endpoint
- ✅ Implement GET `/meetings` (list with filters)
- ✅ Write API documentation (docstrings)

**Deliverable**: Working database with all tables, basic API endpoints

---

#### Junior Developer 2 Tasks (5 days)

**Day 1-2: n8n Installation & Learning**
- ✅ Set up n8n (cloud account OR local Docker)
- ✅ Complete n8n tutorial (official docs)
- ✅ Understand workflow concepts (nodes, webhooks, credentials)
- ✅ Test sample workflow (webhook → email)

**Day 3-4: Email Integration Setup**
- ✅ Create SMTP email account (Gmail or SendGrid)
- ✅ Configure email credentials in n8n
- ✅ Create simple email template for meeting summary
- ✅ Build test workflow: webhook → format data → send email
- ✅ Test with sample meeting data

**Day 5: OpenAI Integration Prep**
- ✅ Create OpenAI API account
- ✅ Get API key and configure in n8n
- ✅ Test simple OpenAI node (basic prompt)
- ✅ Understand token management and costs
- ✅ Document n8n setup process for team

**Deliverable**: n8n working, can send emails, OpenAI connection tested

---

### Week 2: Core Bot Implementation

#### Lead Developer Tasks (5 days)

**Day 1-2: Google Meet Bot Logic**
- ✅ Implement Google account authentication (persistent session)
- ✅ Build Meet-specific join flow (handle waiting room, permissions)
- ✅ Add participant detection and meeting state monitoring
- ✅ Implement graceful exit logic (detect meeting end)

**Day 3-4: Recording Capture**
- ✅ Implement Playwright `recordVideo` integration
- ✅ Add audio extraction from WebM to WAV
- ✅ Create FFmpeg processing pipeline (normalize to 16kHz)
- ✅ Implement file storage with organized directory structure
- ✅ Add recording metadata (timestamp, duration, participants)

**Day 5: Bot Reliability**
- ✅ Add retry logic for failed joins
- ✅ Implement timeout handling (max wait 10 minutes)
- ✅ Create bot health monitoring (heartbeat)
- ✅ Test concurrent bot sessions (2-3 simultaneous)
- ✅ Code review week 2 work

**Deliverable**: Bot can join, record, and save Google Meet with high reliability

---

#### Junior Developer 1 Tasks (5 days)

**Day 1-2: Meeting Storage API**
- ✅ Create POST `/bot/schedule` endpoint (trigger bot)
- ✅ Create POST `/bot/join-now` endpoint
- ✅ Create GET `/bot/status/{meeting_id}` endpoint
- ✅ Implement request validation (Pydantic models)
- ✅ Add error responses (4xx, 5xx handling)

**Day 3-4: Celery Task Integration**
- ✅ Create Celery task for bot join (`join_meeting.py`)
- ✅ Implement task status tracking
- ✅ Add task result storage (success/failure logs)
- ✅ Create task cancellation endpoint
- ✅ Test task queue with multiple meetings

**Day 5: Database Extensions**
- ✅ Add `bot_sessions` table (track join/leave times)
- ✅ Add `processing_logs` table (track pipeline stages)
- ✅ Implement cascade deletes (if meeting deleted, remove all children)
- ✅ Write migration script for schema changes

**Deliverable**: Complete API for bot control, Celery integration working

---

#### Junior Developer 2 Tasks (5 days)

**Day 1-3: Email Template Design**
- ✅ Design professional HTML email template (meeting summary)
- ✅ Create template variables (client_name, meeting_title, summary)
- ✅ Add action items section to template
- ✅ Create "Next Steps" section
- ✅ Test email rendering on Gmail, Outlook

**Day 4-5: n8n Workflow V1 (Simple)**
- ✅ Create workflow: Webhook (receive meeting data) → Format → Send Email
- ✅ Test with sample JSON payload
- ✅ Add error handling (if email fails, log to file)
- ✅ Document workflow design (screenshot + explanation)

**Deliverable**: Professional email template, working n8n workflow

---

### Week 3-4: Processing Pipeline

#### Lead Developer Tasks (10 days)

**Day 1-3: Whisper Integration**
- ✅ Install and configure faster-whisper
- ✅ Implement transcription service (`transcribe.py`)
- ✅ Add GPU detection and fallback to CPU
- ✅ Implement chunking for long meetings (>2 hours)
- ✅ Add progress tracking and logging
- ✅ Test with 10+ sample recordings (different lengths, quality)

**Day 4-6: Speaker Diarization**
- ✅ Install and configure pyannote.audio
- ✅ Implement diarization service (`diarize.py`)
- ✅ Build alignment logic (merge diarization with transcript)
- ✅ Handle edge cases (overlapping speakers, silence)
- ✅ Add confidence scoring
- ✅ Test accuracy on sample meetings

**Day 7-8: Pipeline Orchestration**
- ✅ Create processing pipeline coordinator
- ✅ Implement stage progression (record → preprocess → transcribe → diarize)
- ✅ Add stage status updates to database
- ✅ Implement error recovery (retry failed stages)
- ✅ Create processing webhook (trigger from bot completion)

**Day 9-10: Optimization & Testing**
- ✅ Profile performance bottlenecks
- ✅ Optimize for speed (parallel processing where possible)
- ✅ End-to-end test: Join meeting → Record → Process → Output transcript
- ✅ Code review weeks 3-4 work from juniors

**Deliverable**: Complete processing pipeline, transcript with speaker labels

---

#### Junior Developer 1 Tasks (10 days)

**Day 1-3: Transcript Storage**
- ✅ Create transcript storage schema (JSONB for raw, TEXT for cleaned)
- ✅ Implement transcript CRUD operations
- ✅ Add full-text search index on transcript
- ✅ Create search endpoint GET `/meetings/search?q={query}`
- ✅ Test search performance with sample data

**Day 4-6: Processing Status Tracking**
- ✅ Create processing status enum (pending, transcribing, diarizing, complete, failed)
- ✅ Add status update endpoints
- ✅ Implement SSE (Server-Sent Events) for real-time status updates
- ✅ Create status dashboard API endpoint
- ✅ Write frontend mock to test SSE

**Day 7-10: Testing & Documentation**
- ✅ Write integration tests (API → Database)
- ✅ Write unit tests for all CRUD operations
- ✅ Create API documentation with Swagger/OpenAPI
- ✅ Write database schema documentation
- ✅ Create sample API usage guide (curl examples)

**Deliverable**: Complete database layer with tests, API documentation

---

#### Junior Developer 2 Tasks (10 days)

**Day 1-5: n8n Extraction Workflow**
- ✅ Design prompt for GPT-4 (extract requirements, decisions, action items)
- ✅ Create n8n workflow: Webhook → OpenAI (extraction) → Format JSON → Return
- ✅ Add prompt templates (system + user prompts)
- ✅ Implement JSON validation (check required fields)
- ✅ Test with 5+ sample transcripts, iterate on prompt
- ✅ Measure accuracy (manually verify extractions)

**Day 6-8: n8n Notes Generation Workflow**
- ✅ Create workflow: Webhook → OpenAI (generate notes) → Return Markdown
- ✅ Design markdown template structure
- ✅ Test notes quality with sample transcripts
- ✅ Add executive summary generation
- ✅ Ensure consistent formatting

**Day 9-10: Workflow Integration**
- ✅ Chain workflows (Extraction → Notes Generation → Email)
- ✅ Add error handling between workflows
- ✅ Create master orchestration workflow (one entry point)
- ✅ Test end-to-end: Transcript → Extracted data → Notes → Email sent
- ✅ Document all workflows with screenshots

**Deliverable**: Complete n8n workflow chain, automated email delivery

---

### Week 5-6: AI Understanding & Storage

#### Lead Developer Tasks (10 days)

**Day 1-3: LLM Prompt Engineering**
- ✅ Refine extraction prompts based on accuracy testing
- ✅ Add few-shot examples to prompts (improve consistency)
- ✅ Implement prompt versioning (track which prompt used)
- ✅ Create confidence scoring logic
- ✅ Add hallucination detection (cross-reference with transcript)

**Day 4-6: n8n Storage Workflow Integration**
- ✅ Review Junior Dev 2's storage workflow
- ✅ Optimize database insert performance (batch operations)
- ✅ Add transaction management (all-or-nothing inserts)
- ✅ Implement upsert logic (handle duplicate meeting IDs)
- ✅ Test with large datasets (100+ meetings)

**Day 7-8: End-to-End Integration**
- ✅ Connect bot → processing → n8n workflows → database
- ✅ Test complete flow: Schedule meeting → Bot joins → Process → Extract → Store → Email
- ✅ Measure total time (should be <20 minutes)
- ✅ Fix integration bugs

**Day 9-10: Performance Tuning**
- ✅ Profile entire pipeline (find slowest stages)
- ✅ Optimize database queries
- ✅ Add caching where beneficial (Redis)
- ✅ Test with 10 concurrent meetings
- ✅ Code review all week 5-6 work

**Deliverable**: Fully integrated system, end-to-end working

---

#### Junior Developer 1 Tasks (10 days)

**Day 1-4: Data Storage Workflow (n8n - Python hybrid)**
- ✅ Work with Junior Dev 2 to design storage workflow
- ✅ Create Python script callable from n8n (`store_meeting.py`)
- ✅ Implement batch insert logic for requirements, action items, etc.
- ✅ Add validation (ensure foreign keys exist)
- ✅ Test with n8n webhook trigger

**Day 5-7: API Enhancements**
- ✅ Create GET `/action-items?assignee={name}` endpoint
- ✅ Create GET `/requirements?meeting_id={id}` endpoint
- ✅ Add filtering, sorting, pagination to list endpoints
- ✅ Implement export endpoint (JSON/CSV download)

**Day 8-10: Testing & Bug Fixes**
- ✅ Write end-to-end tests (simulate full meeting flow)
- ✅ Test error scenarios (database down, API timeout)
- ✅ Fix bugs discovered during integration testing
- ✅ Update API documentation with new endpoints

**Deliverable**: Robust storage layer, comprehensive API

---

#### Junior Developer 2 Tasks (10 days)

**Day 1-5: n8n Storage Workflow**
- ✅ Create workflow: Webhook (complete meeting object) → Postgres inserts
- ✅ Insert into `meetings` table first, get ID
- ✅ Batch insert requirements, decisions, action_items, etc.
- ✅ Handle empty arrays (no requirements = skip insert)
- ✅ Add error logging (if insert fails, log to file)
- ✅ Test with 20+ sample meeting objects

**Day 6-8: Master Orchestration Workflow**
- ✅ Create master workflow that calls all sub-workflows
- ✅ Entry point: Webhook (receives transcript + metadata)
- ✅ Call Extraction → Notes Generation → Storage → Email
- ✅ Add parallel processing where possible
- ✅ Implement error recovery (if one step fails, log and continue)

**Day 9-10: Monitoring & Logging**
- ✅ Add n8n execution logging
- ✅ Create workflow to send daily summary email (executions, errors)
- ✅ Set up alerts for workflow failures (email notification)
- ✅ Document troubleshooting guide for n8n

**Deliverable**: Complete n8n orchestration, monitoring in place

---

### Week 7: Testing & Refinement

#### Lead Developer Tasks (5 days)

**Day 1-2: System Testing**
- ✅ Run 20+ end-to-end tests with real meetings
- ✅ Test edge cases (very short meetings, very long meetings, poor audio)
- ✅ Measure accuracy (manually review 10 extractions)
- ✅ Identify and prioritize bugs

**Day 3-4: Bug Fixes & Optimization**
- ✅ Fix critical bugs discovered
- ✅ Optimize slow operations
- ✅ Improve error messages
- ✅ Refactor code for maintainability

**Day 5: Code Review & Documentation**
- ✅ Final code review of entire codebase
- ✅ Ensure all code is commented
- ✅ Update README with setup instructions
- ✅ Create architecture diagram

**Deliverable**: Stable, tested system

---

#### Junior Developer 1 Tasks (5 days)

**Day 1-3: Unit & Integration Tests**
- ✅ Achieve 80%+ code coverage
- ✅ Write tests for all API endpoints
- ✅ Write tests for database operations
- ✅ Write tests for Celery tasks
- ✅ Set up CI to run tests automatically

**Day 4-5: API Documentation**
- ✅ Complete Swagger/OpenAPI documentation
- ✅ Add usage examples for each endpoint
- ✅ Create Postman collection
- ✅ Write API quickstart guide

**Deliverable**: Comprehensive test suite, complete API docs

---

#### Junior Developer 2 Tasks (5 days)

**Day 1-3: n8n Workflow Testing**
- ✅ Test all workflows with varied inputs
- ✅ Test error handling (simulate API failures)
- ✅ Measure token usage and costs
- ✅ Optimize prompts to reduce tokens

**Day 4-5: User Documentation**
- ✅ Create n8n workflow guide (how to use, modify)
- ✅ Document email template customization
- ✅ Create troubleshooting FAQ
- ✅ Record video walkthrough of system

**Deliverable**: Complete n8n documentation, user guides

---

### Week 8: Deployment & Launch Prep

#### Lead Developer Tasks (5 days)

**Day 1-2: Deployment Setup**
- ✅ Configure production server (cloud VM)
- ✅ Set up Docker containers for services
- ✅ Configure reverse proxy (Nginx)
- ✅ Set up SSL certificates (HTTPS)
- ✅ Configure environment variables

**Day 3: Database Migration**
- ✅ Export development database
- ✅ Set up production PostgreSQL (managed service)
- ✅ Run migration scripts
- ✅ Test database connections

**Day 4: Launch Preparation**
- ✅ Run final smoke tests on production
- ✅ Set up monitoring (Prometheus + Grafana)
- ✅ Configure alerting (email/Slack on errors)
- ✅ Create incident response plan

**Day 5: Handoff & Training**
- ✅ Train team on operations
- ✅ Create runbook (how to handle common issues)
- ✅ Final demo to stakeholders
- ✅ Document next steps for Phase 2

**Deliverable**: Production system live and monitored

---

#### Junior Developer 1 Tasks (5 days)

**Day 1-2: Deployment Assistance**
- ✅ Help with database setup
- ✅ Verify API endpoints in production
- ✅ Run integration tests on production
- ✅ Fix any deployment issues

**Day 3-4: Monitoring Setup**
- ✅ Configure database monitoring
- ✅ Set up API request logging
- ✅ Create dashboard for key metrics
- ✅ Test alerting system

**Day 5: Documentation**
- ✅ Create deployment guide (step-by-step)
- ✅ Document server architecture
- ✅ Create backup/restore procedures

**Deliverable**: Production database, monitoring

---

#### Junior Developer 2 Tasks (5 days)

**Day 1-2: n8n Production Setup**
- ✅ Migrate workflows to production n8n instance
- ✅ Update webhook URLs
- ✅ Test all workflows in production
- ✅ Verify email delivery

**Day 3-4: Final Testing**
- ✅ Conduct user acceptance testing
- ✅ Test with real client meeting
- ✅ Gather feedback
- ✅ Make final adjustments

**Day 5: Launch Support**
- ✅ Monitor first production meetings
- ✅ Be on-call for issues
- ✅ Document lessons learned

**Deliverable**: Production workflows, launch support

---

## Daily Development Workflow

### Morning Standup (15 minutes)
**Time**: 9:00 AM daily

**Format**:
1. Each developer shares:
   - What I did yesterday
   - What I'm doing today
   - Any blockers

2. Lead developer:
   - Resolves blockers
   - Adjusts priorities if needed
   - Assigns new tasks

---

### Code Review Process

**Frequency**: End of each day or before merging to main

**Process**:
1. Developer creates Git branch (`feature/bot-join-logic`)
2. Commits code with clear messages
3. Creates Pull Request on GitHub
4. Lead reviews within 24 hours
5. Feedback addressed
6. Merge to main

**Quality Standards**:
- Code must have comments
- Functions must have docstrings
- No hardcoded values (use config/env)
- Tests must pass
- No breaking changes without discussion

---

### Communication Channels

**Slack/Discord**:
- #general: Team announcements
- #dev: Technical discussions
- #bugs: Bug reports
- #random: Off-topic

**Weekly Sync** (1 hour):
- Review week's progress
- Demo completed features
- Plan next week
- Retrospective (what went well, what to improve)

---

## Task Assignment Summary

### Lead Developer Focus Areas
✅ **Critical Path**: Bot logic, recording, pipeline orchestration  
✅ **Architecture**: System design, integration points  
✅ **Quality**: Code review, debugging complex issues  
✅ **Leadership**: Unblock team, make technical decisions  

**Skills Developed**: System architecture, team leadership, performance optimization

---

### Junior Developer 1 Focus Areas
✅ **Backend**: Database, APIs, Celery tasks  
✅ **Testing**: Unit tests, integration tests  
✅ **Documentation**: API docs, deployment guides  

**Skills Developed**: Backend development, database design, API design, testing

---

### Junior Developer 2 Focus Areas
✅ **Automation**: n8n workflows, LLM integration  
✅ **Communication**: Email templates, notifications  
✅ **Documentation**: User guides, workflow documentation  

**Skills Developed**: Workflow automation, no-code tools, prompt engineering, user-facing documentation

---

## Success Metrics (End of Phase 1)

**Technical**:
- ✅ Bot joins Google Meet: >95% success rate
- ✅ Recording captures: >98% success
- ✅ Transcription accuracy: <5% WER
- ✅ Extraction accuracy: >85% (manual review)
- ✅ Total processing time: <20 minutes per 1-hour meeting
- ✅ System uptime: >99%

**Team**:
- ✅ All developers can work independently
- ✅ Code review turnaround: <24 hours
- ✅ Zero critical bugs in production after Week 8
- ✅ Documentation complete and usable

---

## Risk Mitigation

**Risk 1**: Lead developer becomes bottleneck
- **Mitigation**: Junior developers escalate blockers early, use async communication (comments in code, PR descriptions)

**Risk 2**: Junior developers stuck on unfamiliar tech
- **Mitigation**: Lead provides "office hours" (dedicated help time daily), pair programming sessions

**Risk 3**: Integration issues between modules
- **Mitigation**: Weekly integration testing, clear API contracts, frequent communication

**Risk 4**: Scope creep
- **Mitigation**: Strict MVP definition, "Phase 2" list for nice-to-have features, lead approves all new features

---

## Phase 1 Completion Checklist

**Week 8 Exit Criteria**:
- ✅ Bot can join and record Google Meet
- ✅ Recordings are transcribed with speaker labels
- ✅ GPT-4 extracts requirements, decisions, action items
- ✅ Data stored in PostgreSQL
- ✅ Professional email sent to client
- ✅ System deployed to production
- ✅ Monitoring and alerting configured
- ✅ All documentation complete
- ✅ Team trained on operations

**If YES to all**: Phase 1 complete! 🎉  
**If NO**: Identify gaps, extend timeline, prioritize

---

## Next Steps After Phase 1

**Phase 2 Goals** (Weeks 9-16):
- Add Zoom and Teams support
- Implement real-time processing
- Add WhatsApp notifications
- Build client/team dashboards
- Prototype generation workflow

---

## Document Control

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Owner**: Lead Developer (VDK)  
**Review Frequency**: Weekly during Phase 1
