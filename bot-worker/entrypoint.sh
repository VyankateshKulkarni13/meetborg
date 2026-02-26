#!/bin/bash
# ── Bot-Worker Entrypoint ──────────────────────────────────────────────────────
# Boots virtual display + virtual audio, starts FFmpeg recording, runs the
# correct meeting bot script, then cleans up when the meeting ends.
#
# Required env vars (passed by `docker run -e ...`):
#   MEETING_URL  — full meeting URL
#   MEETING_ID   — UUID from the backend DB
#   PLATFORM     — google_meet | zoom | microsoft_teams
#   API_URL      — backend API base (e.g. http://host.docker.internal:8000/api/v1)
#   API_SECRET   — INTERNAL_BOT_SECRET from backend .env
#
# Optional env vars:
#   VNC_ENABLED  — true to start x11vnc on :5900 for live debugging
#   RECORD_VIDEO — true to also record the screen as screen.mkv (audio always recorded)
# ──────────────────────────────────────────────────────────────────────────────
set -e

# Validate required env vars
for var in MEETING_URL MEETING_ID PLATFORM API_URL API_SECRET; do
    if [ -z "${!var}" ]; then
        echo "[ERROR] Required env var '$var' is not set"
        exit 1
    fi
done

echo "============================================================"
echo " Bot-Worker Container Starting"
echo " Platform : $PLATFORM"
echo " Meeting  : $MEETING_ID"
echo "============================================================"

# ── Step 1: Virtual Display (Xvfb) ────────────────────────────────────────────
# Chrome renders its full headed UI to this virtual framebuffer.
# Display :99 at 1920x1080 with 24-bit colour.
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
export DISPLAY=:99
echo "[INFO] Xvfb started (PID: $XVFB_PID, DISPLAY=:99)"
sleep 1  # let Xvfb stabilise

# ── Step 2: Virtual Audio (PulseAudio null-sink) ───────────────────────────────
# PulseAudio creates a software "speaker". Chrome outputs meeting audio here.
# FFmpeg records from the monitor side of this sink.
# We run PulseAudio in system mode to avoid D-Bus user session issues in Docker.
mkdir -p /tmp/pulse-runtime
export PULSE_RUNTIME_PATH=/tmp/pulse-runtime

pulseaudio \
    --start \
    --exit-idle-time=-1 \
    --daemonize=true \
    --log-level=error

# Load a null output sink (virtual speaker) and set it as the default
pactl load-module module-null-sink sink_name=VirtualSink \
      sink_properties=device.description=VirtualSpeaker
pactl set-default-sink VirtualSink
echo "[INFO] PulseAudio null-sink started (VirtualSink)"
sleep 1  # let PulseAudio stabilise

# ── Step 3: Optional VNC (debugging) ─────────────────────────────────────────
# Set VNC_ENABLED=true when running to watch the bot live from your machine.
# Connect with any VNC client to localhost:5900.
if [ "${VNC_ENABLED:-false}" = "true" ]; then
    x11vnc -display :99 -nopw -forever -shared -quiet &
    echo "[INFO] VNC server started on port 5900 — connect with any VNC viewer"
fi

# ── Step 4: Create recording directory ───────────────────────────────────────
RECORDING_DIR="/recordings/${MEETING_ID}"
mkdir -p "$RECORDING_DIR"
echo "[INFO] Recording output: $RECORDING_DIR"

# ── Step 5: Start FFmpeg audio capture ───────────────────────────────────────
# Captures EXACTLY what Chrome plays through the PulseAudio virtual sink.
# Output: 16kHz mono WAV — the exact format faster-whisper expects.
# No codec conversion needed later.
ffmpeg -y \
    -f pulse \
    -i VirtualSink.monitor \
    -ar 16000 \
    -ac 1 \
    -c:a pcm_s16le \
    "${RECORDING_DIR}/audio.wav" \
    2>"${RECORDING_DIR}/ffmpeg_audio.log" &
