# Meeting Data Processing Pipeline - God-Level Architecture

## Executive Overview

This pipeline transforms **raw meeting audio** (from the bot) into a **complete, structured, understood meeting object** containing:

- **Transcript** (word-for-word text with timestamps)
- **Speaker Identification** (who said what)
- **Key Discussion Points** (topics covered)
- **Requirements** (what the client wants built)
- **Decisions** (what was agreed upon)
- **Action Items** (next steps, assignees)
- **Timeline** (deadlines, milestones mentioned)
- **Sentiment** (client satisfaction, concerns)
- **Summary** (executive summary for quick reading)

**Input:** Audio file (WAV 16kHz from bot recording)  
**Output:** Structured JSON object with all extracted information  
**Processing Time Target:** <5 minutes for 1-hour meeting

---

## 1. Pipeline Architecture Overview

### 1.1 Processing Stages

```
┌────────────────────────────────────────────────────────────┐
│ STAGE 1: AUDIO PREPROCESSING                               │
├────────────────────────────────────────────────────────────┤
│ • Noise reduction (RNNoise, FFmpeg filters)                │
│ • Normalization (volume leveling)                          │
│ • Format validation (ensure 16kHz WAV)                     │
│ • Audio quality check (SNR, clipping detection)            │
│ Output: Clean audio ready for transcription                │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 2: TRANSCRIPTION                                     │
├────────────────────────────────────────────────────────────┤
│ Tool: OpenAI Whisper (faster-whisper for speed)           │
│ • Convert audio to text with timestamps                    │
│ • Language detection (auto or specified)                   │
│ • Word-level confidence scores                             │
│ Output: Raw transcript with timestamps                     │
│         [{"start": 0.5, "end": 2.3, "text": "Hello"}]     │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 3: SPEAKER DIARIZATION                               │
├────────────────────────────────────────────────────────────┤
│ Tool: pyannote.audio                                       │
│ • Identify speaker segments                                │
│ • Assign speaker labels (SPEAKER_00, SPEAKER_01, ...)     │
│ • Align with transcript timestamps                         │
│ • Infer speaker names from context (optional)              │
│ Output: Transcript with speaker labels                     │
│         [{"speaker": "SPEAKER_00", "text": "Hello"}]      │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 4: TRANSCRIPT ENHANCEMENT                            │
├────────────────────────────────────────────────────────────┤
│ • Punctuation correction                                   │
│ • Filler word removal (um, uh, like)                       │
│ • Paragraph segmentation (topic breaks)                    │
│ • Speaker name inference (client vs VDK vs team)           │
│ Output: Cleaned, readable transcript                       │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 5: AI UNDERSTANDING (LLM EXTRACTION)                 │
├────────────────────────────────────────────────────────────┤
│ Tool: GPT-4 or Local Llama 3 70B                          │
│ • Extract structured information:                          │
│   - Summary (executive + detailed)                         │
│   - Requirements (feature requests, specs)                 │
│   - Decisions (agreed actions)                             │
│   - Action items (to-dos with owners)                      │
│   - Timeline (deadlines, milestones)                       │
│   - Key discussion points                                  │
│   - Questions raised                                       │
│   - Concerns/risks                                         │
│   - Sentiment analysis                                     │
│ Output: Structured JSON object                             │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 6: VALIDATION & POST-PROCESSING                      │
├────────────────────────────────────────────────────────────┤
│ • Cross-reference extracted data with transcript           │
│ • Confidence scoring for each extraction                   │
│ • Duplicate removal                                        │
│ • Format standardization (dates, times)                    │
│ • Quality checks (completeness, coherence)                 │
│ Output: Final validated meeting object                     │
└────────────────┬───────────────────────────────────────────┘
                 │
                 v
┌────────────────────────────────────────────────────────────┐
│ STAGE 7: STORAGE & INDEXING                                │
├────────────────────────────────────────────────────────────┤
│ • Save to PostgreSQL (structured data)                     │
│ • Index for search (full-text search on transcript)        │
│ • Cache for quick retrieval                                │
│ • Trigger downstream modules (client comms, docs)          │
│ Output: Meeting ready for consumption                      │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Audio Preprocessing

### 2.1 Why Preprocessing Matters

Raw audio often contains:
- Background noise (HVAC, keyboard clicks)
- Uneven volume levels
- Clipping/distortion
- Echo/reverb

**Impact on transcription:** Poor audio = 20-40% lower accuracy

### 2.2 Noise Reduction

**Tool: RNNoise** (AI-based, open-source)
```bash
# Apply RNNoise filter
rnnoise_demo input.wav output_clean.wav
```

**Alternative: FFmpeg Filters**
```bash
ffmpeg -i input.wav \
  -af "highpass=f=200,lowpass=f=3000,anlmdn=s=10" \
  output_clean.wav
