"""
Automated Microsoft Teams Meeting Join - Browser Automation
Handles Teams web client join flow with camera/mic controls

Supports URL types:
  1. Direct join:   https://teams.live.com/meet/{code}?p={passcode}&anon=true
  2. Launch redirect: https://teams.live.com/light-meetings/launch?...&coords=BASE64_JSON
  3. Classic Teams:  https://teams.microsoft.com/l/meetup-join/...
"""
import asyncio
import json
import base64
import re
from urllib.parse import urlparse, parse_qs, unquote
from playwright.async_api import async_playwright


def extract_teams_join_url(original_url: str) -> str:
    """
    Parse any Teams URL variant and return the best direct join URL.

    - light-meetings/launch: decode 'coords' Base64 JSON -> use meetingUrl
    - teams.live.com/meet/{code}: use as-is (ensure anon=true params)
    - teams.microsoft.com classic: use as-is
    """
    parsed = urlparse(original_url)

    # ── Case 1: Launch-redirect URL ──────────────────────────────────────────
    if "light-meetings/launch" in parsed.path:
        qs = parse_qs(parsed.query)
        coords_raw = qs.get("coords", [None])[0]
        if coords_raw:
            try:
                # URL-decode then base64-decode
                coords_decoded = unquote(coords_raw)
                # Add padding if needed
                padding = 4 - len(coords_decoded) % 4
                if padding != 4:
                    coords_decoded += "=" * padding
                coords_json = json.loads(base64.b64decode(coords_decoded))
                meeting_url = coords_json.get("meetingUrl", "")
                meeting_code = coords_json.get("meetingCode", "")
                passcode = coords_json.get("passcode", "")

                if meeting_url:
                    print(f"[INFO] Decoded launch URL -> meetingCode={meeting_code}")
                    # Ensure essential params are present
                    if "anon=true" not in meeting_url:
                        sep = "&" if "?" in meeting_url else "?"
                        meeting_url += f"{sep}anon=true"
                    if "launchType=web" not in meeting_url:
                        meeting_url += "&launchType=web"
                    if "lightExperience=true" not in meeting_url:
                        meeting_url += "&lightExperience=true"
                    return meeting_url

                # Fallback: reconstruct from code + passcode
                if meeting_code:
                    url = f"https://teams.live.com/meet/{meeting_code}?anon=true&launchType=web&lightExperience=true"
                    if passcode:
                        url += f"&p={passcode}"
                    return url
            except Exception as e:
                print(f"[WARN] Could not decode coords param: {e}")

        print("[WARN] Could not parse launch URL, using original")
        return original_url

    # ── Case 2: teams.live.com/meet/{code} — already direct ─────────────────
    if "teams.live.com/meet/" in original_url:
        # Make sure anon / lightExperience flags are present for web join
        url = original_url
        if "anon=true" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}anon=true"
        if "lightExperience=true" not in url:
            url += "&lightExperience=true"
        if "launchType=web" not in url:
            url += "&launchType=web"
        return url

    # ── Case 3: Classic teams.microsoft.com URL ──────────────────────────────
    return original_url


async def toggle_off(page, candidate_selectors: list[tuple[str, str]], label: str) -> bool:
    """
    Try each selector; if the element is visible and is a toggle currently ON,
    click it. Returns True when successfully toggled (or already off).
    """
    for selector, note in candidate_selectors:
        try:
            loc = page.locator(selector).first
            if await loc.count() == 0:
                continue
            if not await loc.is_visible():
                continue

            # Read aria attributes to determine ON/OFF state
            aria_pressed = await loc.get_attribute("aria-pressed")
            aria_checked = await loc.get_attribute("aria-checked")
            aria_label   = (await loc.get_attribute("aria-label") or "").lower()
            btn_text     = (await loc.inner_text()).strip().lower()

            print(f"[DEBUG] {label} candidate found via '{note}': "
                  f"aria-pressed={aria_pressed}, aria-checked={aria_checked}, "
                  f"text='{btn_text}', label='{aria_label}'")

            # Determine if currently ON (we want to turn OFF)
            is_on = (
                aria_pressed == "true"
                or aria_checked == "true"
                # Toggle switch visual state
                or "turn off" in aria_label
                or "stop" in aria_label
                or "disable" in aria_label
            )
            # Also treat unknown state as ON conservatively
            if aria_pressed is None and aria_checked is None and "don't" not in aria_label:
                is_on = True  # assume on if we don't know

            if is_on:
                await loc.click()
                await page.wait_for_timeout(700)
                print(f"[OK] {label} toggled OFF")
                return True
            else:
                print(f"[INFO] {label} already OFF")
                return True
        except Exception as e:
            print(f"[DEBUG] Selector '{selector}' failed: {e}")
            continue

    return False


