# ── Bot-Worker Docker Image ────────────────────────────────────────────────────
# Provides a complete headless-but-headed browser environment:
#   • Xvfb  — virtual 1920x1080 display (Chrome renders here, not visible on host)
#   • PulseAudio null-sink — virtual speaker (Chrome plays audio here, captured by FFmpeg)
#   • FFmpeg — records screen + audio to /recordings/{meeting_id}/
#   • x11vnc — optional VNC server so you can watch the browser live (debug)
#   • Playwright Chromium — the actual browser joining meetings
# ──────────────────────────────────────────────────────────────────────────────
FROM ubuntu:22.04

# Prevent apt from asking interactive questions
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Virtual display
    xvfb \
    x11vnc \
    # Virtual audio
    pulseaudio \
    pulseaudio-utils \
    # Screen + audio capture
    ffmpeg \
    # Python
    python3.11 \
    python3-pip \
    python3.11-venv \
    # Chrome dependencies
    wget \
    curl \
    gnupg \
    ca-certificates \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    # Fonts (avoid missing glyph errors on meeting pages)
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# ── Google Chrome ──────────────────────────────────────────────────────────────
# We use Google Chrome (not Chromium) because Teams/Zoom verify the Chrome
# user agent and some features degrade on Chromium builds.
RUN wget -q -O /tmp/chrome.deb \
      https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ────────────────────────────────────────────────────────────────
WORKDIR /app
# Copy requirements and entrypoint from bot-worker/
COPY bot-worker/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright and its browser binaries
RUN pip3 install playwright && playwright install chromium && playwright install-deps chromium

# ── Bot scripts ────────────────────────────────────────────────────────────────
# Copy all join scripts and the monitor from backend/ — they run unchanged inside the container.
COPY backend/simple_join.py backend/zoom_join.py backend/teams_join.py backend/meeting_monitor.py ./

# ── Recording output ───────────────────────────────────────────────────────────
RUN mkdir -p /recordings

# ── Entrypoint ─────────────────────────────────────────────────────────────────
COPY bot-worker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
