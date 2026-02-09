# Meeting Bot Architecture - God-Level Documentation

## Executive Overview

This architecture focuses on a **single, powerful method**: an **AI Meeting Bot** that joins video conferences (Google Meet, Zoom, Microsoft Teams) as a participant, captures the entire meeting, and extracts all necessary information automatically.

**Core Concept:**
The bot acts like a human attendee - it receives a meeting invite, joins at the scheduled time, listens/records the conversation, and processes the data in real-time or post-meeting.

**Critical Success Factors:**
- **Seamless joining** across 3 major platforms (Meet, Zoom, Teams)
- **Reliable audio capture** with high quality
- **Undetectable/acceptable bot presence** (transparent to participants)
- **Real-time processing** for instant insights
- **100% open-source** - no paid APIs

---

## 1. Bot Identity & Presence Strategy

### 1.1 How the Bot Appears

**Visual Presence:**
- **Display Name:** "AI Meeting Assistant (Recording)" or "VDK's AI Note Taker"
- **Avatar:** Custom logo/icon indicating it's a bot
- **Transparency:** Clear indication it's an automated system (ethical + legal compliance)

**Participant Behavior:**
- **Audio:** Muted by default (bot doesn't speak)
- **Video:** Optional camera off, or static "Recording in progress" image
- **Chat:** Can send acknowledgment message: "AI Assistant has joined and is recording"

**Permission Model:**
- **Explicit Invite:** Bot only joins when meeting link is provided by authorized user (VDK)
- **Host Control:** Meeting host can kick bot if needed
- **Legal Compliance:** Auto-announce recording (varies by jurisdiction)

---

### 1.2 Bot Account Setup (Per Platform)

#### Google Meet
**Account Type:** Standard Google Workspace account
- Email: `aimeet-bot@yourdomain.com` (requires G Suite or regular Gmail)
- Setup: Manual account creation (one-time)
- Authentication: OAuth 2.0 for API access + stored credentials for automated login

**No Official Bot API:** Google Meet doesn't have a public bot API, so we use **browser automation**

#### Zoom
**Account Type:** Zoom Meeting SDK account
- **Free Tier:** Meeting SDK is free for development
- **Bot User:** Create via Zoom Marketplace app
- **Authentication:** JWT or OAuth (SDK provides token)

**Alternative:** Zoom doesn't require accounts for participants - can join with just name

#### Microsoft Teams
**Account Type:** Azure Bot Service registration
- **Free Tier:** Yes, Azure Bot Service has free tier (10k messages/month - irrelevant for our use case)
- **Bot Framework:** Use Microsoft Bot Framework SDK
- **Authentication:** Azure AD app registration

**Alternative:** Browser automation (like Meet)

---

## 2. Meeting Join Mechanisms (Platform-Specific)

### 2.1 Google Meet (Browser Automation)

**Technology:** Playwright (Node.js) or Puppeteer
- **Why:** No official bot API, must simulate browser
- **Advantages:** Full control, works with any meeting
- **Disadvantages:** Resource intensive, fragile to UI changes

**Join Flow:**
```
1. Receive meeting link (e.g., https://meet.google.com/abc-defg-hij)
2. Launch headless Chrome via Playwright
3. Navigate to Google login page
4. Auto-login with bot account credentials
5. Navigate to meeting link
6. Wait for "Ask to join" or "Join now" button
7. Click button
8. Wait for confirmation (joined state)
9. Mute microphone (if not already)
10. Start audio capture from browser tab
```

**Code Approach (High-Level):**
```javascript
// Using Playwright
const { chromium } = require('playwright');

async function joinGoogleMeet(meetingUrl) {
  const browser = await chromium.launch({ headless: false }); // headless: true in prod
  const context = await browser.newContext({
    permissions: ['microphone', 'camera'],
    recordVideo: { dir: './recordings' }
  });
  
  const page = await context.newPage();
  
  // Login
  await page.goto('https://accounts.google.com');
  await page.fill('input[type="email"]', 'aimeet-bot@yourdomain.com');
  await page.click('#identifierNext');
  await page.fill('input[type="password"]', process.env.BOT_PASSWORD);
  await page.click('#passwordNext');
  
  // Join meeting
  await page.goto(meetingUrl);
  await page.waitForSelector('button[aria-label*="Join"]');
  await page.click('button[aria-label*="Join"]');
  
  // Capture audio (see section 3)
  // ...
}
```

**Challenges:**
- **Login CAPTCHA:** Use persistent browser session (stay logged in)
- **UI Changes:** Google updates Meet UI frequently - need selector resilience
- **Waiting Room:** If host hasn't joined, wait up to 10 minutes

---

### 2.2 Zoom (SDK Approach - Recommended)

**Technology:** Zoom Meeting SDK (Official)
- **Documentation:** https://developers.zoom.us/docs/meeting-sdk/
- **Language:** JavaScript (Web SDK) or Python (using zoom-api wrapper)
- **Advantages:** Stable, official support, fewer UI breakages
- **Disadvantages:** Requires Zoom account setup

**Join Flow:**
```
1. Receive Zoom meeting ID + password (from link parsing)
2. Initialize Zoom SDK with credentials
3. Join meeting programmatically
4. Set display name ("AI Meeting Assistant")
5. Mute audio output
6. Capture raw audio stream
```

**Alternative: Browser Automation (Fallback)**
- Similar to Google Meet approach
- Navigate to Zoom web client (doesn't require Zoom app)
- Join as guest with custom name

**Link Parsing:**
```
Input: https://zoom.us/j/1234567890?pwd=abcdef123456
Extract: 
  - Meeting ID: 1234567890
  - Password: abcdef123456
```

---

### 2.3 Microsoft Teams (Bot Framework - Official)

**Technology:** Microsoft Bot Framework + Teams SDK
- **Language:** Python (botbuilder-core) or Node.js (@microsoft/teams-js)
- **Advantages:** Official support, enterprise-ready
- **Disadvantages:** More complex initial setup

**Join Flow:**
```
1. Bot receives meeting invite (via Teams webhook or Graph API)
2. Parse meeting join URL
3. Use Graph API to join meeting on behalf of bot
   - Endpoint: POST /communications/calls/{id}/join
4. Establish media stream
5. Capture audio
```

**Alternative: Browser Automation (Simpler)**
- Use Teams web client (teams.microsoft.com)
- Playwright automation similar to Google Meet

**Recommendation:** Start with browser automation for MVP, migrate to Bot Framework for scale

---

## 3. Audio/Video Capture Strategy

### 3.1 Browser-Based Capture (For Meet/Teams via Playwright)

**Method 1: Built-in Video Recording**
```javascript
const context = await browser.newContext({
  recordVideo: {
    dir: './recordings',
    size: { width: 1280, height: 720 }
  }
});
// Playwright automatically records tab audio + video
// Output: .webm file when context closes
```

**Advantages:**
- Simple, one-line setup
- Captures everything (audio + video)
- No custom streaming logic

**Disadvantages:**
- Recording only saved at end (not real-time)
- Large file sizes
- Can't process audio in real-time

---

**Method 2: Real-time Audio Streaming (Advanced)**

**Approach:** Use Chrome DevTools Protocol (CDP) to capture audio
```javascript
const client = await page.context().newCDPSession(page);

// Enable audio capture
await client.send('Page.startScreencast', {
  format: 'jpeg',
  quality: 50
});

// Capture audio via WebRTC
await page.evaluate(() => {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (event) => {
        // Send chunks to backend via WebSocket
        ws.send(event.data);
      };
      mediaRecorder.start(1000); // 1-second chunks
    });
});
```

**Advantages:**
- Real-time processing possible
- Can feed directly to transcription engine
- Lower latency for insights

**Disadvantages:**
- Complex implementation
- Requires WebSocket server to receive chunks

---

### 3.2 Zoom SDK Capture

**If using Zoom SDK:**
```python
# Pseudocode - Zoom SDK provides hooks
import zoomsdk

meeting = zoomsdk.join_meeting(meeting_id, password)

# Hook into audio stream
def on_audio_raw_data(data):
    # data = raw PCM audio bytes
    save_to_file(data)
    # OR send to real-time transcription
    send_to_whisper(data)

meeting.subscribe_audio(on_audio_raw_data)
```

**Zoom Web SDK** also provides access to audio MediaStream objects

---

### 3.3 Audio Format Standardization

**Raw Capture Output:**
- Format: WebM (Playwright), MP4 (Zoom SDK), or raw PCM
- Codec: OPUS or AAC
- Sample Rate: Variable (usually 48 kHz)

**Normalization (Post-Capture):**
```bash
ffmpeg -i input.webm \
  -ar 16000 \
  -ac 1 \
  -c:a pcm_s16le \
  output.wav
```

**For Real-time Processing:**
- Stream chunks directly to Whisper API (OpenAI's Whisper supports streaming)
- OR use faster-whisper (local, optimized)

---

## 4. Complete Technical Stack (Open-Source)

### 4.1 Bot Orchestration Layer

**Technology:** Python FastAPI
- **Role:** Central coordinator
- **Responsibilities:**
  - Receive meeting join requests (API endpoint)
  - Launch browser/SDK sessions
  - Manage bot lifecycle (join, record, leave)
  - Store recordings and metadata

**Key Libraries:**
- `fastapi` - API framework
- `celery` - Background task queue (for async meeting joins)
- `redis` - Message broker for Celery

---

### 4.2 Browser Automation

**Technology:** Playwright (Python or Node.js)
- **Why Playwright over Puppeteer:** Better cross-browser support, active development
- **Setup:**
  ```bash
  pip install playwright
  playwright install chromium
  ```

**Alternative Stack (If Node.js Preferred):**
- Puppeteer (Node.js)
- Advantages: Simpler, lighter, better documentation

---

### 4.3 Zoom Integration

**Option 1: Official SDK**
- **Zoom Meeting SDK (JavaScript):** https://marketplace.zoom.us/docs/sdk/native-sdks/web
- **Free tier:** Yes

**Option 2: Browser Automation**
- Use Playwright on zoom.us web client

**Recommendation:** Start with browser automation (simpler), migrate to SDK if performance issues

---

### 4.4 Microsoft Teams Integration

**Option 1: Bot Framework**
- **Library:** `botbuilder` (Python SDK)
- **Docs:** https://learn.microsoft.com/en-us/microsoftteams/platform/bots/what-are-bots

**Option 2: Browser Automation**
- Use Playwright on teams.microsoft.com

**Recommendation:** Browser automation for MVP

---

### 4.5 Audio Processing

**Transcription Engine:** OpenAI Whisper (Self-Hosted)
- **Model:** `medium.en` (English-only, balance speed/accuracy)
- **Setup:** 
  ```bash
  pip install openai-whisper
  # OR use faster-whisper (5x faster)
  pip install faster-whisper
  ```

**Format Conversion:** FFmpeg
- Convert captured audio to Whisper-compatible format
- Command: See section 3.3

---

### 4.6 Storage

**Recordings:** Local Filesystem + MinIO (same as previous architecture)
- Path: `/recordings/{year}/{month}/{meeting_id}/recording.webm`

**Metadata:** PostgreSQL
- Schema:
  ```sql
  meetings (
    id UUID PRIMARY KEY,
    meeting_url TEXT,
    platform VARCHAR(20), -- 'google_meet', 'zoom', 'teams'
    scheduled_time TIMESTAMP,
    actual_join_time TIMESTAMP,
    duration_seconds INTEGER,
    recording_path TEXT,
    status VARCHAR(20), -- 'scheduled', 'joining', 'recording', 'completed', 'failed'
    bot_session_id TEXT,
    created_at TIMESTAMP
  )
  ```

---

### 4.7 Real-time Processing (Optional)

**For live insights during meeting:**
- **Streaming Transcription:** Use Whisper with chunked audio (1-second intervals)
- **Live Understanding:** Feed transcript to LLM in real-time
- **WebSocket:** Push insights to frontend dashboard

**Tech Stack:**
- **Websockets:** `fastapi.WebSocket`
- **Stream Processing:** `asyncio` coroutines
- **LLM:** Local Llama 3 or cloud GPT-4 API

---

## 5. Detailed Join Workflow (End-to-End)

### 5.1 Trigger Methods

**Method 1: Manual API Call**
```http
POST /api/v1/bot/join-meeting
Content-Type: application/json

{
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "title": "Client Discovery Call",
  "client_name": "Acme Corp",
  "scheduled_time": "2026-02-05T15:00:00Z"
}

Response 202 Accepted:
{
  "meeting_id": "uuid",
  "status": "scheduled",
  "bot_will_join_at": "2026-02-05T14:58:00Z"  // 2 min before
}
```

**Method 2: Calendar Integration (Auto-trigger)**
- Monitor Google Calendar for events with "aimeet" keyword in description
- OR specific calendar (e.g., "Client Meetings" calendar)
- Auto-extract meeting link from event description or conference data
- Trigger join 2 minutes before scheduled time

**Method 3: Email Parsing**
- Monitor bot email inbox for meeting invites
- Parse invite for meeting link
- Extract time and auto-schedule join

---

### 5.2 Step-by-Step Execution

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCHEDULING PHASE                                          │
├─────────────────────────────────────────────────────────────┤
│ • API receives join request                                  │
│ • Validate meeting URL                                       │
│ • Detect platform (regex: meet.google.com, zoom.us, etc.)  │
│ • Create meeting record in database (status: scheduled)     │
│ • Schedule background job (Celery) to run at meeting time   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. PRE-JOIN PHASE (T-2 minutes)                             │
├─────────────────────────────────────────────────────────────┤
│ • Celery worker picks up task                                │
│ • Select appropriate bot strategy:                           │
│   - Google Meet → Playwright automation                      │
│   - Zoom → Browser automation (or SDK)                       │
│   - Teams → Browser automation (or Bot Framework)            │
│ • Launch browser/SDK session                                 │
│ • Update status: joining                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. JOIN PHASE                                                │
├─────────────────────────────────────────────────────────────┤
│ GOOGLE MEET:                                                 │
│ • Navigate to meeting URL                                    │
│ • Click "Join now" (or "Ask to join")                       │
│ • Wait for host approval (if waiting room enabled)           │
│ • Detect joined state (check for participant list visible)  │
│                                                              │
│ ZOOM:                                                        │
│ • Enter meeting ID + password                                │
│ • Set display name                                           │
│ • Join as participant                                        │
│                                                              │
│ TEAMS:                                                       │
│ • Follow meeting link                                        │
│ • Join as guest (or authenticated bot)                       │
│ • Enable microphone permission                               │
│                                                              │
│ • Update status: recording                                   │
│ • Record actual join timestamp                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RECORDING PHASE                                           │
├─────────────────────────────────────────────────────────────┤
│ • Start audio/video capture                                  │
│ • Option A: Playwright recordVideo (simple)                  │
│ • Option B: Real-time stream capture (WebRTC → WebSocket)   │
│ • Monitor meeting state:                                     │
│   - Participant count                                        │
│   - Audio activity detection                                 │
│   - Meeting end signals                                      │
│ • Store recording chunks (if streaming)                      │
│ • Optional: Real-time transcription (feed to Whisper)       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. EXIT PHASE                                                │
├─────────────────────────────────────────────────────────────┤
│ • Detect meeting end:                                        │
│   - Host ends meeting (kicked notification)                  │
│   - All other participants left (only bot remains)           │
│   - Timeout (max 8 hours)                                    │
│ • Click "Leave" button gracefully                            │
│ • Close browser/SDK session                                  │
│ • Finalize recording file                                    │
│ • Update status: completed                                   │
│ • Record end timestamp, calculate duration                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. POST-PROCESSING PHASE                                     │
├─────────────────────────────────────────────────────────────┤
│ • Move recording to permanent storage                        │
│ • Convert to normalized format (WAV 16kHz)                   │
│ • Trigger transcription pipeline                             │
│ • Extract metadata (duration, file size)                     │
│ • Generate thumbnail (if video captured)                     │
│ • Publish "meeting.recorded" event → Next module            │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Platform-Specific Implementation Details

### 6.1 Google Meet Gotchas

**Challenge 1: Waiting Room**
- **Issue:** If host hasn't joined, bot waits in lobby
- **Solution:** Implement timeout (10 min), send notification to VDK if stuck

**Challenge 2: Permission Prompts**
- **Issue:** Browser asks for microphone/camera access
- **Solution:** Grant permissions in browser context config:
  ```javascript
  context = await browser.newContext({
    permissions: ['microphone', 'camera']
  });
  ```

**Challenge 3: Dynamic Selectors**
- **Issue:** Google changes button labels/classes frequently
- **Solution:** Use aria-labels (more stable):
  ```javascript
  await page.click('button[aria-label*="Join"]');
  ```

---

### 6.2 Zoom Gotchas

**Challenge 1: Password Protected Meetings**
- **Issue:** Can't join without password
- **Solution:** Parse password from URL or require it in API request

**Challenge 2: Waiting for Host**
- **Issue:** "Waiting for host to start meeting"
- **Solution:** Detect message, wait max 15 minutes

**Challenge 3: Web vs Desktop Client**
- **Issue:** Web client has limited features
- **Solution:** Use "Launch Meeting" button simulation OR browser automation with full Zoom web client

---

### 6.3 Microsoft Teams Gotchas

**Challenge 1: Guest Join Flow**
- **Issue:** Teams asks for name entry before joining
- **Solution:** Auto-fill name field with bot name

**Challenge 2: Browser Compatibility**
- **Issue:** Teams prefers Edge/Chrome
- **Solution:** Use Chromium via Playwright (compatible)

**Challenge 3: Lobby Approval**
- **Issue:** Teams has lobby feature (like waiting room)
- **Solution:** Similar to Meet - wait and notify if stuck

---

## 7. Major Challenges & Solutions

### Challenge 1: Bot Detection & Blocking

**Problem:** Platforms might detect and block automation

**Solutions:**
1. **Human-like Behavior**
   - Random delays between actions (100-500ms)
   - Mouse movements (even in headless mode)
   - Use `playwright-extra-plugin-stealth` (bypasses detection)

2. **Persistent Browser Profiles**
   - Save browser state (cookies, localStorage)
   - Reuse same profile (looks like same user)
   - Avoid repeated logins

3. **IP Rotation (if needed)**
   - Use proxy rotation (though likely overkill)

4. **Transparency**
   - Don't hide that it's a bot (ethical + reduces risk)
   - Display name clearly indicates automation

**Code Example:**
```javascript
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

chromium.use(stealth);  // Bypass bot detection
```

---

### Challenge 2: Audio Quality & Mixing

**Problem:** Poor audio quality, speaker overlap, background noise

**Solutions:**
1. **Capture at Highest Quality**
   - Sample rate: 48 kHz during capture (downsample later)
   - Bitrate: 128 kbps minimum

2. **Noise Reduction (Post-processing)**
   - Use FFmpeg audio filters:
     ```bash
     ffmpeg -i input.webm -af "highpass=f=200,lowpass=f=3000" output.wav
     ```
   - OR use RNNoise (AI-based noise suppression)

3. **Speaker Diarization**
   - Use pyannote.audio (open-source) to separate speakers
   - Helps with transcription accuracy

---

### Challenge 3: Authentication & Session Management

**Problem:** Bot account gets logged out, OAuth tokens expire

**Solutions:**
1. **Persistent Sessions**
   - Save browser cookies to disk
   - Load cookies on each session:
     ```javascript
     const context = await browser.newContext({
       storageState: './auth/google-meet-state.json'
     });
     await context.storageState({ path: './auth/google-meet-state.json' });
     ```

2. **Credential Rotation**
   - Use multiple bot accounts
   - If one gets rate-limited/blocked, use another

3. **OAuth Refresh Automation**
   - Background job refreshes tokens before expiry
   - Store in database, encrypted

---

### Challenge 4: Concurrency (Multiple Simultaneous Meetings)

**Problem:** Need to join 5 meetings at the same time

**Solutions:**
1. **Separate Browser Instances**
   - One browser per meeting
   - Resource intensive but isolated

2. **Browser Context Pooling**
   - Reuse browser, separate contexts
   - Lighter weight:
     ```javascript
     const browser = await chromium.launch();
     const context1 = await browser.newContext();
     const context2 = await browser.newContext();
     ```

3. **Resource Limits**
   - Max 3 concurrent bots (to avoid CPU overload)
   - Queue additional requests

4. **Distributed Architecture (Future)**
   - Multiple bot servers (worker nodes)
   - Load balancer distributes meetings

---

### Challenge 5: Meeting End Detection

**Problem:** Don't know when to stop recording

**Solutions:**
1. **Participant Count Monitoring**
   - If only bot remains, leave after 2 minutes
   - Check every 30 seconds:
     ```javascript
     setInterval(async () => {
       const count = await page.$$eval('.participant', els => els.length);
       if (count === 1) leaveAfterDelay();
     }, 30000);
     ```

2. **Host End Signal**
   - Detect "Meeting has ended" message
   - Screenshot analysis or text content check

3. **Max Duration Timeout**
   - Hard limit: 8 hours
   - Prevents infinite recording

4. **Audio Silence Detection**
   - If no audio activity for 10 minutes, send warning
   - If 15 minutes, auto-leave

---

### Challenge 6: Network Reliability

**Problem:** Internet drops, reconnection fails

**Solutions:**
1. **Auto-Reconnect Logic**
   - Detect disconnect (page error events)
   - Attempt rejoin (same meeting URL)
   - Resume recording

2. **Chunked Recording**
   - Save recording in 5-minute segments
   - If crash, only lose last chunk

3. **Health Monitoring**
   - WebSocket to backend: heartbeat every 10s
   - If no heartbeat, alert + manual intervention

---

### Challenge 7: Platform Updates & UI Changes

**Problem:** Google Meet changes button layout, breaks automation

**Solutions:**
1. **Robust Selectors**
   - Use multiple selectors (fallback chain):
     ```javascript
     await page.click('button[aria-label*="Join"]')
       .catch(() => page.click('button:has-text("Join")'))
       .catch(() => page.click('[data-test-id="join-button"]'));
     ```

2. **Visual Regression Testing**
   - Weekly automated test: bot joins test meeting
   - Alert if selectors fail

3. **Maintenance Plan**
   - Monthly review of automation scripts
   - Subscribe to platform changelog/release notes

---

## 8. Security & Compliance

### 8.1 Legal Considerations

**Recording Consent:**
- **Required by law** in many jurisdictions (especially US states like California)
- **Implementation:**
  - Bot sends chat message: "This meeting is being recorded by AI Assistant"
  - OR verbal announcement (TTS): Bot "speaks" at join
  - Participants can decline and leave

**Data Storage:**
- **Encryption at rest** (LUKS for filesystem)
- **Encryption in transit** (HTTPS, TLS)
- **Retention policy:** Auto-delete after 2 years (or per client agreement)

---

### 8.2 Access Control

**Bot Credentials:**
- **Environment variables** (never in code)
- **Secrets manager** (e.g., Vault) for production

**Meeting Access:**
- Only VDK can trigger bot join (via API key)
- Rate limiting: Max 20 meetings/day per user

---

### 8.3 Audit Logging

**Log Every Action:**
- Meeting join attempts (success/failure)
- Recording start/stop times
- File access (who viewed/downloaded)

**Log Format:**
```json
{
  "timestamp": "2026-02-05T15:00:00Z",
  "event": "bot_joined_meeting",
  "meeting_id": "uuid",
  "platform": "google_meet",
  "user": "vdk",
  "ip": "1.2.3.4"
}
```

---

## 9. Development Roadmap (45 Days)

### Week 1-2: Foundation (14 days)
- [ ] Database schema design
- [ ] FastAPI project setup
- [ ] Celery + Redis configuration
- [ ] Google Meet bot (Playwright)
  - [ ] Login automation
  - [ ] Join meeting
  - [ ] Basic recording (recordVideo)
- [ ] Manual testing: Join 5 test meetings successfully

---

### Week 3: Zoom Integration (7 days)
- [ ] Zoom link parsing
- [ ] Browser automation for Zoom web client
- [ ] Recording capture
- [ ] Handle password-protected meetings
- [ ] Test: Join 3 Zoom meetings

---

### Week 4: Teams Integration (7 days)
- [ ] Teams browser automation
- [ ] Guest join flow
- [ ] Recording capture
- [ ] Test: Join 3 Teams meetings

---

### Week 5: Audio Processing (7 days)
- [ ] FFmpeg conversion pipeline
- [ ] Whisper transcription integration
- [ ] Real-time streaming (optional)
- [ ] Noise reduction filters
- [ ] Test: Transcribe 10 test recordings

---

### Week 6: Robustness & Polish (7 days)
- [ ] Error handling (reconnection, timeouts)
- [ ] Meeting end detection logic
- [ ] Concurrency testing (3 simultaneous meetings)
- [ ] Dashboard UI (view bot status, upcoming meetings)
- [ ] Documentation

---

### Week 7: Production Deployment (3 days)
- [ ] Server setup (Docker Compose)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Alerting (Slack/email notifications)
- [ ] Load testing
- [ ] Go-live with VDK's real meetings

---

## 10. API Specifications

### Endpoint 1: Schedule Bot Join
```http
POST /api/v1/bot/schedule-join

{
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "title": "Client Discovery",
  "client_name": "Acme Corp",
  "scheduled_time": "2026-02-06T10:00:00Z",  // Optional, auto-detect from calendar
  "auto_leave": true,  // Leave when meeting ends
  "transcribe_realtime": false  // Transcribe during meeting or after
}

Response 202:
{
  "meeting_id": "uuid",
  "status": "scheduled",
  "bot_join_time": "2026-02-06T09:58:00Z"
}
```

---

### Endpoint 2: Get Bot Status
```http
GET /api/v1/bot/status/{meeting_id}

Response 200:
{
  "meeting_id": "uuid",
  "status": "recording",  // scheduled, joining, recording, completed, failed
  "platform": "google_meet",
  "joined_at": "2026-02-06T10:00:45Z",
  "recording_duration_seconds": 320,
  "participant_count": 4,
  "is_recording": true
}
```

---

### Endpoint 3: Force Leave
```http
POST /api/v1/bot/leave/{meeting_id}

Response 200:
{
  "status": "leaving",
  "message": "Bot will exit in 10 seconds"
}
```

---

### Endpoint 4: List Bot Sessions
```http
GET /api/v1/bot/sessions?status=recording&limit=10

Response 200:
{
  "sessions": [
    {
      "meeting_id": "uuid1",
      "title": "Client Call",
      "status": "recording",
      "joined_at": "2026-02-06T10:00:00Z"
    },
    {
      "meeting_id": "uuid2",
      "title": "Internal Standup",
      "status": "completed",
      "duration_seconds": 1800
    }
  ],
  "total": 2
}
```

---

## 11. Monitoring & Alerts

### Key Metrics

1. **Join Success Rate:** % of scheduled meetings successfully joined
   - **Target:** >95%
   - **Alert:** If <90% over 24 hours

2. **Recording Failures:** Instances where recording didn't capture
   - **Target:** <2%
   - **Alert:** Any failure (critical)

3. **Bot Latency:** Time from scheduled join to actual join
   - **Target:** <2 minutes
   - **Alert:** If >5 minutes

4. **Concurrency:** Number of active bot sessions
   - **Limit:** 3 simultaneous
   - **Alert:** If queue depth >5

### Alerting Channels
- **Email:** For non-critical warnings
- **Slack:** For critical failures (join failure, recording crash)
- **Dashboard:** Real-time status page

---

## 12. Cost Analysis (Open-Source Stack)

### Infrastructure Costs
- **Server:** 8 CPU, 16GB RAM, 500GB SSD = ~$40/month (Hetzner, DigitalOcean)
- **Storage:** 1TB additional = ~$10/month
- **Total:** ~$50/month

### No Paid APIs
- ✅ Playwright: Free
- ✅ Whisper (self-hosted): Free
- ✅ FFmpeg: Free
- ✅ PostgreSQL: Free
- ✅ Zoom Meeting SDK: Free tier sufficient
- ✅ Google/Microsoft APIs: Free tier (no bot-specific charges)

**Total Monthly Cost:** $50 (infrastructure only)

---

## 13. Success Criteria

**Bot is production-ready when:**

✅ **Core Functionality:**
- [ ] Joins Google Meet meetings 95% of the time
- [ ] Joins Zoom meetings 90% of the time
- [ ] Joins Teams meetings 85% of the time
- [ ] Records entire meeting without drops
- [ ] Transcribes audio to text with >85% accuracy

✅ **Reliability:**
- [ ] Handles 3 concurrent meetings
- [ ] Auto-recovers from network disconnects
- [ ] Detects meeting end accurately
- [ ] Zero data loss (all recordings saved)

✅ **User Experience:**
- [ ] VDK can schedule bot with <3 clicks
- [ ] Real-time status visible in dashboard
- [ ] Recording available <5 min after meeting ends

---

## 14. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Google blocks automation | High | Medium | Use stealth plugins, persistent sessions, multiple accounts |
| Frequent UI changes | Medium | High | Robust selectors, weekly testing, fallback strategies |
| Server crashes during meeting | High | Low | Auto-restart, chunked recording (minimal data loss) |
| Legal issues (consent) | High | Low | Auto-announce recording, clear bot naming |
| Audio quality poor | Medium | Medium | Noise reduction, high bitrate capture |

---

## Conclusion

This **Meeting Bot Architecture** provides a **focused, powerful solution** for automatic meeting attendance and data extraction. By acting as a participant, the bot gains access to the complete meeting experience - audio, video, chat, and participant list.

**Key Advantages Over Upload-Based Approach:**
- ✅ **Zero manual work** - no uploading files
- ✅ **Real-time insights** - can process during meeting
- ✅ **Complete data** - captures everything, not just what's recorded
- ✅ **Consistent format** - all recordings normalized automatically

**Next Steps:**
1. Approve this architecture
2. Set up development environment
3. Begin Week 1: Google Meet bot MVP
4. Test with real meetings

The open-source stack ensures **zero recurring costs** beyond infrastructure, and the modular design allows platform-by-platform rollout (start with Meet, add Zoom/Teams later).