```
- `highpass=200`: Remove low rumble
- `lowpass=3000`: Remove high hiss
- `anlmdn`: Adaptive noise reduction

### 2.3 Normalization

**Goal:** Consistent volume across entire meeting

```bash
ffmpeg -i input.wav -af "loudnorm" output_normalized.wav
```

### 2.4 Quality Check

**Metrics to Validate:**
- **SNR (Signal-to-Noise Ratio):** >20dB acceptable
- **Clipping:** <1% of samples
- **Duration:** Matches expected (vs meeting scheduled length)

**Implementation:**
```python
import librosa
import numpy as np

def check_audio_quality(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    
    # SNR estimation
    energy = np.sum(y**2) / len(y)
    snr_estimate = 10 * np.log10(energy)
    
    # Clipping detection
    clipping_ratio = np.sum(np.abs(y) > 0.99) / len(y)
    
    return {
        "snr_db": snr_estimate,
        "clipping_percent": clipping_ratio * 100,
        "duration_seconds": len(y) / sr
    }
```

---

## 3. Stage 2: Transcription

### 3.1 Tool Selection: Whisper

**Why Whisper:**
- State-of-the-art accuracy (WER <5% on clear audio)
- Multi-language support (99 languages)
- Open-source (MIT license)
- Handles accents, jargon well

**Model Options:**

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39M | 32x realtime | Good | Real-time transcription |
| base | 74M | 16x realtime | Better | Fast batch processing |
| small | 244M | 6x realtime | Very Good | Balanced choice |
| medium | 769M | 2x realtime | Excellent | High accuracy needed |
| large-v3 | 1550M | 1x realtime | Best | Maximum accuracy |

**Recommendation:** `medium.en` (English-only, faster than multilingual)

### 3.2 Implementation: faster-whisper

**Why faster-whisper over standard Whisper:**
- 4-5x faster inference
- Lower memory usage
- Same accuracy

**Setup:**
```bash
pip install faster-whisper
```

**Code:**
```python
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cuda", compute_type="float16")

def transcribe_audio(audio_path):
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True  # Voice Activity Detection
    )
    
    transcript = []
    for segment in segments:
        transcript.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": [
                {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end,
                    "probability": word.probability
                }
                for word in segment.words
            ]
        })
    
    return {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": transcript
    }
```

### 3.3 Optimization Strategies

**GPU Acceleration:**
- Use CUDA if available (10x faster)
- Batch processing for multiple files

**Chunking for Long Meetings:**
- Split audio into 10-minute chunks
- Process in parallel
- Merge results with timestamp alignment

**Caching:**
- Cache transcriptions by audio hash
- Avoid re-transcribing if re-processing needed

### 3.4 Output Format

```json
{
  "language": "en",
  "duration": 3600,
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello everyone, thanks for joining today's call.",
      "words": [
        {"word": "Hello", "start": 0.0, "end": 0.3, "probability": 0.98},
        {"word": "everyone", "start": 0.4, "end": 0.8, "probability": 0.95}
      ]
    }
  ]
}
```

---

## 4. Stage 3: Speaker Diarization

### 4.1 Why Diarization Matters

**Problem:** Whisper doesn't identify speakers  
**Solution:** Overlay speaker labels on transcript

**Use Case:** Know who said what (client vs VDK vs team members)

### 4.2 Tool: pyannote.audio

**Installation:**
```bash
pip install pyannote.audio
```

**Requires Hugging Face Token** (free account):
- Sign up at huggingface.co
- Accept model license: https://huggingface.co/pyannote/speaker-diarization
- Generate token

**Code:**
```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="YOUR_HF_TOKEN"
)

