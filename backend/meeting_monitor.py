"""
Meeting End Monitor — stdlib only, no external dependencies.
Detects meeting end via cross-frame scanning and multiple signals.
"""
import asyncio
import json
import re
import time
import urllib.request
import urllib.error
from typing import Optional


# ── Teams call timer extraction ───────────────────────────────────────────────
# During an active call the frame text starts with a timer like '00:16' or '1:03:42'.
# The timer increments every second. When the host ends the call, it freezes or
# disappears. We use this to detect meeting end robustly.
_TIMER_RE = re.compile(r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b')

# Teams participant count patterns — e.g. '2 people', '1 person', '1 people'
_TEAMS_PARTICIPANT_RE = re.compile(r'(\d+)\s+(?:people|person|participant)')


def _extract_timer_seconds(frame_texts: list) -> Optional[int]:
    """Extract call timer as total seconds from any frame, or None if not found."""
    for _, text in frame_texts:
        m = _TIMER_RE.search(text)
        if m:
            groups = m.groups()
            if groups[2] is not None:  # H:MM:SS
                return int(groups[0]) * 3600 + int(groups[1]) * 60 + int(groups[2])
            else:  # MM:SS
                return int(groups[0]) * 60 + int(groups[1])
    return None


def _extract_teams_participant_count(frame_texts: list) -> Optional[int]:
    """Extract participant count from Teams frame text, or None if not found.
    
    Returns:
      - The number if found (e.g. '2 people' -> 2)
      - 0 if 'people' appears without a number (Teams removes the count when alone)
      - None if no participant indicator found at all
    """
    for _, text in frame_texts:
        m = _TEAMS_PARTICIPANT_RE.search(text)
        if m:
            return int(m.group(1))
        # Teams removes the number entirely when bot is alone:
        # '2 people' becomes just 'people' (no digit)
        # Check for 'people' NOT preceded by a digit
        if re.search(r'(?<!\d)\bpeople\b', text) and not _TEAMS_PARTICIPANT_RE.search(text):
            return 0  # no number = bot is alone
    return None


# ── End-phrase lists per platform ─────────────────────────────────────────────
_END_PHRASES = {
    "google_meet": [
        'you left the call', "you've left", 'the call has ended',
        'call ended', 'meeting ended', 'meeting has ended',
        'host ended', 'host has ended', 'return to home screen',
        'left the meeting', 'you left the meeting',
    ],
    "zoom": [
        'meeting is over', 'meeting has been ended', 'meeting has ended',
        'this meeting has ended', 'host has ended', 'host ended',
        'meeting ended', 'thank you for joining',
    ],
    "microsoft_teams": [
        'call ended', 'call has ended', 'the call has ended',
        'you left the meeting', 'you have left the meeting',
        'the meeting has ended', 'meeting has ended', 'meeting ended',
        'everyone has left', "you've left", 'you left the call',
        'left the call', 'left the meeting', 'call is over',
        'the call is over', 'your call has ended',
        # Teams shows these on the post-call screen or when alone
        'rate your call', 'how was your call', 'rate your call quality',
        'only one in the meeting', 'only one in this meeting',
        'you\'re the only one here',
        'waiting for others to join',
    ],
}

# ── JavaScript for detecting Rejoin button and special end elements ────────────
_JS_POSTJOIN_CHECK = """
() => {
    // Check all buttons and links for rejoin text
    const allEls = Array.from(document.querySelectorAll('button, a, [role="button"]'));
    for (const el of allEls) {
        const t = (el.innerText || el.textContent || '').toLowerCase().trim();
        if (t === 'rejoin' || t === 're-join' || t.startsWith('rejoin ') || t === 'rejoin call') {
            return 'rejoin:' + t;
        }
    }
    // Teams-specific call-ended data-tid
    const endEl = document.querySelector(
        '[data-tid="call-ended-page"], [data-tid*="call-ended"], ' +
        '[data-tid="post-call-page"], [data-tid="prejoin-retry"]'
    );
    if (endEl) return 'tid:' + (endEl.getAttribute('data-tid') || 'ended');
    return '';
}
"""

# ── Active-selector lists (used only to CONFIRM we're in — not for exit) ──────
_ACTIVE_SELECTORS = {
    "google_meet": [
        '[aria-label*="Leave call" i]',
        '[data-tooltip*="Leave call" i]',
        '[aria-label*="Turn off microphone" i]',
    ],
    "zoom": [
        '[aria-label*="Leave" i]',
        '#footer-leave-btn',
    ],
    # For Teams we only use these to CONFIRM we're in – exit logic uses frames
    "microsoft_teams": [
        'button:has-text("Leave")',
        '[data-tid="toggle-mute"]',
        '[aria-label*="mute" i]',
    ],
}

# ── URL domain checks ──────────────────────────────────────────────────────────
_ACTIVE_URL_CHECK = {
    "google_meet":      lambda url: "meet.google.com/" in url,
    "zoom":             lambda url: "app.zoom.us/wc" in url,
    "microsoft_teams":  lambda url: "teams.live.com" in url or "teams.microsoft.com" in url,
}


async def _scan_frame(frame, platform: str, debug: bool = False) -> str:
    """
    Scan a single frame for meeting-end signals.
    Returns a reason string if ended, '' otherwise.
    """
    try:
        body = await frame.evaluate(
            "document.body ? document.body.innerText : ''"
        )
    except Exception:
        return ""

    body_lower = body.lower()

    if debug and body_lower.strip():
        snippet = body_lower.replace("\n", " ")[:200]
        print(f"[MONITOR]   frame text: {snippet!r}")

    # Text phrase scan
    for phrase in _END_PHRASES.get(platform, []):
        if phrase in body_lower:
            return f"text:{phrase}"

    # Rejoin button + special elements scan
    try:
        reason = await frame.evaluate(_JS_POSTJOIN_CHECK)
        if reason:
            return f"js:{reason}"
    except Exception:
        pass

    return ""


async def _check_all_frames(page, platform: str, debug: bool = False) -> str:
    """
    Scan ALL frames (main + iframes) for end signals.
    Teams loads content in sub-frames — this is critical for Teams detection.
    """
    frames = page.frames
    if debug:
        print(f"[MONITOR] Scanning {len(frames)} frame(s)")

    for frame in frames:
        try:
            reason = await _scan_frame(frame, platform, debug=debug)
            if reason:
                frame_url = frame.url[:50] if frame.url else "?"
                return f"[frame:{frame_url}] {reason}"
        except Exception:
            pass
    return ""


async def _get_all_frame_text(page) -> list:
    """Return list of (frame_url, body_lower) for all frames with non-empty bodies."""
    results = []
    for frame in page.frames:
        try:
            body = await frame.evaluate(
                "document.body ? document.body.innerText : ''"
            )
            if body and body.strip():
                results.append((frame.url or "", body.lower()))
        except Exception:
            pass
    return results


def _teams_signature_present(frame_texts: list) -> bool:
    """True if Teams in-meeting control bar keywords are found in any frame."""
    for _, text in frame_texts:
        found = sum(1 for w in _TEAMS_SIGNATURE_WORDS if w in text)
        if found >= 3:  # at least 3 of {mic, camera, share, leave}
            return True
    return False


async def _active_selector_present(page, platform: str) -> bool:
    """Returns True if any active-meeting control is found on the page."""
    for sel in _ACTIVE_SELECTORS.get(platform, []):
        try:
            count = await page.locator(sel).count()
            if count > 0:
                print(f"[MONITOR] Active selector matched: {sel}")
                return True
        except Exception:
            pass
    return False


async def _is_meeting_active(
    page, platform: str, seen_active_selector: bool, tick: int
) -> tuple:
    """
    Returns (is_active: bool, reason: str).

    Checks:
      1. page.is_closed()
      2. URL left meeting domain
      3. Cross-frame text / DOM detection (every poll)
      4. Active-selector disappeared (only if previously confirmed in-meeting)
    """
    # Signal 1 — browser closed
    try:
        if page.is_closed():
            return False, "browser_closed"
    except Exception:
        return False, "context_lost"

    url = page.url.lower()
    print(f"[MONITOR] URL: {url[:80]}")

    # Signal 2 — URL left meeting domain
    url_checker = _ACTIVE_URL_CHECK.get(platform)
    if url_checker and not url_checker(url):
        return False, f"url_left_domain:{url[:60]}"

    # Signal 3 — Log page title (useful for Teams debugging)
    try:
        title = await page.title()
        if title:
            print(f"[MONITOR] Page title: {title}")
    except Exception:
        pass

    # Signal 4 — Cross-frame text / DOM detection
    # Enable verbose frame debug on first 3 polls and every 10th poll
    debug_frames = (tick < 3) or (tick % 10 == 0)
    reason = await _check_all_frames(page, platform, debug=debug_frames)
    if reason:
        return False, reason

    # Signal 5 — active selector disappeared (after we confirmed in-meeting)
    if seen_active_selector:
        still_active = await _active_selector_present(page, platform)
        if not still_active:
            return False, "controls_disappeared"

    return True, ""


def _mark_completed(meeting_id: str, api_url: str, api_secret: str) -> bool:
    """POST /meetings/{id}/complete using stdlib urllib."""
    if not meeting_id:
        print("[MONITOR] No meeting_id — skipping backend update")
        return False

    endpoint = f"{api_url}/meetings/{meeting_id}/complete"
    headers = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({}).encode("utf-8")

    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                endpoint, data=payload, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 204):
                    print(f"[MONITOR] ✅ Meeting {meeting_id} marked COMPLETED")
                    return True
                print(f"[MONITOR] Backend returned HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            print(f"[MONITOR] HTTP {e.code} on attempt {attempt}: {e.reason}")
        except Exception as e:
            print(f"[MONITOR] Attempt {attempt} error: {e}")
        time.sleep(2 ** attempt)

    print("[MONITOR] ⚠ Could not reach backend after 3 attempts")
    return False


async def monitor_and_complete(
    page,
    context,
    platform: str,
    meeting_id: Optional[str],
    api_url: str = "http://localhost:8000/api/v1",
    api_secret: str = "",
    poll_interval: int = 10,
    max_hours: int = 4,
):
    """
    Monitor a meeting for end signals. When ended:
      1. Closes the browser context
      2. Calls /meetings/{id}/complete on the backend
    """
    max_polls = int((max_hours * 3600) / poll_interval)

    print(f"\n[MONITOR] Watching {platform} (ID: {meeting_id or 'None'})")
    print(f"[MONITOR] Poll every {poll_interval}s · max {max_hours}h")

    # Wait for page to fully settle inside the meeting
    await asyncio.sleep(8)

    # Confirm we are inside the meeting
    seen_active_selector = await _active_selector_present(page, platform)
    if seen_active_selector:
        print("[MONITOR] Active meeting controls confirmed — tracking end signals")
    else:
        print("[MONITOR] Active controls not found yet — relying on frame/text signals")

    # Teams-specific: track call timer for freeze/disappearance
    teams_timer_confirmed = False   # True once we've seen the timer
    teams_last_timer: Optional[int] = None
    teams_timer_frozen_count = 0

    # Teams-specific: track participant count (bot alone = meeting over)
    teams_alone_count = 0           # consecutive polls where participant count <= 1
    teams_last_participant_count: Optional[int] = None

    ended = False
    reason = ""

    for tick in range(max_polls):
        try:
            await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            reason = "cancelled"
            break

        # ── Teams call-timer freeze/disappearance detection ─────────────────
        if platform == "microsoft_teams":
            ft = await _get_all_frame_text(page)
            timer_secs = _extract_timer_seconds(ft)

            if timer_secs is not None:
                if not teams_timer_confirmed:
                    teams_timer_confirmed = True
                    teams_last_timer = timer_secs
                    print(f"[MONITOR] Teams call timer confirmed: {timer_secs}s")
                else:
                    if timer_secs != teams_last_timer:
                        # Timer is advancing — meeting active
                        teams_timer_frozen_count = 0
                        teams_last_timer = timer_secs
                    else:
                        # Timer value unchanged since last poll
                        teams_timer_frozen_count += 1
                        print(f"[MONITOR] Teams timer frozen at {timer_secs}s ({teams_timer_frozen_count}/3 polls)")
                        if teams_timer_frozen_count >= 3:
                            reason = f"teams_timer_frozen_at_{timer_secs}s"
                            ended = True
                            break
            elif teams_timer_confirmed:
                # Timer was present before but is now gone — strong end signal
                print("[MONITOR] Teams call timer disappeared")
                reason = "teams_timer_disappeared"
                ended = True
                break

            # ── Teams participant count detection ─────────────────────────────
            # Frame text shows '2 people', '3 people', etc.
            # When host leaves, it drops to '1 person' or '1 people' — bot is alone.
            participant_count = _extract_teams_participant_count(ft)
            if participant_count is not None:
                teams_last_participant_count = participant_count
                if participant_count <= 1:
                    teams_alone_count += 1
                    print(f"[MONITOR] Teams: bot appears alone ({participant_count} participant) [{teams_alone_count}/2 polls]")
                    if teams_alone_count >= 2:
                        reason = f"teams_bot_alone_{participant_count}_participants"
                        ended = True
                        break
                else:
                    teams_alone_count = 0  # reset — others are still in

            # Log participant count and frame text every poll for debugging
            if tick < 5 or tick % 5 == 0:
                for _, text in ft:
                    snippet = text.replace('\n', ' ')[:200]
                    print(f"[MONITOR]   frame text: {snippet!r}")

        # ── Generic end-signal checks ───────────────────────────────────────
        active, reason = await _is_meeting_active(
            page, platform, seen_active_selector, tick
        )

        if not active:
            print(f"[MONITOR] Meeting ended — reason: {reason}")
            ended = True
            break

        # Re-check whether we've now confirmed the active selector
        if not seen_active_selector:
            seen_active_selector = await _active_selector_present(page, platform)
            if seen_active_selector:
                print("[MONITOR] Now tracking active meeting controls")

        # Progress log every 5 minutes
        if (tick + 1) % max(1, 300 // poll_interval) == 0:
            elapsed_min = ((tick + 1) * poll_interval) // 60
            print(f"[MONITOR] Still in meeting ({elapsed_min} min elapsed)")

    if not ended:
        print(f"[MONITOR] Max duration ({max_hours}h) reached — forcing close")

    # ── Close browser ──────────────────────────────────────────────────────────
    try:
        if not page.is_closed():
            await context.close()
            print("[MONITOR] Browser closed")
    except Exception as e:
        print(f"[MONITOR] Browser close: {e}")

    # ── Notify backend ─────────────────────────────────────────────────────────
    if meeting_id:
        _mark_completed(meeting_id, api_url, api_secret)