async def join_teams_meeting(meeting_url: str):
    """
    Join a Microsoft Teams meeting automatically via the web browser.
    Steps: parse URL → navigate → enter name → turn off camera → mute mic → join
    """
    print("=" * 60)
    print("Automated Microsoft Teams Meeting Join Bot")
    print("=" * 60)
    print(f"Original URL: {meeting_url}")

    # ── Resolve the best direct join URL ────────────────────────────────────
    join_url = extract_teams_join_url(meeting_url)
    print(f"[INFO] Resolved join URL: {join_url}")
    print("=" * 60)

    async with async_playwright() as p:
        from pathlib import Path

        user_data_dir = Path.home() / ".meetborg" / "chrome_profile_teams"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        print("\n[INFO] Launching Chrome...")
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-features=ExternalProtocolDialogInProductHelp",
                "--window-size=1280,720",
                "--window-position=100,50",
            ],
            permissions=["camera", "microphone"],
            viewport={"width": 1280, "height": 720},
            accept_downloads=False,
        )
        print("[OK] Chrome launched!")

        page = await context.new_page()

        # Handle any browser-level dialogs
        page.on("dialog", lambda d: asyncio.ensure_future(d.dismiss()))

        # ── Navigate ─────────────────────────────────────────────────────────
        print(f"\n[INFO] Navigating to Teams web client...")
        await page.goto(join_url, wait_until="domcontentloaded", timeout=60000)

        # Wait for the pre-join page to settle
        print("[INFO] Waiting for pre-join page to load...")
        try:
            await page.wait_for_selector(
                'input[placeholder*="name" i], input[data-tid*="prejoin" i]',
                state="visible",
                timeout=30000,
            )
            print("[OK] Pre-join page loaded!")
        except Exception:
            print("[WARN] Name input took long, continuing anyway...")
            await page.screenshot(path="teams_prejoin_load.png")

        await page.wait_for_timeout(1500)  # Let camera/mic toggles render

        # ── Step 1: Enter name ───────────────────────────────────────────────
        print("\n[INFO] Entering name...")
        name_entered = False
        name_selectors = [
            'input[placeholder*="name" i]',
            'input[data-tid*="name" i]',
            'input[aria-label*="name" i]',
            'input[type="text"]',
        ]
        for sel in name_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click()
                    # Select all existing text and replace
                    await page.keyboard.press("Control+A")
                    await loc.fill("Meeting Assistant")
                    # Dismiss the tooltip by pressing Tab
                    await page.keyboard.press("Tab")
                    print(f"[OK] Name entered via '{sel}'")
                    name_entered = True
                    await page.wait_for_timeout(500)
                    break
            except Exception as e:
                print(f"[DEBUG] Name selector '{sel}' failed: {e}")

        if not name_entered:
            print("[WARN] Could not enter name")
            await page.screenshot(path="teams_name_not_found.png")

        # ── Step 2: Turn camera OFF ──────────────────────────────────────────
        print("\n[INFO] Turning camera OFF...")
        camera_selectors = [
            # Toggle button next to video preview (lightExperience)
            ('[data-tid="toggle-video"]',                           "data-tid toggle-video"),
            ('[aria-label*="camera" i]',                           "aria-label camera"),
            ('[aria-label*="video" i][role="button"]',             "aria-label video button"),
            ('[aria-label*="Turn off camera" i]',                  "aria-label Turn off camera"),
            ('[aria-label*="Stop video" i]',                       "aria-label Stop video"),
            # Generic toggle switches in pre-join
            ('button[data-tid*="video" i]',                       "data-tid video button"),
            # SVG icon buttons — Teams uses label on parent
            ('div[data-tid*="video" i] button',                   "div>button data-tid video"),
        ]
        cam_ok = await toggle_off(page, camera_selectors, "Camera")
        if not cam_ok:
            print("[WARN] Could not toggle camera — saving screenshot")
            await page.screenshot(path="teams_camera_not_found.png")

        # ── Step 3: Mute microphone (or choose "Don't use audio") ────────────
        print("\n[INFO] Muting microphone...")
        mic_selectors = [
            ('[data-tid="toggle-mute"]',                           "data-tid toggle-mute"),
            ('[data-tid*="microphone" i]',                        "data-tid microphone"),
            ('[aria-label*="microphone" i]',                      "aria-label microphone"),
            ('[aria-label*="mute" i]:not([aria-label*="unmute" i])', "aria-label mute"),
            ('[aria-label*="audio" i]',                           "aria-label audio"),
            ('button[data-tid*="audio" i]',                       "data-tid audio button"),
        ]
        mic_ok = await toggle_off(page, mic_selectors, "Microphone")

        if not mic_ok:
            # Fallback: select "Don't use audio" radio button
            print("[INFO] Trying 'Don't use audio' radio button as fallback...")
            try:
                dont_use = page.locator(
                    "text=Don't use audio, input[type='radio'] + label:has-text(\"Don\"), "
                    "[aria-label*=\"don't use audio\" i]"
                ).first
                if await dont_use.count() > 0 and await dont_use.is_visible():
                    await dont_use.click()
                    print("[OK] Selected 'Don't use audio'")
                    mic_ok = True
                else:
                    # broader search
                    radio = page.locator("label, div, span").filter(has_text="Don't use audio").first
                    if await radio.count() > 0:
                        await radio.click()
                        print("[OK] Selected 'Don't use audio' (broad match)")
                        mic_ok = True
            except Exception as e:
                print(f"[WARN] Could not select Don't use audio: {e}")

            if not mic_ok:
                await page.screenshot(path="teams_mic_not_found.png")
                print("[INFO] Screenshot saved: teams_mic_not_found.png")

        # ── Step 4: Click "Join now" ─────────────────────────────────────────
        print("\n[INFO] Looking for 'Join now' button...")
        await page.wait_for_timeout(500)

        join_selectors = [
            'button:has-text("Join now")',
            '[data-tid*="prejoin-join-button" i]',
            '[aria-label*="join now" i]',
            'button:has-text("Join")',
            '[data-tid*="join" i]',
        ]

        join_clicked = False
        for sel in join_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    btn_text = await loc.inner_text()
                    print(f"[DEBUG] Clicking join button: '{btn_text.strip()}' via '{sel}'")
                    await loc.click()
                    join_clicked = True
                    print("[OK] Clicked 'Join now'!")
                    await page.wait_for_timeout(3000)
                    break
            except Exception as e:
                print(f"[DEBUG] Join selector '{sel}' failed: {e}")

        if not join_clicked:
            print("[WARN] Could not find Join button")
            await page.screenshot(path="teams_join_failed.png")
            print("[INFO] Screenshot saved: teams_join_failed.png")

        # ── Step 5: Detect waiting room ──────────────────────────────────────
        await page.wait_for_timeout(3000)
        page_content = await page.content()

        waiting_phrases = ["waiting for someone to let you in", "waiting room", "waiting to be admitted"]
        if any(phrase in page_content.lower() for phrase in waiting_phrases):
            print("\n" + "=" * 60)
            print("[INFO] In waiting room — waiting for host to admit you...")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[SUCCESS] Joined Teams meeting!")
            print("=" * 60)

        print("\n[INFO] Browser will stay open — close it manually when done.")

        # Keep browser alive
        try:
            while True:
                await page.wait_for_timeout(60000)
        except KeyboardInterrupt:
            print("\n[INFO] Closing browser...")
            await context.close()
            return True
        except Exception:
            return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://teams.live.com/meet/1234567890?anon=true"
        print("[WARN] No URL provided, using placeholder")

    result = asyncio.run(join_teams_meeting(url))
    if result:
        print("\n[SUCCESS] Teams automation completed!")
    else:
        print("\n[INFO] Check browser or screenshots for details")