def diarize_audio(audio_path):
    diarization = pipeline(audio_path)
    
    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    
    return speakers
```

**Output:**
```json
[
  {"start": 0.0, "end": 5.2, "speaker": "SPEAKER_00"},
  {"start": 5.3, "end": 12.1, "speaker": "SPEAKER_01"},
  {"start": 12.2, "end": 18.5, "speaker": "SPEAKER_00"}
]
```

### 4.3 Aligning Diarization with Transcript

**Challenge:** Diarization and transcription are separate  
**Solution:** Merge based on timestamp overlap

```python
def merge_transcript_with_speakers(transcript, speakers):
    result = []
    
    for segment in transcript["segments"]:
        seg_start = segment["start"]
        seg_end = segment["end"]
        
        # Find speaker who spoke during this segment (majority overlap)
        speaker_times = {}
        for spk in speakers:
            overlap_start = max(seg_start, spk["start"])
            overlap_end = min(seg_end, spk["end"])
            overlap_duration = max(0, overlap_end - overlap_start)
            
            speaker = spk["speaker"]
            speaker_times[speaker] = speaker_times.get(speaker, 0) + overlap_duration
        
        # Assign speaker with most overlap
        assigned_speaker = max(speaker_times, key=speaker_times.get) if speaker_times else "UNKNOWN"
        
        result.append({
            "speaker": assigned_speaker,
            "start": seg_start,
            "end": seg_end,
            "text": segment["text"]
        })
    
    return result
```

### 4.4 Speaker Name Inference (Optional)

**Goal:** Convert SPEAKER_00 → "VDK", SPEAKER_01 → "Client"

**Approach 1: Contextual Clues**
- If speaker says "I'm VDK" → label as VDK
- If multiple unknown speakers, ask user to identify

**Approach 2: Voice Enrollment (Future)**
- Pre-record VDK's voice
- Use speaker recognition to auto-identify

**Approach 3: LLM Inference**
- Feed transcript to LLM, ask it to infer based on context
- "Who is most likely the client based on questions asked?"

---

## 5. Stage 4: Transcript Enhancement

### 5.1 Punctuation Correction

**Problem:** Whisper sometimes misses punctuation  
**Solution:** Use punctuation restoration model

**Tool: deepmultilingualpunctuation**
```bash
pip install deepmultilingualpunctuation
```

```python
from deepmultilingualpunctuation import PunctuationModel

model = PunctuationModel()

def add_punctuation(text):
    return model.restore_punctuation(text)
```

### 5.2 Filler Word Removal

**Common Fillers:** um, uh, like, you know, sort of

```python
import re

def remove_fillers(text):
    fillers = r'\b(um|uh|like|you know|sort of|kind of)\b'
    return re.sub(fillers, '', text, flags=re.IGNORECASE).strip()
```

**Trade-off:** Keep fillers for authenticity vs remove for readability  
**Recommendation:** Keep in raw transcript, remove in cleaned version

### 5.3 Paragraph Segmentation

**Goal:** Break transcript into logical paragraphs (topics)

**Approach:**
- Use sentence embeddings to detect topic shifts
- Group sentences with high similarity

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def segment_paragraphs(sentences, threshold=0.7):
    embeddings = model.encode(sentences)
    paragraphs = []
    current_para = [sentences[0]]
    
    for i in range(1, len(sentences)):
        similarity = cosine_similarity(
            [embeddings[i-1]], 
            [embeddings[i]]
        )[0][0]
        
        if similarity > threshold:
            current_para.append(sentences[i])
        else:
            paragraphs.append(" ".join(current_para))
            current_para = [sentences[i]]
    
    paragraphs.append(" ".join(current_para))
    return paragraphs
```

---

