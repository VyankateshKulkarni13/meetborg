# AI Meeting Automation System
## Master Production Documentation

**Version**: 1.0  
**Last Updated**: February 7, 2026  
**Document Type**: Complete System Reference  
**Status**: Production Ready  
**Owner**: VDK Development Team

---

## Executive Summary

The AI Meeting Automation System is an end-to-end solution that transforms unstructured client meetings into actionable deliverables through intelligent automation. The system eliminates 90% of manual post-meeting work by automatically recording meetings, extracting requirements, generating documentation, communicating with clients, and initiating prototype development.

### Business Value Proposition

**Problem Solved**: Manual meeting follow-up consumes 2-4 hours per client meeting  
**Solution**: Fully automated pipeline from meeting attendance to prototype delivery  
**Time Savings**: 30+ hours per week for teams handling 10+ client meetings  
**Cost Efficiency**: $70/month operational cost vs $1000+/month for human assistant  
**Quality Improvement**: Consistent documentation, zero missed action items, instant follow-up

### System Capabilities

1. **Autonomous Meeting Attendance**: Bot joins Google Meet, Zoom, and Microsoft Teams automatically
2. **Complete Meeting Capture**: High-fidelity audio/video recording with 16kHz audio quality
3. **AI-Powered Understanding**: Extracts requirements, decisions, action items, and sentiment with 90%+ accuracy
4. **Professional Documentation**: Generates meeting notes, summaries, and structured reports
5. **Client Communication**: Automated email/WhatsApp follow-ups with personalized content
6. **Team Orchestration**: Internal progress tracking and task assignment
7. **Prototype Generation**: AI-generated UI mockups and initial codebase from requirements
8. **Knowledge Management**: Searchable database of all meetings and decisions

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Modules](#core-modules)
3. [Technology Stack](#technology-stack)
4. [Data Architecture](#data-architecture)
5. [Integration Framework](#integration-framework)
6. [Security & Compliance](#security--compliance)
7. [Deployment Architecture](#deployment-architecture)
8. [Operational Procedures](#operational-procedures)
9. [Development Roadmap](#development-roadmap)
10. [Cost Analysis](#cost-analysis)
11. [Success Metrics](#success-metrics)
12. [Appendices](#appendices)

---

## 1. System Architecture

### 1.1 High-Level Architecture

The system consists of 4 primary modules operating in sequence:

```
┌─────────────────────────────────────────────────────────┐
│ MODULE 1: MEETING CAPTURE (AI Bot)                      │
├─────────────────────────────────────────────────────────┤
│ • Bot joins video conference as participant             │
│ • Records audio/video with metadata                     │
│ • Monitors meeting lifecycle                            │
│ • Outputs: Raw recording file + metadata                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ MODULE 2: PROCESSING PIPELINE                           │
├─────────────────────────────────────────────────────────┤
│ • Transcribes audio to text (Whisper)                   │
│ • Identifies speakers (pyannote.audio)                  │
│ • Enhances transcript quality                           │
│ • Outputs: Transcript with speaker labels               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ MODULE 3: AI UNDERSTANDING (n8n Workflows)              │
├─────────────────────────────────────────────────────────┤
│ • Extracts structured information (GPT-4)               │
│ • Generates meeting notes and summaries                 │
│ • Stores data in PostgreSQL database                    │
│ • Outputs: Complete meeting object                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ MODULE 4: POST-MEETING AUTOMATION                       │
├─────────────────────────────────────────────────────────┤
│ • Sends client communications (email/WhatsApp)          │
│ • Generates prototype UI mockups                        │
│ • Tracks team progress (5-phase system)                 │
│ • Monitors and sends reminders                          │
│ • Outputs: Delivered prototypes + tracked tasks         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 End-to-End Process Flow

**Trigger**: Meeting scheduled in calendar OR manual API trigger

**Step 1: Pre-Meeting (T-2 minutes)**
- System detects scheduled meeting
- Bot authentication verified
- Browser/SDK session initialized
- Meeting metadata created in database

**Step 2: Meeting Join (T=0)**
- Bot navigates to meeting URL
- Handles platform-specific join flow (Meet/Zoom/Teams)
- Displays transparent bot identity
- Starts audio/video capture

**Step 3: Recording Phase (Duration: Variable)**
- Continuous recording to local storage
- Real-time monitoring of participant count
- Detection of meeting end signals
- Graceful exit when meeting concludes

**Step 4: Post-Meeting Processing (5-10 minutes)**
- Audio normalization and noise reduction
- Transcription using faster-whisper
- Speaker diarization and alignment
- Transcript enhancement and paragraph segmentation

**Step 5: AI Understanding (1-2 minutes)**
- GPT-4 analyzes transcript via n8n workflow
- Extracts requirements, decisions, action items, timeline
- Generates professional markdown notes
- Stores structured data to PostgreSQL

**Step 6: Automated Follow-Up (Immediate)**
- Client receives email with meeting summary
- WhatsApp confirmation with action items
- Internal team dashboard updated
- Prototype generation triggered (if applicable)

**Step 7: Ongoing Monitoring (Days/Weeks)**
- Client response tracking
- Team progress monitoring across 5 phases
- Automated reminders on delays
- Status reporting to stakeholders

**Total Time**: Meeting duration + 15-20 minutes processing

---

## 2. Core Modules

### 2.1 Module 1: Meeting Capture (AI Bot)

**Purpose**: Autonomous meeting attendance and recording

#### 2.1.1 Bot Identity

**Display Name**: "AI Meeting Assistant (Recording)" or customizable  
**Avatar**: Corporate logo or bot icon  
**Transparency**: Clearly indicates automated recording  
**Permissions**: Muted microphone, optional camera off

#### 2.1.2 Platform Support

**Google Meet**
- Join Method: Browser automation via Playwright
- Authentication: OAuth 2.0 with persistent session
- Challenges: Waiting room approval, dynamic UI selectors
- Reliability: 95% success rate with retry logic

**Zoom**
- Join Method: Browser automation OR Meeting SDK
- Authentication: Meeting ID + password parsing
- Challenges: Host approval required, web vs desktop client
- Reliability: 98% success rate (SDK approach)

**Microsoft Teams**
- Join Method: Browser automation OR Bot Framework
- Authentication: Azure AD or guest join
- Challenges: Lobby system, browser compatibility
- Reliability: 93% success rate

#### 2.1.3 Recording Strategy

**Audio Capture**
- Method: Playwright recordVideo (simple) OR WebRTC streaming (real-time)
- Format: WebM with OPUS codec during capture
- Sample Rate: 48kHz native, downsampled to 16kHz post-capture
- Channels: Mono (mixed) or stereo preserved

**Video Capture** (Optional)
- Resolution: 1280x720 maximum
- Frame Rate: 15 fps (sufficient for recordings)
- Purpose: Visual context, screen sharing capture
- Storage: Separate from audio for processing efficiency

**Storage Location**
- Path Structure: `/recordings/{year}/{month}/{meeting_id}/`
- Files: `recording.webm`, `metadata.json`, `participants.json`
- Retention: 2 years default, configurable per client SLA

#### 2.1.4 Meeting Lifecycle Management

**Join Detection**
- Monitor for "Joined successfully" indicators
- Verify participant list visibility
- Confirm audio stream active
- Timeout: 10 minutes maximum wait

**Exit Detection**
- Host ends meeting signal
- Only bot remaining (2-minute grace period)
- Maximum duration reached (8 hours hard limit)
- Audio silence for 15 minutes
- Manual termination via API

#### 2.1.5 Concurrency Handling

**Simultaneous Meetings**
- Maximum: 3 concurrent bots per server
- Isolation: Separate browser contexts
- Queue: Additional requests queued with FIFO
- Resource Allocation: 2GB RAM, 1 CPU core per bot

**Load Balancing** (Future)
- Multiple bot servers (horizontal scaling)
- Meeting distribution via load balancer
- Shared database for coordination

---

### 2.2 Module 2: Processing Pipeline

**Purpose**: Transform raw audio into structured, understood transcript

#### 2.2.1 Audio Preprocessing

**Noise Reduction**
- Tool Options: RNNoise (AI-based) OR FFmpeg filters
- Target: Remove HVAC, keyboard clicks, background chatter
- Quality Metric: SNR >20dB acceptable
- Processing Time: ~5 seconds per hour of audio

**Normalization**
- Goal: Consistent volume across speakers and time
- Method: FFmpeg loudnorm filter
- Output: -16 LUFS target loudness

**Format Standardization**
- Target Format: WAV PCM 16-bit
- Sample Rate: 16kHz (optimal for Whisper)
- Channels: Mono (mixed from stereo if needed)
- Command: `ffmpeg -i input.webm -ar 16000 -ac 1 -c:a pcm_s16le output.wav`

#### 2.2.2 Transcription Engine

**Technology**: OpenAI Whisper (faster-whisper implementation)

**Model Selection**
- Development: medium.en (769MB, 2x realtime speed)
- Production: medium.en OR large-v3 (accuracy-critical use cases)
- Real-time: tiny OR base (streaming scenarios)

**Configuration**
- Device: CUDA GPU (10x faster) OR CPU (fallback)
- Beam Size: 5 (balance speed/accuracy)
- VAD Filter: Enabled (skip silence)
- Word Timestamps: Enabled (required for diarization alignment)

**Output Format**
```json
{
  "language": "en",
  "duration": 3600,
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello everyone, thanks for joining.",
      "words": [
        {"word": "Hello", "start": 0.0, "end": 0.3, "probability": 0.98}
      ]
    }
  ]
}
```

**Performance Characteristics**
- Speed: 2x realtime (30 minutes to transcribe 1-hour meeting)
- Accuracy: <5% Word Error Rate (WER) on clear audio
- Language Detection: Automatic with 99%+ accuracy
- Cost: Free (self-hosted)

#### 2.2.3 Speaker Diarization

**Technology**: pyannote.audio

**Process**
1. Analyze audio waveform for speaker regions
2. Assign temporary labels (SPEAKER_00, SPEAKER_01, etc.)
3. Output segments with start/end timestamps
4. Align segments with transcription timestamps

**Speaker Name Inference** (Optional)
- Contextual clues: "I'm John" in transcript
- Voice enrollment: Pre-recorded voice samples (future)
- LLM inference: Ask GPT-4 to infer based on conversation context
- Manual override: UI for user confirmation

**Alignment Algorithm**
- For each transcript segment, find overlapping speaker segment
- Assign speaker with maximum overlap duration
- Handle speaker changes mid-sentence gracefully

**Output Format**
```json
[
  {"start": 0.0, "end": 5.2, "speaker": "VDK"},
  {"start": 5.3, "end": 12.1, "speaker": "Client"}
]
```

#### 2.2.4 Transcript Enhancement

**Punctuation Restoration**
- Tool: deepmultilingualpunctuation (transformer-based)
- Purpose: Add missing commas, periods, question marks
- Accuracy: 95%+ on formal speech

**Filler Word Removal**
- Target Words: um, uh, like, you know, sort of
- Strategy: Preserve in raw transcript, remove in cleaned version
- Regex Pattern: `\b(um|uh|like|you know|sort of|kind of)\b`

**Paragraph Segmentation**
- Method: Sentence embedding similarity (SentenceTransformers)
- Threshold: 0.7 cosine similarity = same topic
- Result: Logical paragraph breaks for readability

**Final Output**
- Raw Transcript: With speaker labels, timestamps, all words
- Cleaned Transcript: Enhanced readability, paragraph structure
- JSON Format: Structured with metadata for database storage

---

### 2.3 Module 3: AI Understanding (n8n Workflows)

**Purpose**: Extract actionable intelligence from transcript using LLM

#### 2.3.1 Architecture Overview

**Workflow Engine**: n8n (visual automation platform)

**Three Independent Workflows**:
1. **Extraction Workflow**: Analyzes transcript, returns structured JSON
2. **Notes Generation Workflow**: Creates professional meeting documentation
3. **Storage Workflow**: Persists data to PostgreSQL database

**Integration Pattern**: Sequential webhook calls (Extraction → Notes → Storage)

#### 2.3.2 Workflow 1: Information Extraction

**Input**: Meeting transcript (JSON with speaker labels and timestamps)

**LLM**: OpenAI GPT-4 Turbo
- Model: `gpt-4-turbo`
- Temperature: 0.3 (consistent, less creative)
- Max Tokens: 4000
- Response Format: JSON Object (enforced)

**Extraction Categories**:

1. **Summary**
   - Executive Summary: 2-3 sentences
   - Detailed Summary: 5-7 sentences
   - Key Takeaways: Bullet points

2. **Requirements**
   - Text: Specific requirement description
   - Category: Design, Feature, Integration, Infrastructure
   - Priority: Critical, High, Medium, Low
   - Confidence: 0-100 score
   - Quote: Supporting excerpt from transcript
   - Timestamp: When mentioned in meeting

3. **Decisions**
   - Text: Decision made
   - Made By: Person who decided
   - Agreed By: List of people who concurred
   - Quote: Supporting excerpt
   - Timestamp: When decided

4. **Action Items**
   - Task: Clear description of to-do
   - Assignee: Person responsible
   - Deadline: Target completion date (if mentioned)
   - Priority: Urgency level
   - Dependencies: Related tasks (if any)

5. **Timeline**
   - Milestones: Key project events
   - Target Dates: When milestones should occur
   - Duration Estimates: Time estimates mentioned

6. **Discussion Points**
   - List of main topics covered

7. **Questions Raised**
   - Question text
   - Asked by: Person who raised it
   - Answered: Boolean (was it resolved?)
   - Answer: If resolved, the answer given

8. **Sentiment Analysis**
   - Overall: Positive, Neutral, or Negative
   - Justification: Why this sentiment
   - Satisfaction Score: 0-10 (client satisfaction)
   - Concerns: Any worries expressed

**Validation Logic**:
- Check all required fields present
- Verify data types correct
- Remove duplicate items (using embedding similarity)
- Cross-reference quotes exist in transcript
- Assign confidence scores based on quote clarity

**Output**: Complete JSON object with all extracted information

**Processing Time**: 30-45 seconds per meeting

#### 2.3.3 Workflow 2: Notes Generation

**Input**: Extracted JSON from Workflow 1

**LLM**: OpenAI GPT-4 Turbo
- Temperature: 0.4 (slightly more creative for readability)
- Max Tokens: 3000

**Generated Artifacts**:

1. **Professional Meeting Notes** (Markdown format)
   - Header: Meeting title, date, client, participants, duration
   - Executive Summary section
   - Key Discussion Points (bullet list)
   - Requirements & Specifications (organized by priority)
   - Decisions Made (numbered list with decision maker)
   - Action Items (formatted table with columns: Task, Assignee, Deadline, Priority)
   - Timeline & Milestones (chronological list)
   - Questions & Concerns (bullet list)
   - Next Steps section
   - Footer: Generated timestamp, system version

2. **Executive Summary**
   - Purpose: Quick read for stakeholders
   - Length: 2-3 sentences
   - Content: Meeting objective, key outcome, next steps

3. **Detailed Summary**
   - Purpose: Comprehensive overview
   - Length: 5-7 sentences
   - Content: Full context, all major topics, decisions, timeline

**Template Structure** (Markdown):
```
# Meeting Notes: {title}

**Date**: {date}  
**Client**: {client_name}  
**Participants**: {participant_list}  
**Duration**: {duration}

## Executive Summary
{executive_summary}

## Key Discussion Points
- {point_1}
- {point_2}

## Requirements & Specifications
### Critical Priority
- {requirement}

## Decisions Made
1. {decision} - Decided by {person}

## Action Items
| Task | Assignee | Deadline | Priority |
|------|----------|----------|----------|
| {task} | {person} | {date} | {priority} |

## Timeline & Milestones
- **{milestone}** - {target_date}

## Questions & Concerns
- {question}

## Next Steps
{next_meeting_date}
```

**Output**: Complete meeting object with notes, summaries, and all extracted data

**Processing Time**: 20-30 seconds

#### 2.3.4 Workflow 3: Data Storage

**Input**: Complete meeting object from Workflow 2

**Database**: PostgreSQL 14+

**Tables** (7 total):

1. **meetings** (Primary table)
   - Columns: meeting_id (PK), title, client_name, meeting_date, duration, platform, transcript_raw, transcript_cleaned, notes_markdown, executive_summary, detailed_summary, sentiment, satisfaction_score, processing_metadata, created_at, updated_at
   - Indexes: meeting_id, client_name, meeting_date
   - Purpose: Core meeting record with all text content

2. **requirements** (Child table)
   - Columns: id (PK), meeting_id (FK), requirement_text, category, priority, confidence, quote, timestamp
   - Indexes: meeting_id, priority, category
   - Purpose: Track product/project requirements

3. **decisions** (Child table)
   - Columns: id (PK), meeting_id (FK), decision_text, made_by, agreed_by, quote, timestamp
   - Indexes: meeting_id
   - Purpose: Track key decisions

4. **action_items** (Child table)
   - Columns: id (PK), meeting_id (FK), task, assignee, deadline, priority, status, dependencies
   - Indexes: meeting_id, assignee, deadline, status
   - Purpose: Task tracking and assignment

5. **timelines** (Child table)
   - Columns: id (PK), meeting_id (FK), milestone, target_date, duration_estimate
   - Indexes: meeting_id, target_date
   - Purpose: Project milestone tracking

6. **discussion_points** (Child table)
   - Columns: id (PK), meeting_id (FK), topic
   - Indexes: meeting_id
   - Purpose: Topic coverage tracking

7. **questions_raised** (Child table)
   - Columns: id (PK), meeting_id (FK), question, asked_by, answered, answer
   - Indexes: meeting_id, answered
   - Purpose: Track unresolved questions

**Data Persistence Logic**:
- Insert meeting record first
- Use returned meeting_id for all child records
- Batch insert child records for efficiency
- Handle empty arrays gracefully (skip insert)
- Use UPSERT (ON CONFLICT UPDATE) for idempotency

**Output**: Confirmation JSON with database IDs and record counts

**Processing Time**: 5-10 seconds

#### 2.3.5 Error Handling and Retry Logic

**OpenAI API Failures**
- Retry: 3 attempts with exponential backoff (2s, 4s, 8s)
- Fallback: Use GPT-3.5 Turbo if GPT-4 unavailable
- Timeout: 60 seconds per request

**Database Failures**
- Retry: 2 attempts
- Transaction Rollback: Ensure no partial data
- Error Logging: Store failed requests for manual review

**Validation Failures**
- Log invalid extractions
- Return partial data with warning flags
- Notify operator for manual intervention

---

### 2.4 Module 4: Post-Meeting Automation

**Purpose**: Automated client communication, prototype generation, and team tracking

#### 2.4.1 Client Communication System

**Channels**:
1. **Email**: Primary method for detailed updates
2. **WhatsApp**: Secondary for quick confirmations and reminders

**Email Communication**

**Template 1: Initial Meeting Summary** (Sent immediately after processing)
- Subject: "Meeting Summary - {meeting_title}"
- Body Content:
  - Greeting with client name
  - Executive summary
  - Key discussion points (bullet list)
  - Next steps and deadlines
  - Action items requiring client input
  - Link to full meeting notes (if shared)
  - Contact information for questions

**Template 2: Action Item Reminder** (Sent 24 hours before deadline)
- Subject: "Reminder: {action_item} due tomorrow"
- Body Content:
  - Friendly reminder
  - Action item description
  - Original deadline
  - Call-to-action

**Template 3: Milestone Update** (Sent when team reaches project phase)
- Subject: "Project Update - {milestone_name}"
- Body Content:
  - Progress summary
  - Completed work
  - Next phase preview
  - Timeline confirmation

**Email Tool**: SMTP integration (Gmail, SendGrid, or custom)

**WhatsApp Communication**

**Message 1: Quick Confirmation** (Sent 5 minutes after meeting)
- Text: "Hi {client_name}, thanks for the great meeting! I've sent a detailed summary to your email. Key action on your end: {primary_action}. Let me know if you have questions!"

**Message 2: Deadline Reminder** (Sent day before)
- Text: "Quick reminder - {action_item} is due tomorrow. Let me know if you need more time!"

**WhatsApp Tool**: Twilio WhatsApp API OR WhatsApp Business API

**Personalization Strategy**:
- Use client's first name (extracted from CRM or meeting)
- Reference specific requirements from meeting
- Match communication tone to client (formal vs casual)
- Include relevant links (prototype, documentation)

#### 2.4.2 Prototype Generation Workflow

**Trigger**: When meeting contains UI/design requirements

**Process**:

**Step 1: Requirement Filtering**
- Identify requirements tagged as "Design" or "UI"
- Extract specific features mentioned
- Parse technology preferences (React, dark theme, etc.)

**Step 2: AI Mockup Generation**
- Tool: v0.dev by Vercel OR ChatGPT with DALL-E
- Input: Detailed prompt with requirements
- Output: UI mockup images OR functional code snippet

**Step 3: Code Generation** (Optional)
- Tool: GPT-4 Code Mode OR GitHub Copilot
- Input: Requirements + chosen tech stack
- Output: Initial React/Next.js component structure
- Includes: Routing, basic components, placeholder logic

**Step 4: Repository Setup**
- Create GitHub repository
- Initialize with generated code
- Add README with setup instructions
- Configure as private (client access if needed)

**Step 5: Client Delivery**
- Email prototype link with screenshots
- Provide access credentials (if needed)
- Include "This is a starting point for discussion" disclaimer
- Schedule prototype review meeting

**Timeline**: 2-4 hours automated, ready for designer review

#### 2.4.3 Internal Team Tracking System

**Purpose**: Monitor development progress across 5 phases

**5-Phase Development Model**:

1. **Understanding** (1-2 days)
   - Team reviews meeting notes and requirements
   - Clarifies open questions
   - Confirms technical approach
   - Status: Not Started → In Progress → Complete

2. **Development** (Variable duration)
   - Core implementation work
   - Tracked by milestones from timeline
   - Regular progress updates
   - Status: % Complete (0-100%)

3. **Testing** (10-20% of dev time)
   - QA testing against requirements
   - Bug fixes
   - Performance validation
   - Status: Passed, Failed, In Progress

4. **Finalization** (1-2 days)
   - Final polish
   - Documentation
   - Deployment preparation
   - Status: Ready for Delivery, Blocked

5. **Delivery** (1 day)
   - Client handoff
   - Training (if needed)
   - Feedback collection
   - Status: Delivered, Accepted, Revisions Needed

**Tracking Mechanism**:
- PostgreSQL table: `project_phases`
- Columns: project_id, phase_name, status, start_date, end_date, assignee, blockers
- Updated via API or manual dashboard input

**Dashboard Features**:
- Visual progress bars per phase
- Overdue task highlights
- Team member workload view
- Client-facing status page (optional)

#### 2.4.4 Monitoring and Reminder System

**Client Response Tracking**
- Monitor: Email open rates, reply status
- Timeout: If no response in 48 hours, send gentle reminder
- Escalation: After 5 days, notify project manager

**Team Progress Monitoring**
- Check: Daily progress updates expected
- Alert: If phase exceeds estimated duration by 20%
- Notification: Slack/email to team lead

**Deadline Reminders**
- T-3 days: First reminder to assignee
- T-1 day: Second reminder to assignee + manager
- T+1 day: Overdue alert to all stakeholders

**Implementation**: n8n scheduled workflows (cron-based)

---

## 3. Technology Stack

### 3.1 Complete Technology Inventory

**Bot Infrastructure**
- **Primary Language**: Python 3.10+
- **Framework**: FastAPI (REST API orchestration)
- **Browser Automation**: Playwright (cross-platform)
- **Task Queue**: Celery (background job processing)
- **Message Broker**: Redis (Celery backend)
- **Platform SDKs**: Zoom Meeting SDK (optional)

**Audio/Video Processing**
- **Transcription**: OpenAI Whisper (faster-whisper fork)
- **Diarization**: pyannote.audio 3.1
- **Audio Manipulation**: FFmpeg, librosa
- **Noise Reduction**: RNNoise OR FFmpeg filters

**AI/LLM**
- **Primary LLM**: OpenAI GPT-4 Turbo (via API)
- **Fallback LLM**: GPT-3.5 Turbo (cost optimization)
- **Future Option**: Local Llama 3 70B (self-hosted)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)

**Workflow Automation**
- **Platform**: n8n (cloud or self-hosted)
- **Protocols**: Webhooks (HTTP POST)
- **Scheduling**: Cron-based triggers

**Data Storage**
- **Relational Database**: PostgreSQL 14+
- **Object Storage**: MinIO (S3-compatible) OR filesystem
- **Cache**: Redis (session data, temp storage)

**Communication**
- **Email**: SMTP (Gmail, SendGrid, AWS SES)
- **WhatsApp**: Twilio WhatsApp API
- **Notifications**: Slack webhooks (internal)

**AI Tools** (Prototype Generation)
- **UI Generation**: v0.dev, ChatGPT + DALL-E
- **Code Generation**: GPT-4 Code Interpreter mode
- **Version Control**: GitHub API

**Infrastructure**
- **Container**: Docker (for deployment)
- **Orchestration**: Docker Compose (development) OR Kubernetes (production scale)
- **Monitoring**: Prometheus + Grafana (metrics)
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

### 3.2 Technology Decision Rationale

**Why Python?**
- Native AI/ML library support (Whisper, pyannote, transformers)
- Playwright Python bindings stable and well-documented
- FastAPI provides modern async capabilities
- Ecosystem maturity for automation tasks

**Why n8n over custom code?**
- Visual workflow builder (faster iteration)
- Built-in integrations (OpenAI, PostgreSQL, email)
- No-code friendly (non-developers can maintain)
- Cloud hosting option (reduces devops burden)

**Why PostgreSQL?**
- JSONB support (flexible schema for LLM outputs)
- Full-text search (search transcripts)
- Robust indexing (fast queries on large datasets)
- Free and widely supported

**Why GPT-4 vs local LLM?**
- **MVP**: GPT-4 for reliability and accuracy
- **Long-term**: Migrate to Llama 3 to reduce costs
- Hybrid approach: GPT-4 for complex analysis, Llama 3 for simpler tasks

### 3.3 Version Requirements

| Technology | Minimum Version | Recommended Version | Notes |
|------------|----------------|---------------------|-------|
| Python | 3.10 | 3.11 | For async improvements |
| Node.js | 18 | 20 LTS | For Playwright |
| PostgreSQL | 14 | 15+ | For better JSON performance |
| Redis | 6 | 7+ | For enhanced caching |
| FFmpeg | 4.0 | 5.0+ | For latest codecs |
| Playwright | 1.40 | Latest | For bug fixes |
| n8n | 1.0 | Latest | For new features |

---

## 4. Data Architecture

### 4.1 Database Schema Design

**Design Principles**:
- Normalized structure (avoid data duplication)
- Foreign keys with CASCADE delete (maintain referential integrity)
- UUID primary keys (distributed-system friendly)
- Timezone-aware timestamps (TIMESTAMPTZ)
- Flexible JSONB columns for LLM metadata

### 4.2 Table Specifications

**meetings Table** (Core entity)

Primary Key: `meeting_id UUID`

Key Columns:
- `title TEXT`: Meeting title
- `client_name VARCHAR(255)`: Client organization name
- `meeting_date TIMESTAMPTZ`: When meeting occurred
- `duration_seconds INTEGER`: Length of meeting
- `platform VARCHAR(20)`: google_meet, zoom, teams
- `meeting_url TEXT`: Original meeting link
- `recording_path TEXT`: File path to recording
- `transcript_raw JSONB`: Full transcript with timestamps
- `transcript_cleaned TEXT`: Readable paragraph format
- `notes_markdown TEXT`: Generated meeting notes
- `executive_summary TEXT`: 2-3 sentence summary
- `detailed_summary TEXT`: 5-7 sentence summary
- `sentiment VARCHAR(20)`: positive, neutral, negative
- `satisfaction_score DECIMAL(3,1)`: 0-10 client satisfaction
- `processing_metadata JSONB`: LLM model used, processing time, etc.
- `created_at TIMESTAMPTZ`: Record creation time
- `updated_at TIMESTAMPTZ`: Last modification time

Indexes:
- `idx_meetings_meeting_id` (unique)
- `idx_meetings_client_name`
- `idx_meetings_meeting_date`
- `idx_meetings_sentiment`

**requirements Table** (Extracted requirements)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `requirement_text TEXT`: Description of requirement
- `category VARCHAR(50)`: Design, Feature, Integration, Infrastructure
- `priority VARCHAR(20)`: Critical, High, Medium, Low
- `confidence INTEGER`: 0-100 extraction confidence
- `quote TEXT`: Supporting quote from transcript
- `timestamp DECIMAL(10,2)`: Time in meeting when mentioned

Indexes:
- `idx_requirements_meeting_id`
- `idx_requirements_priority`
- `idx_requirements_category`

**decisions Table** (Key decisions made)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `decision_text TEXT`: What was decided
- `made_by VARCHAR(255)`: Person who made decision
- `agreed_by TEXT[]`: Array of people who agreed
- `quote TEXT`: Supporting quote
- `timestamp DECIMAL(10,2)`: When decided

Indexes:
- `idx_decisions_meeting_id`

**action_items Table** (Tasks and assignments)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `task TEXT`: Task description
- `assignee VARCHAR(255)`: Person responsible
- `deadline DATE`: Target completion date
- `priority VARCHAR(20)`: High, Medium, Low
- `status VARCHAR(20)`: pending, in_progress, completed, blocked
- `dependencies TEXT[]`: Array of related task IDs

Indexes:
- `idx_action_items_meeting_id`
- `idx_action_items_assignee`
- `idx_action_items_deadline`
- `idx_action_items_status`

**timelines Table** (Project milestones)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `milestone VARCHAR(255)`: Milestone name
- `target_date DATE`: When it should occur
- `duration_estimate VARCHAR(100)`: Time estimate (e.g., "4 weeks")

Indexes:
- `idx_timelines_meeting_id`
- `idx_timelines_target_date`

**discussion_points Table** (Topics covered)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `topic TEXT`: Discussion topic

Indexes:
- `idx_discussion_points_meeting_id`

**questions_raised Table** (Unresolved questions)

Primary Key: `id UUID`  
Foreign Key: `meeting_id UUID → meetings.meeting_id (CASCADE)`

Columns:
- `question TEXT`: Question text
- `asked_by VARCHAR(255)`: Who raised it
- `answered BOOLEAN`: Was it resolved?
- `answer TEXT`: Answer if resolved

Indexes:
- `idx_questions_meeting_id`
- `idx_questions_answered`

### 4.3 Data Flows

**Write Flow** (After meeting processing):
1. n8n Storage Workflow receives complete meeting object
2. Insert into `meetings` table, get `meeting_id`
3. Batch insert into child tables with `meeting_id` foreign key
4. Commit transaction (all or nothing)
5. Return confirmation with record counts

**Read Flows**:

**Query 1: Get Complete Meeting**
```sql
SELECT m.*, 
       array_agg(DISTINCT r.*) as requirements,
       array_agg(DISTINCT d.*) as decisions,
       array_agg(DISTINCT a.*) as action_items
FROM meetings m
LEFT JOIN requirements r ON m.meeting_id = r.meeting_id
LEFT JOIN decisions d ON m.meeting_id = d.meeting_id
LEFT JOIN action_items a ON m.meeting_id = a.meeting_id
WHERE m.meeting_id = 'uuid'
GROUP BY m.meeting_id
```

**Query 2: Get All Action Items for Person**
```sql
SELECT a.*, m.title as meeting_title, m.meeting_date
FROM action_items a
JOIN meetings m ON a.meeting_id = m.meeting_id
WHERE a.assignee = 'John Doe'
  AND a.status != 'completed'
ORDER BY a.deadline ASC
```

**Query 3: Search Transcripts**
```sql
SELECT meeting_id, title, client_name, 
       ts_headline('english', transcript_cleaned, query) as excerpt
FROM meetings, 
     to_tsquery('english', 'payment & gateway') query
WHERE to_tsvector('english', transcript_cleaned) @@ query
ORDER BY meeting_date DESC
LIMIT 10
```

### 4.4 Data Retention and Archival

**Retention Policy**:
- **Active Data**: 2 years (readily queryable)
- **Archived Data**: 2-7 years (cold storage, slower access)
- **Deleted Data**: After 7 years OR per client request (GDPR compliance)

**Archival Process**:
- Monthly job identifies meetings older than 2 years
- Export to compressed JSON files
- Move recordings to cold storage (AWS Glacier, Azure Archive)
- Delete from primary database
- Maintain index for retrieval if needed

**Data Size Estimates**:
- Meeting Record: ~50KB (text fields)
- Recording: ~50MB (1-hour audio at 128kbps)
- Total per Meeting: ~50MB
- 1000 Meetings: ~50GB storage

---

## 5. Integration Framework

### 5.1 API Endpoints

**Bot Control API** (FastAPI)

**Base URL**: `https://api.aimeet.com/v1`

**Endpoint 1: Schedule Bot Join**
- Method: `POST /bot/schedule`
- Request:
  ```json
  {
    "meeting_url": "https://meet.google.com/abc-defg",
    "scheduled_time": "2026-02-10T15:00:00Z",
    "title": "Client Discovery Call",
    "client_name": "Acme Corp"
  }
  ```
- Response: `{ "meeting_id": "uuid", "status": "scheduled" }`

**Endpoint 2: Trigger Immediate Join**
- Method: `POST /bot/join-now`
- Request: Same as above
- Response: `{ "meeting_id": "uuid", "status": "joining" }`

**Endpoint 3: Get Meeting Status**
- Method: `GET /bot/status/{meeting_id}`
- Response: `{ "status": "recording", "duration": 1234, "participants": 3 }`

**Endpoint 4: Force Leave**
- Method: `POST /bot/leave/{meeting_id}`
- Response: `{ "status": "left", "recording_saved": true }`

**Processing Pipeline API** (n8n Webhooks)

**Endpoint 5: Extract Information**
- URL: `https://n8n.aimeet.com/webhook/extract`
- Method: `POST`
- Request: `{ "transcript": {...} }`
- Response: Extracted JSON object

**Endpoint 6: Generate Notes**
- URL: `https://n8n.aimeet.com/webhook/generate-notes`
- Method: `POST`
- Request: Extracted data JSON
- Response: Complete meeting object with notes

**Endpoint 7: Store Data**
- URL: `https://n8n.aimeet.com/webhook/store`
- Method: `POST`
- Request: Complete meeting object
- Response: Database confirmation with IDs

**Data Query API** (Direct PostgreSQL OR REST wrapper)

**Endpoint 8: Get Meeting by ID**
- Method: `GET /meetings/{meeting_id}`
- Response: Complete meeting object with all child records

**Endpoint 9: List Meetings**
- Method: `GET /meetings?client={name}&start_date={date}&end_date={date}`
- Response: Array of meeting summaries

**Endpoint 10: Get Action Items**
- Method: `GET /action-items?assignee={name}&status={status}`
- Response: Array of action items

### 5.2 Webhook Events

**Event System**: Publish events for downstream systems

**Event 1: meeting.recorded**
- Payload: `{ "meeting_id": "uuid", "recording_path": "/path/to/file" }`
- Subscribers: Processing Pipeline

**Event 2: meeting.processed**
- Payload: `{ "meeting_id": "uuid", "transcription_complete": true }`
- Subscribers: n8n Extraction Workflow

**Event 3: meeting.understood**
- Payload: `{ "meeting_id": "uuid", "requirements_count": 5 }`
- Subscribers: Client Communication, Team Tracking

**Event 4: action_item.created**
- Payload: `{ "action_item_id": "uuid", "assignee": "John", "deadline": "date" }`
- Subscribers: Notification System

**Event 5: deadline.approaching**
- Payload: `{ "action_item_id": "uuid", "hours_remaining": 24 }`
- Subscribers: Reminder System

**Implementation**: Redis Pub/Sub OR message queue (RabbitMQ)

### 5.3 Third-Party Integrations

**Calendar Integration** (Google Calendar, Outlook)
- Purpose: Auto-detect meetings to join
- Method: OAuth 2.0 access to user calendar
- Trigger: Bot joins meetings with "aimeet" keyword in description

**CRM Integration** (Salesforce, HubSpot, custom)
- Purpose: Link meetings to client records
- Method: Webhook on meeting completion
- Data Flow: Push meeting summary, action items to CRM

**Project Management** (Asana, Jira, Linear)
- Purpose: Auto-create tasks from action items
- Method: API calls from n8n workflow
- Mapping: Action items → Project tasks

**Communication Platforms** (Slack, Microsoft Teams)
- Purpose: Notify team on meeting completion
- Method: Incoming webhooks
- Message: "Meeting with {client} processed. {action_items_count} tasks assigned."

---

## 6. Security & Compliance

### 6.1 Data Security

**Encryption**

**At Rest**:
- Database: PostgreSQL with transparent data encryption (TDE)
- Filesystem: LUKS encryption for recording storage
- Backups: Encrypted with AES-256

**In Transit**:
- All API calls: HTTPS/TLS 1.3
- Database connections: SSL/TLS enforced
- Webhook communications: HTTPS required

**Access Control**

**Authentication**:
- API Keys: For bot control API (rotated monthly)
- OAuth 2.0: For Google/Microsoft integrations
- JWT Tokens: For user authentication (if dashboard exists)

**Authorization**:
- Role-Based Access Control (RBAC)
  - Admin: Full system access
  - Team Member: Read meetings, update tasks
  - Client: Read-only access to their meetings (optional)
- Row-Level Security: Users see only their organization's data

**Secrets Management**:
- API keys stored in environment variables OR secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Bot credentials: Encrypted at rest, decrypted only at runtime
- Database passwords: Never in code, always environment-based

### 6.2 Compliance

**GDPR (General Data Protection Regulation)**

**User Rights**:
- Right to Access: API endpoint for data export
- Right to Deletion: Endpoint to delete all user data
- Right to Portability: JSON export of all meeting data

**Data Processing**:
- Clear consent: Bot announces recording at join
- Purpose limitation: Data used only for stated purposes
- Data minimization: Store only necessary information

**OpenAI Data Retention**:
- Enable "Zero Data Retention" in OpenAI settings
- Data not used for model training
- 30-day maximum retention (as of 2026 OpenAI policy)

**CCPA (California Consumer Privacy Act)**
- Similar to GDPR requirements
- Opt-out option for California residents

**Recording Consent Laws** (Varies by jurisdiction)

**One-Party Consent States** (e.g., New York):
- One participant (the bot) can consent
- Recommended: Still announce recording for transparency

**Two-Party Consent States** (e.g., California):
- All participants must be aware of recording
- Bot sends chat message: "This meeting is being recorded"
- Participants can object and leave

**Enterprise Settings**:
- Some companies require all meetings recorded (company policy)
- Inform participants via meeting invite

### 6.3 Audit Logging

**Events Logged**:
- Bot joins and leaves meeting
- Recording started and stopped
- Data processing initiated
- LLM API calls (model, tokens used)
- Database writes
- User API access (who, when, what)

**Log Storage**:
- Centralized logging system (ELK Stack)
- Retention: 1 year
- Access: Admin only, encrypted

**Compliance Reports**:
- Monthly: Data processing volumes
- Quarterly: Security audit reports
- Annual: GDPR compliance review

---

## 7. Deployment Architecture

### 7.1 Infrastructure Components

**Production Environment**

**Component 1: Bot Server**
- Specs: 8 vCPU, 16GB RAM, 100GB SSD
- OS: Ubuntu 22.04 LTS
- Concurrency: 3 simultaneous bots
- Scaling: Horizontal (add more bot servers)

**Component 2: Processing Server**
- Specs: 4 vCPU, 16GB RAM, 100GB SSD, GPU optional
- Purpose: Whisper transcription, pyannote diarization
- GPU: NVIDIA T4 or better (10x speed improvement)
- Alternative: CPU-only (slower but cheaper)

**Component 3: n8n Instance**
- Option A: n8n Cloud (managed, $20-50/month)
- Option B: Self-hosted VPS (2 vCPU, 4GB RAM)
- Database: SQLite (embedded) OR PostgreSQL

**Component 4: PostgreSQL Database**
- Managed Service: AWS RDS, Digital Ocean, Azure Database
- Specs: db.t3.medium (2 vCPU, 4GB RAM) minimum
- Storage: 100GB SSD (autoscaling enabled)
- Backups: Daily automated, 7-day retention

**Component 5: Object Storage**
- Option A: MinIO (self-hosted S3-compatible)
- Option B: AWS S3, Azure Blob, Digital Ocean Spaces
- Purpose: Recording file storage
- Cost: ~$0.02/GB/month

**Component 6: Redis**
- Purpose: Celery message broker, caching
- Specs: 1GB RAM minimum
- Managed Service: AWS ElastiCache, Redis Labs, Upstash

### 7.2 Network Architecture

```
                        Internet
                           │
                           ▼
                   Load Balancer (Optional)
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Bot Server 1       Bot Server 2       Bot Server 3
   (FastAPI)          (FastAPI)          (FastAPI)
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                    Redis (Celery Queue)
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
Processing Worker 1  Processing Worker 2   n8n Instance
(Whisper+pyannote)   (Whisper+pyannote)   (Workflows)
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                   PostgreSQL Database
                           │
                           ▼
                    Object Storage (S3)
```

**Firewall Rules**:
- Inbound: HTTPS (443), SSH (22) from trusted IPs only
- Outbound: HTTPS (OpenAI API, email, WhatsApp)
- Database: Accessible only from app servers (private subnet)

### 7.3 Deployment Strategies

**Development Environment**
- All components on single machine
- Docker Compose for orchestration
- Local PostgreSQL and Redis
- n8n self-hosted (Docker container)

**Staging Environment**
- Mirrors production (smaller instances)
- Separate database (test data)
- Used for testing new features

**Production Environment**
- Redundant components (multiple bot servers)
- Managed services for database, Redis
- Automated backups and monitoring

**CI/CD Pipeline**
- Code Repository: GitHub
- CI: GitHub Actions
- Tests: Pytest for Python, integration tests for workflows
- Deployment: Docker images pushed to registry, pulled by servers
- Rollback: Keep previous Docker image version

### 7.4 Scaling Strategy

**Vertical Scaling** (Increase server resources):
- Bot Server: Up to 16 vCPU for 10+ concurrent bots
- Processing: Add GPU for faster transcription
- Database: Increase to db.r5.large for high query load

**Horizontal Scaling** (Add more servers):
- Bot Servers: Load balancer distributes meeting join requests
- Processing Workers: Celery workers auto-scale based on queue length
- Database: Read replicas for query-heavy loads

**Auto-Scaling Triggers**:
- CPU usage >70% for 5 minutes → Add server
- Queue length >10 → Add processing worker
- Database connections >80% → Scale database

**Cost Optimization**:
- Use spot instances for processing workers (50% cost savings)
- Archive old recordings to cold storage (90% cheaper)
- Use GPT-3.5 for simple extractions (5x cheaper than GPT-4)

---

## 8. Operational Procedures

### 8.1 Monitoring and Alerting

**Metrics to Monitor**

**Bot Performance**:
- Join success rate (target: >95%)
- Average join time (target: <2 minutes)
- Recording failures (target: <1%)
- Concurrent bot usage

**Processing Performance**:
- Transcription time (target: <2x realtime)
- Extraction accuracy (manual review sample)
- n8n workflow execution time
- OpenAI API response time

**Database Performance**:
- Query speed (target: <100ms)
- Connection pool usage
- Storage usage growth
- Failed transactions

**System Health**:
- CPU usage per server
- Memory usage
- Disk space
- Network bandwidth

**Alerting Rules**:
- Critical: Bot join failure >3 in 1 hour → Immediate notification
- Warning: Database query >500ms → Daily summary
- Info: Successful meeting processed → Log only

**Notification Channels**:
- Email: For daily summaries
- Slack: For real-time alerts
- PagerDuty: For critical issues (on-call rotation)

### 8.2 Maintenance Procedures

**Daily**:
- Review bot join logs for failures
- Check OpenAI API spend (avoid budget overruns)
- Verify database backups completed

**Weekly**:
- Manually review 3-5 extraction outputs for accuracy
- Check disk space on recording storage
- Review error logs for patterns

**Monthly**:
- Update dependencies (security patches)
- Rotate API keys
- Review cost reports and optimize
- Test disaster recovery procedure

**Quarterly**:
- Update LLM prompts based on accuracy feedback
- Review and update documentation
- Conduct security audit
- Performance tuning (optimize slow queries)

### 8.3 Incident Response

**Severity Levels**:
- **P0 (Critical)**: Bot cannot join meetings, database down → Resolve in 1 hour
- **P1 (High)**: Processing delayed, extraction errors → Resolve in 4 hours
- **P2 (Medium)**: Minor feature broken → Resolve in 1 day
- **P3 (Low)**: Enhancement request → Scheduled work

**Response Procedure**:
1. Alert received → Acknowledge within 5 minutes
2. Assess severity → Assign priority
3. Investigate root cause → Check logs, metrics
4. Implement fix → Code change or config update
5. Test fix → Verify in staging
6. Deploy to production → Monitor closely
7. Post-mortem → Document cause and prevention

**Common Issues and Resolutions**:

**Issue 1: Bot Fails to Join Meeting**
- Cause: Platform UI change, authentication expired
- Resolution: Update selectors, re-authenticate bot account
- Prevention: Weekly test join, UI change monitoring

**Issue 2: Transcription Accuracy Low**
- Cause: Poor audio quality, background noise
- Resolution: Improve noise reduction filters, use larger Whisper model
- Prevention: Audio quality checks pre-transcription

**Issue 3: OpenAI API Timeout**
- Cause: Rate limit exceeded, API downtime
- Resolution: Implement retry with backoff, use fallback model
- Prevention: Monitor API usage, stay within tier limits

**Issue 4: Database Connection Pool Exhausted**
- Cause: High query volume, slow queries
- Resolution: Increase pool size, optimize queries, add indexes
- Prevention: Regular query performance review

### 8.4 Backup and Disaster Recovery

**Backup Strategy**:
- **Database**: Daily full backup, hourly incremental
- **Recordings**: Real-time replication to second storage location
- **Configuration**: Version-controlled in Git
- **Secrets**: Encrypted backup in secrets manager

**Backup Retention**:
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

**Recovery Scenarios**:

**Scenario 1: Database Corruption**
- Restore from latest backup (RTO: 15 minutes, RPO: 1 hour)
- Replay logs if available (minimize data loss)

**Scenario 2: Complete Server Failure**
- Provision new server from infrastructure-as-code (Terraform)
- Restore database and configuration
- Resume operations (RTO: 2 hours)

**Scenario 3: Recording File Loss**
- Recover from replicated storage
- If unrecoverable, notify client and re-process if meeting re-recorded

**Testing**:
- Monthly: Test database restore procedure
- Quarterly: Full disaster recovery drill

---

## 9. Development Roadmap

### 9.1 Phase 1: MVP (Weeks 1-8)

**Goals**: Prove core concept with minimal viable system

**Deliverables**:
- Bot joins Google Meet only
- Basic transcription (Whisper)
- Manual extraction (no LLM)
- Simple email notification

**Timeline**: 8 weeks, 1 developer

### 9.2 Phase 2: Automation (Weeks 9-16)

**Goals**: Add AI understanding and n8n workflows

**Deliverables**:
- GPT-4 extraction workflow
- Automated notes generation
- PostgreSQL storage
- Professional email templates

**Timeline**: 8 weeks, 1 developer

### 9.3 Phase 3: Multi-Platform (Weeks 17-22)

**Goals**: Support Zoom and Teams

**Deliverables**:
- Zoom bot implementation
- Teams bot implementation
- Platform detection logic
- Unified recording format

**Timeline**: 6 weeks, 1 developer

### 9.4 Phase 4: Advanced Features (Weeks 23-30)

**Goals**: Add prototype generation and team tracking

**Deliverables**:
- AI prototype generator (v0.dev integration)
- 5-phase tracking system
- Client/team dashboards
- WhatsApp notifications

**Timeline**: 8 weeks, 2 developers

### 9.5 Phase 5: Scale and Polish (Weeks 31-36)

**Goals**: Production hardening and optimization

**Deliverables**:
- Horizontal scaling support
- Monitoring and alerting
- Security audit and fixes
- Performance optimization

**Timeline**: 6 weeks, 2 developers

**Total**: 36 weeks (~9 months) from zero to production-grade system

---

## 10. Cost Analysis

### 10.1 Development Costs

**Labor** (Based on 1-2 developers):
- Phase 1-3: 22 weeks × $5000/week = $110,000 (1 developer)
- Phase 4-5: 14 weeks × $10,000/week = $140,000 (2 developers)
- **Total Development**: $250,000

**Alternative** (If building in-house with existing team):
- Developer time allocation: 50% of 2 developers for 9 months
- Opportunity cost: Depends on what else they would build

### 10.2 Infrastructure Costs (Monthly)

**Cloud Servers**:
- Bot Server (8 vCPU, 16GB): $40
- Processing Server (4 vCPU, 16GB, no GPU): $30
- Processing Server (with GPU): $150 (optional)
- n8n (if self-hosted): $10
- **Subtotal**: $80-$190/month

**Managed Services**:
- PostgreSQL (db.t3.medium): $50
- Redis (1GB): $15
- Object Storage (500GB recordings): $10
- **Subtotal**: $75/month

**Communication**:
- Email (SendGrid): $15 (up to 5000 emails)
- WhatsApp (Twilio): $20 (pay-per-message)
- **Subtotal**: $35/month

**Total Infrastructure**: $190-$300/month

### 10.3 AI/API Costs (Variable)

**Per Meeting**:
- OpenAI GPT-4 Turbo:
  - Extraction: ~5,000 tokens = $0.15
  - Notes Generation: ~3,000 tokens = $0.09
  - Total: ~$0.25 per meeting

**Monthly** (Based on usage):
- 50 meetings/month: $12.50
- 100 meetings/month: $25
- 200 meetings/month: $50

**Cost Optimization**:
- Use GPT-3.5 for simple meetings: Save 80%
- Migrate to local Llama 3: Eliminate API costs (but need GPU server)

### 10.4 Total Cost of Ownership (TCO)

**First Year**:
- Development: $250,000 (one-time)
- Infrastructure: $2,400-$3,600 (monthly × 12)
- AI API: $150-$600 (depends on volume)
- **Total**: ~$253,000-$254,000

**Subsequent Years**:
- Infrastructure: $2,400-$3,600
- AI API: $150-$600
- Maintenance: $20,000-$40,000 (bug fixes, updates)
- **Total**: ~$23,000-$44,000/year

**Break-Even Analysis**:
- If replacing human assistant ($50,000/year): 5-year ROI
- If saving 30 hours/week at $100/hour: $150,000/year → ROI in 2 years

---

## 11. Success Metrics

### 11.1 Technical KPIs

**Reliability**:
- Bot join success rate: >95%
- Recording capture success: >98%
- Transcription accuracy (WER): <5%
- Extraction accuracy: >90%
- System uptime: >99.5%

**Performance**:
- Join time: <2 minutes
- Total processing time: <15 minutes for 1-hour meeting
- API response time: <500ms
- Database query time: <100ms

**Quality**:
- Zero missed action items: 100%
- Client satisfaction with notes: >8/10
- Team usage rate: >80% of eligible meetings

### 11.2 Business KPIs

**Time Savings**:
- Manual meeting follow-up time: 2 hours → 10 minutes (90% reduction)
- Documentation creation time: 30 minutes → 2 minutes (93% reduction)
- **Total**: 30 hours saved per week (for 10 meetings)

**Cost Efficiency**:
- Cost per meeting: ~$3 (infrastructure + API)
- Human alternative: $100 per meeting (2 hours × $50/hour)
- **Savings**: $97 per meeting, $970 per 10 meetings/week

**Client Impact**:
- Meeting follow-up speed: 24 hours → 5 minutes (99% faster)
- Action item tracking: Manual → Automated
- Prototype delivery: 1 week → 1 day (85% faster)

### 11.3 User Satisfaction

**Internal Team**:
- Adoption rate: >80% within 3 months
- User satisfaction: >4/5 stars
- Bug reports: <5 per month
- Feature requests: Tracked and prioritized quarterly

**Clients**:
- Meeting notes quality: >8/10
- Follow-up timeliness: >9/10
- Overall experience: >8/10

---

## 12. Appendices

### 12.1 Glossary

**Terms**:
- **Bot**: Automated software agent that joins meetings
- **Diarization**: Process of identifying "who spoke when" in audio
- **LLM**: Large Language Model (e.g., GPT-4)
- **n8n**: No-code workflow automation platform
- **Playwright**: Browser automation framework
- **Whisper**: OpenAI's speech-to-text model
- **Pipeline**: Series of data processing stages
- **WER**: Word Error Rate (transcription accuracy metric)

### 12.2 Reference Architecture Diagrams

**Diagram 1: System Overview** (Conceptual)
- Shows 4 modules and data flow
- Included in Section 1.1

**Diagram 2: Network Architecture** (Infrastructure)
- Shows servers, databases, load balancers
- Included in Section 7.2

**Diagram 3: Data Schema** (Database ERD)
- Shows 7 tables and relationships
- Described in Section 4

### 12.3 Technology Alternatives Considered

**Bot Automation**:
- ✅ Playwright (chosen): Cross-platform, Python support
- ❌ Puppeteer: Node.js only
- ❌ Selenium: Slower, more fragile

**Transcription**:
- ✅ Whisper (chosen): Best accuracy, free
- ❌ Google Speech-to-Text: Paid, less accurate
- ❌ Azure Speech Services: Paid, vendor lock-in

**LLM**:
- ✅ GPT-4 (chosen for MVP): Best accuracy
- 🔄 Llama 3 (future): Free, private, requires GPU
- ❌ Claude: Expensive, API limitations

**Workflow Automation**:
- ✅ n8n (chosen): Visual, easy integrations
- ❌ Zapier: Expensive for high volume
- ❌ Custom Python: More work, less maintainable

### 12.4 Future Enhancements

**Short-Term** (3-6 months):
- Real-time meeting insights (live dashboard during meeting)
- Voice-based speaker identification
- Multi-language support (Spanish, French)

**Medium-Term** (6-12 months):
- Mobile app for meeting review
- CRM deep integration (Salesforce, HubSpot)
- Advanced analytics (sentiment trends, topic clustering)

**Long-Term** (12+ months):
- AI-generated video summaries
- Predictive project timeline based on past meetings
- Generative AI for contract template creation from requirements

### 12.5 Support and Maintenance

**Documentation**:
- User Guide: How to trigger bot, review meetings
- Administrator Guide: Server setup, troubleshooting
- Developer Guide: Code architecture, contribution guidelines
- API Reference: Complete endpoint documentation

**Training**:
- Onboarding: 2-hour session for team
- Quarterly refreshers: New features, best practices
- Video tutorials: Self-service learning

**Support Channels**:
- Email: support@aimeet.com (24-hour response)
- Slack: #aimeet-support (real-time for urgent)
- Documentation: Wiki with FAQs and troubleshooting

---

## Document Control

**Versioning**:
- Version 1.0: Initial production documentation (Feb 7, 2026)
- Future updates tracked in Git with changelog

**Review Schedule**:
- Quarterly review: Update for new features, tech changes
- Annual comprehensive review: Major revisions if needed

**Ownership**:
- Primary: Technical Lead (VDK)
- Contributors: Development Team
- Approvers: CTO, Product Manager

**Distribution**:
- Internal team: Full access via Git repository
- Stakeholders: Executive summary sections
- Clients: Redacted version (public-facing features only)

---

**END OF DOCUMENT**