FFMPEG_AUDIO_PID=$!
echo "[INFO] FFmpeg audio capture started (PID: $FFMPEG_AUDIO_PID)"

# ── Step 6: Optional screen video capture ────────────────────────────────────
# Records the entire virtual display as a video. Useful for playback / review.
# Disabled by default to save disk space — set RECORD_VIDEO=true to enable.
FFMPEG_VIDEO_PID=""
if [ "${RECORD_VIDEO:-false}" = "true" ]; then
    ffmpeg -y \
        -f x11grab \
        -r 15 \
        -s 1920x1080 \
        -i :99 \
        -c:v libx264 \
        -preset ultrafast \
        -crf 30 \
        "${RECORDING_DIR}/screen.mkv" \
        2>"${RECORDING_DIR}/ffmpeg_video.log" &
    FFMPEG_VIDEO_PID=$!
    echo "[INFO] FFmpeg screen capture started (PID: $FFMPEG_VIDEO_PID)"
fi

# Write metadata file
cat > "${RECORDING_DIR}/metadata.json" <<EOF
{
  "meeting_id": "${MEETING_ID}",
  "platform": "${PLATFORM}",
  "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# ── Step 7: Run meeting bot script ────────────────────────────────────────────
# The existing join scripts run unchanged. Playwright auto-detects DISPLAY=:99
# and Chrome outputs audio to PulseAudio's VirtualSink via PULSE_SINK env var.
export PULSE_SINK=VirtualSink
export DOCKER_ENV=1  # tells the script to add --no-sandbox to Chrome args

BOT_EXIT_CODE=0
case "$PLATFORM" in
    "google_meet")
        echo "[INFO] Launching Google Meet bot..."
        python3 simple_join.py "$MEETING_URL" \
            --meeting-id "$MEETING_ID" \
            --api-url "$API_URL" \
            --api-secret "$API_SECRET" || BOT_EXIT_CODE=$?
        ;;
    "zoom")
        echo "[INFO] Launching Zoom bot..."
        python3 zoom_join.py "$MEETING_URL" \
            --meeting-id "$MEETING_ID" \
            --api-url "$API_URL" \
            --api-secret "$API_SECRET" || BOT_EXIT_CODE=$?
        ;;
    "microsoft_teams")
        echo "[INFO] Launching Teams bot..."
        python3 teams_join.py "$MEETING_URL" \
            --meeting-id "$MEETING_ID" \
            --api-url "$API_URL" \
            --api-secret "$API_SECRET" || BOT_EXIT_CODE=$?
        ;;
    *)
        echo "[ERROR] Unknown platform: $PLATFORM"
        BOT_EXIT_CODE=1
        ;;
esac

# ── Step 8: Cleanup ───────────────────────────────────────────────────────────
echo "[INFO] Bot exited (code: $BOT_EXIT_CODE). Stopping recorders..."

# Stop FFmpeg gracefully — SIGTERM triggers final file flush
[ -n "$FFMPEG_AUDIO_PID" ] && kill -SIGTERM $FFMPEG_AUDIO_PID 2>/dev/null && wait $FFMPEG_AUDIO_PID 2>/dev/null || true
[ -n "$FFMPEG_VIDEO_PID" ] && kill -SIGTERM $FFMPEG_VIDEO_PID 2>/dev/null && wait $FFMPEG_VIDEO_PID 2>/dev/null || true

# Append end time to metadata
cat >> "${RECORDING_DIR}/metadata.json" <<EOF

{
  "end_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "bot_exit_code": $BOT_EXIT_CODE
}
EOF

echo "[INFO] Recording files:"
ls -lh "${RECORDING_DIR}/"

# Stop Xvfb
kill $XVFB_PID 2>/dev/null || true

echo "============================================================"
echo " Bot-Worker Complete"
echo " Recording: $RECORDING_DIR"
echo "============================================================"

exit $BOT_EXIT_CODE