## 6. Stage 5: AI Understanding (LLM Extraction)

### 6.1 The Core Challenge

**Input:** Long transcript (10,000+ words for 1-hour meeting)  
**Goal:** Extract structured, actionable information  
**Tool:** Large Language Model (GPT-4, Claude, or local Llama 3)

### 6.2 LLM Selection

**Option 1: GPT-4 (OpenAI API)**
- **Pros:** Best accuracy, 128k context window, JSON mode
- **Cons:** Paid ($0.03/1k tokens), external dependency
- **Cost:** ~$0.50 per 1-hour meeting

**Option 2: Claude 3 Opus (Anthropic)**
- **Pros:** 200k context, excellent at following instructions
- **Cons:** Paid ($0.015/1k tokens)

**Option 3: Local Llama 3 70B**
- **Pros:** Free, private, no API limits
- **Cons:** Requires powerful GPU (40GB VRAM), slower

**Recommendation for MVP:** GPT-4 (quality first)  
**Long-term:** Migrate to local Llama 3 (cost savings)

### 6.3 Extraction Prompt Strategy

**Key Principle:** Use structured prompts with examples (few-shot learning)

**Prompt Template:**
```
You are an expert meeting analyzer. Extract structured information from the following meeting transcript.

TRANSCRIPT:
{transcript_with_speakers}

Extract the following information in JSON format:

1. SUMMARY: A 2-3 sentence executive summary of the meeting
2. REQUIREMENTS: List of product/project requirements mentioned (be specific)
3. DECISIONS: Key decisions made during the meeting
4. ACTION_ITEMS: Tasks to be done, with assignee if mentioned
5. TIMELINE: Any deadlines or time estimates discussed
6. DISCUSSION_POINTS: Main topics covered
7. QUESTIONS_RAISED: Unanswered questions or concerns
8. SENTIMENT: Overall client satisfaction (positive/neutral/negative) with justification

Output only valid JSON, no additional text.

EXAMPLE OUTPUT:
{
  "summary": "Discussed website redesign project...",
  "requirements": [
    "Modern dark theme UI",
    "Mobile responsive design",
    "User authentication system"
  ],
  "decisions": [
    "Use React for frontend",
    "Launch MVP in 4 weeks"
  ],
  "action_items": [
    {
      "task": "Create wireframes",
      "assignee": "VDK",
      "deadline": "2026-02-10"
    }
  ],
  "timeline": "4 weeks for MVP, 8 weeks for full launch",
  "discussion_points": [
    "Design preferences",
    "Technology stack",
    "Budget constraints"
  ],
  "questions_raised": [
    "Which payment gateway to use?"
  ],
  "sentiment": {
    "overall": "positive",
    "justification": "Client expressed excitement about the timeline"
  }
}
```

### 6.4 Implementation

```python
import openai
import json

openai.api_key = "YOUR_API_KEY"

def extract_meeting_insights(transcript):
    prompt = f"""
    You are an expert meeting analyzer. Extract structured information from the following meeting transcript.
    
    TRANSCRIPT:
    {transcript}
    
    [... rest of prompt ...]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a meeting analysis expert."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},  # Ensures JSON output
        temperature=0.3  # Lower = more consistent
    )
    
    return json.loads(response.choices[0].message.content)
```

### 6.5 Handling Long Transcripts (>100k tokens)

**Problem:** Even GPT-4 has 128k limit; very long meetings may exceed

**Solution 1: Chunking + Summarization**
```
1. Split transcript into 20-minute chunks
2. Extract insights from each chunk separately
3. Merge results
4. Final pass: Summarize merged insights
```

**Solution 2: Map-Reduce Pattern**
```
1. Extract key points from each chunk (MAP)
2. Combine all key points (REDUCE)
3. Final analysis on combined points
```

### 6.6 Advanced Extraction: Multi-Pass Analysis

**Pass 1: Quick Extraction (Fast Model)**
- Use GPT-3.5 for initial pass
- Extract obvious requirements, decisions

**Pass 2: Deep Analysis (GPT-4)**
- Focus on nuances, sentiment, risks
- Cross-reference with Pass 1

**Pass 3: Validation**
- Check for contradictions
- Ensure completeness

---

## 7. Stage 6: Validation & Quality Assurance

### 7.1 Confidence Scoring

**Goal:** Assign confidence to each extraction

**Method:**
- Ask LLM to provide confidence (0-100) for each item
- Cross-reference with transcript (does quote exist?)

**Enhanced Prompt:**
```
For each requirement, provide:
- The requirement text
- A direct quote from the transcript supporting it
- Confidence score (0-100)
```

### 7.2 Cross-Referencing

**Validation Checks:**
- Do all action items have corresponding discussion in transcript?
- Are quoted decisions actually in the transcript?
- Do timelines match mentioned dates?

```python
def validate_extraction(transcript, extraction):
    errors = []
    
    # Check if requirements are mentioned in transcript
    for req in extraction["requirements"]:
        if req.lower() not in transcript.lower():
            errors.append(f"Requirement not found in transcript: {req}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

### 7.3 Duplicate Removal

**Problem:** LLM might extract same item multiple times

```python
def remove_duplicates(items):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    embeddings = model.encode(items)
    unique_items = []
    
    for i, item in enumerate(items):
        is_duplicate = False
        for j in range(i):
            similarity = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if similarity > 0.9:  # 90% similar = duplicate
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_items.append(item)
    
    return unique_items
```

---

## 8. Final Output Schema (Complete Meeting Object)

```json
{
  "meeting_id": "uuid",
  "title": "Client Discovery Call - Acme Corp",
  "client_name": "Acme Corp",
  "date": "2026-02-05T15:00:00Z",
  "duration_seconds": 3600,
  "participants": [
    {"name": "VDK", "speaker_label": "SPEAKER_00", "speaking_time_seconds": 1800},
    {"name": "John (Client)", "speaker_label": "SPEAKER_01", "speaking_time_seconds": 1600}
  ],
  
  "transcript": {
    "raw": [
      {"speaker": "VDK", "start": 0.0, "end": 5.2, "text": "Hello everyone..."},
      {"speaker": "John", "start": 5.3, "end": 12.1, "text": "Thanks for having me..."}
    ],
    "cleaned": "VDK: Hello everyone...\nJohn: Thanks for having me...",
    "paragraphs": [
      "Opening remarks and introductions...",
      "Discussion of project requirements..."
    ]
  },
  
  "summary": {
    "executive": "Discussed website redesign for Acme Corp...",
    "detailed": "The meeting covered three main areas: design preferences..."
  },
  
  "requirements": [
    {
      "text": "Modern dark theme with glassmorphism effects",
      "category": "Design",
      "priority": "High",
      "confidence": 95,
      "quote": "We really want a modern dark theme...",
      "timestamp": 145.3
    },
    {
      "text": "User authentication with Google and email",
      "category": "Feature",
      "priority": "Critical",
      "confidence": 98,
      "quote": "Users should be able to login with Google...",
      "timestamp": 320.1
    }
  ],
  
  "decisions": [
    {
      "text": "Use React for frontend framework",
      "made_by": "VDK",
      "agreed_by": ["John"],
      "timestamp": 890.5,
      "confidence": 99
    }
  ],
  
  "action_items": [
    {
      "task": "Create initial wireframes",
      "assignee": "VDK",
      "deadline": "2026-02-10",
      "priority": "High",
      "status": "pending",
      "timestamp": 1200.3
    },
    {
      "task": "Send brand guidelines document",
      "assignee": "John",
      "deadline": "2026-02-08",
      "priority": "Medium",
      "status": "pending",
      "timestamp": 1450.8
    }
  ],
  
  "timeline": {
    "milestones": [
      {
        "event": "MVP Launch",
        "target_date": "2026-03-05",
        "duration_estimate": "4 weeks"
      },
      {
        "event": "Full Launch",
        "target_date": "2026-04-02",
        "duration_estimate": "8 weeks total"
      }
    ],
    "next_meeting": "2026-02-12T15:00:00Z"
  },
  
  "discussion_points": [
    "Design preferences and inspiration",
    "Technology stack selection",
    "Budget and timeline constraints",
    "Integration requirements"
  ],
  
  "questions_raised": [
    {
      "question": "Which payment gateway should we use?",
      "asked_by": "John",
      "answered": false,
      "timestamp": 2100.5
    }
  ],
  
  "concerns": [
    "Timeline might be tight for full feature set",
    "Budget allocation for third-party APIs"
  ],
  
  "sentiment": {
    "overall": "positive",
    "client_satisfaction": 8.5,
    "justification": "Client expressed excitement multiple times...",
    "key_positive_moments": [
      {"timestamp": 450.2, "text": "This is exactly what we need!"}
    ],
    "key_concerns": [
      {"timestamp": 1800.1, "text": "I'm a bit worried about the timeline"}
    ]
  },
  
  "metadata": {
    "transcription_model": "faster-whisper-medium.en",
    "transcription_confidence": 0.94,
    "language": "en",
    "processing_time_seconds": 180,
    "llm_model": "gpt-4-turbo",
    "processed_at": "2026-02-05T17:30:00Z"
  }
}
```

---

## 9. Technical Stack Summary

| Component | Tool | Alternative | Reason |
|-----------|------|-------------|---------|
| **Transcription** | faster-whisper | Standard Whisper | 5x faster, same accuracy |
| **Diarization** | pyannote.audio | - | Best open-source option |
| **LLM Extraction** | GPT-4 | Llama 3 70B | Quality (MVP), will migrate to local |
| **Audio Processing** | FFmpeg, RNNoise | - | Industry standard |
| **Embeddings** | sentence-transformers | - | Deduplication, similarity |
| **Database** | PostgreSQL | - | JSON support, full-text search |
| **Task Queue** | Celery + Redis | - | Background processing |

---

## 10. Processing: Real-Time vs Batch

### 10.1 Real-Time Processing (During Meeting)

**Advantages:**
- Instant insights (view summary while meeting ongoing)
- Can alert VDK if important point mentioned
- Faster time-to-value

**Challenges:**
- Higher CPU/GPU load during meeting
- Incremental transcription less accurate
- Diarization needs complete audio

**Implementation:**
```python
# Process in 30-second chunks
async def realtime_process(audio_stream):
    buffer = []
    
    async for chunk in audio_stream:
        buffer.append(chunk)
        
        if len(buffer) >= 30:  # 30 seconds
            audio = combine_chunks(buffer)
            transcript = transcribe(audio)
            insights = quick_extract(transcript)  # Lightweight extraction
            
            emit_to_dashboard(insights)
            buffer = []
```

**Use Case:** Live dashboard showing topics being discussed

---

### 10.2 Batch Processing (Post-Meeting)

**Advantages:**
- Better accuracy (full context for LLM)
- Lower resource usage during meeting
- Can retry if errors

**Challenges:**
- Delay in insights (wait for meeting to end)

**Recommendation:** **Batch processing for MVP**, add real-time later

---

## 11. Major Challenges & Solutions

### Challenge 1: Low Transcription Accuracy (Noisy Audio, Accents)

**Problem:** Whisper struggles with heavy accents, jargon, background noise

**Solutions:**
1. **Audio Preprocessing** (see Stage 1)
   - Aggressive noise reduction
   - Voice isolation

2. **Custom Vocabulary**
   - Fine-tune Whisper on domain-specific terms
   - Create jargon dictionary (e.g., "Kubernetes" not "Cuban Nettie's")

3. **Post-Correction**
   - Use LLM to fix obvious errors
   - "Kuber Nettie's" → "Kubernetes" based on context

4. **Human-in-Loop (Fallback)**
   - If confidence <70%, flag for manual review

---

### Challenge 2: Speaker Diarization Errors (Multiple Speakers)

**Problem:** pyannote confuses speakers, especially if voices similar

**Solutions:**
1. **Voice Enrollment**
   - Pre-record VDK's voice
   - Use as anchor for identification

2. **Context-Based Correction**
   - LLM infers: "The person asking questions is likely the client"
   - Relabel based on role

3. **Manual Correction UI**
   - Dashboard to fix speaker labels
   - "Was this said by you or the client?"

---

### Challenge 3: LLM Hallucinations (Invented Requirements)

**Problem:** GPT-4 extracts requirements not actually discussed

**Solutions:**
1. **Grounding with Quotes**
   - Force LLM to provide transcript quote for each extraction
   - Validate quote exists

2. **Low Temperature**
   - Set temperature=0.1 (more deterministic, less creative)

3. **Validation Layer**
   - Semantic search: Is extracted item in transcript embeddings?

4. **Human Review**
   - Send summary to VDK for approval before sending to client

---

### Challenge 4: Long Processing Time (1-hour meeting = 10 min processing)

**Problem:** Target is <5 minutes, but naive approach takes longer

**Solutions:**
1. **Parallel Processing**
   ```
   Split audio → [Chunk 1, Chunk 2, Chunk 3]
                      ↓        ↓        ↓
                  Transcribe in parallel
                      ↓        ↓        ↓
                  Merge results
   ```

2. **GPU Acceleration**
   - Use CUDA for Whisper (10x faster)
   - Batch GPU operations

3. **Smaller Models for Speed**
   - Use `small` Whisper model (6x realtime)
   - Trade 2% accuracy for 3x speed

4. **Caching**
   - Cache transcription (audio hash)
   - Only re-run LLM extraction if prompt changes

---

### Challenge 5: Cost Management (LLM API Costs)

**Problem:** $0.50/meeting adds up (100 meetings/month = $50)

**Solutions:**
1. **Prompt Optimization**
   - Compress transcript (remove fillers, redundancy)
   - Use cheaper model (GPT-3.5) for initial pass

2. **Local LLM Migration**
   - Run Llama 3 70B locally
   - One-time GPU cost ($2000 RTX 4090), unlimited usage

3. **Tiered Processing**
   - Quick extraction (free, local) by default
   - Deep analysis (GPT-4) only for important meetings

---

### Challenge 6: Multi-Language Support

**Problem:** Client speaks in non-English language

**Solutions:**
1. **Whisper Auto-Detection**
   - Whisper detects 99 languages automatically
   - Transcribe in original language

2. **Translation Layer**
   - Use Google Translate API (free tier: 500k chars/month)
   - Translate to English before LLM extraction

3. **Multilingual LLM**
   - GPT-4 handles 50+ languages natively

---

### Challenge 7: Data Privacy & Security

**Problem:** Sensitive client data sent to OpenAI

**Solutions:**
1. **Local-First Architecture**
   - Run Llama 3 locally (no external API)
   - Data never leaves your server

2. **Data Anonymization**
   - Redact PII (emails, phone numbers) before LLM
   - Replace with placeholders: "john@example.com" → "[EMAIL_1]"

3. **Encryption**
   - Encrypt transcripts at rest (AES-256)
   - TLS for all API calls

4. **OpenAI Data Policy**
   - Use `api.openai.com` (not stored for training)
   - Set data retention: 0 days

---

## 12. Development Timeline (30 Days)

### Week 1: Transcription (7 days)
- [ ] Set up faster-whisper
- [ ] Audio preprocessing pipeline (FFmpeg, RNNoise)
- [ ] Quality validation logic
- [ ] GPU optimization
- [ ] Test: Transcribe 20 sample meetings

---

### Week 2: Diarization (7 days)
- [ ] Integrate pyannote.audio
- [ ] Speaker alignment algorithm
- [ ] Speaker name inference
- [ ] Test: Diarize 10 multi-speaker meetings

---

### Week 3: LLM Extraction (7 days)
- [ ] Design extraction prompts
- [ ] GPT-4 integration
- [ ] Confidence scoring
- [ ] Validation layer
- [ ] Test: Extract insights from 15 meetings

---

### Week 4: Integration & Polish (7 days)
- [ ] End-to-end pipeline (audio → JSON object)
- [ ] Database storage
- [ ] API endpoints (get insights, update corrections)
- [ ] Dashboard UI (view extracted data)
- [ ] Load testing (10 concurrent meetings)

---

### Week 5 (Buffer): Edge Cases (2 days)
- [ ] Handling errors (failed transcription, LLM timeout)
- [ ] Retry logic
- [ ] Monitoring and alerts
- [ ] Documentation

---

## 13. API Specifications

### Endpoint 1: Trigger Processing
```http
POST /api/v1/meetings/{meeting_id}/process

Response 202 Accepted:
{
  "status": "processing",
  "estimated_completion": "2026-02-05T17:35:00Z",
  "progress_url": "/api/v1/meetings/{id}/processing-status"
}
```

---

### Endpoint 2: Get Processing Status
```http
GET /api/v1/meetings/{meeting_id}/processing-status

Response 200:
{
  "status": "processing",  // queued, processing, completed, failed
  "current_stage": "transcription",
  "progress_percent": 45,
  "stages": {
    "preprocessing": "completed",
    "transcription": "in_progress",
    "diarization": "pending",
    "extraction": "pending"
  }
}
```

---

### Endpoint 3: Get Processed Data
```http
GET /api/v1/meetings/{meeting_id}/insights

Response 200:
{
  "meeting_id": "uuid",
  "summary": {...},
  "requirements": [...],
  "decisions": [...],
  "action_items": [...],
  "timeline": {...},
  "sentiment": {...}
  // Full schema from Section 8
}
```

---

### Endpoint 4: Update Corrections (Human Feedback)
```http
PATCH /api/v1/meetings/{meeting_id}/insights

Body:
{
  "corrections": {
    "speaker_labels": {
      "SPEAKER_00": "VDK",
      "SPEAKER_01": "John Smith"
    },
    "requirements": {
      "add": ["New requirement not detected"],
      "remove": ["Hallucinated requirement"]
    }
  }
}

Response 200:
{
  "status": "updated",
  "reprocessing_needed": false
}
```

---

## 14. Monitoring & Success Metrics

### Key Metrics

1. **Transcription Accuracy (WER - Word Error Rate)**
   - Target: <5%
   - Measure: Compare against manual transcription (sample 10%)

2. **Diarization Accuracy**
   - Target: >90% correct speaker assignment
   - Measure: Manual validation

3. **Extraction Precision**
   - Target: >85% of extracted items are correct
   - Measure: VDK feedback (thumbs up/down)

4. **Processing Time**
   - Target: <5 minutes for 1-hour meeting
   - Measure: Time from trigger to completion

5. **LLM Cost**
   - Target: <$0.50 per meeting
   - Measure: Token usage tracking

---

## 15. Success Criteria

**Pipeline is production-ready when:**

✅ **Accuracy:**
- [ ] Transcription WER <5% on clear audio
- [ ] Speaker diarization >90% correct
- [ ] LLM extraction precision >85%

✅ **Performance:**
- [ ] Process 1-hour meeting in <5 minutes
- [ ] Handle 10 concurrent processing jobs
- [ ] GPU utilization >80% during processing

✅ **Reliability:**
- [ ] 99% success rate (no crashes)
- [ ] Automatic retry on failures
- [ ] Data integrity (no lost transcripts)

✅ **Usability:**
- [ ] Clean, readable transcript output
- [ ] Structured JSON ready for downstream use
- [ ] Confidence scores for human review

---

## Conclusion

This **Meeting Data Processing Pipeline** transforms raw audio into a **gold mine of structured information**. By combining:
- **State-of-the-art transcription** (Whisper)
- **Speaker intelligence** (pyannote)
- **AI understanding** (GPT-4/Llama)

We get a **complete meeting object** that powers:
- Automatic client follow-ups (requirements pre-filled)
- Internal team briefings (summary + action items)
- Prototype generation (requirements → code)

**Next Steps:**
1. Approve this architecture
2. Begin Week 1: Transcription MVP
3. Test with 5 real VDK meetings
4. Iterate based on accuracy feedback

This is the **brain** of the entire system - get this right, and everything downstream becomes trivial.
