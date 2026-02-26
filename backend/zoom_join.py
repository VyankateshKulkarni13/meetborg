"""
Automated Zoom Meeting Join - Browser Automation
Handles Zoom web client join flow with camera/mic controls
"""
import asyncio
import argparse
from playwright.async_api import async_playwright
from meeting_monitor import monitor_and_complete

async def join_zoom_meeting(meeting_url: str, meeting_id: str = None,
                            api_url: str = "http://localhost:8000/api/v1",
                            api_secret: str = ""):
    """
    Join Zoom meeting automatically via web browser
    Handles: "Join from browser" link, camera/mic toggle, name input, join button
    """
    
    print("=" * 60)
    print("Automated Zoom Meeting Join Bot")
    print("=" * 60)
    print(f"Meeting: {meeting_url}")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("\n[INFO] Launching Chrome...")
        
        from pathlib import Path
        
        # Create user data directory for persistent browser profile
        user_data_dir = Path.home() / ".meetborg" / "chrome_profile"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Launch persistent context with args to bypass protocol handler dialogs
        import os
        docker_args = ["--no-sandbox", "--disable-dev-shm-usage"] if os.environ.get("DOCKER_ENV") == "1" else []
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            channel='chrome',
            args=docker_args + [
                '--disable-blink-features=AutomationControlled',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--disable-features=ExternalProtocolDialogInProductHelp',
                '--disable-external-intent-requests',
                '--no-first-run',
                '--no-default-browser-check',
                '--window-size=1280,720',
                '--window-position=100,50',
            ],
            permissions=['camera', 'microphone'],
            viewport={'width': 1280, 'height': 720},
            accept_downloads=False
        )
        
        print("[OK] Chrome launched!")
        
        # Create new page
        page = await context.new_page()

        # Force window size via CDP — overrides profile's saved maximized state
        try:
            cdp = await context.new_cdp_session(page)
            info = await cdp.send("Browser.getWindowForTarget")
            await cdp.send("Browser.setWindowBounds", {
                "windowId": info["windowId"],
                "bounds": {"left": 100, "top": 50, "width": 1280, "height": 720, "windowState": "normal"}
            })
            await cdp.detach()
        except Exception:
            pass  # CDP not available, window-size flag is our fallback

        # Convert Zoom meeting URL to web client URL
        # From: https://zoom.us/j/86010230348?pwd=abc123
        # To:   https://app.zoom.us/wc/join/86010230348?pwd=abc123
        print(f"\n[INFO] Original meeting URL: {meeting_url}")
        
        import re
        from urllib.parse import urlparse, parse_qs, urlencode
        
        # Extract Zoom meeting code and password from URL
        zoom_code = None
        password = None
        
        # Pattern 1: zoom.us/j/[CODE]?pwd=[PWD]
        match = re.search(r'zoom\.us/j/(\d+)', meeting_url)
        if match:
            zoom_code = match.group(1)
            # Extract password if present
            parsed = urlparse(meeting_url)
            params = parse_qs(parsed.query)
            if 'pwd' in params:
                password = params['pwd'][0]
        
        if zoom_code:
            # Construct direct web client URL
            web_client_url = f"https://app.zoom.us/wc/join/{zoom_code}"
            if password:
                web_client_url += f"?pwd={password}"
            
            print(f"[INFO] Converted to web client URL: {web_client_url}")
            meeting_url = web_client_url
        else:
            print("[WARN] Could not extract Zoom code, using original URL")
        
        print(f"\n[INFO] Navigating to Zoom web client: {meeting_url}")
        await page.goto(meeting_url, wait_until='networkidle', timeout=60000)
        
        # Wait for the join form to appear
        print("[INFO] Waiting for join form to load...")
        try:
            await page.wait_for_selector('button:has-text("Join")', timeout=30000)
            print("[OK] Join form loaded!")
        except:
            print("[WARN] Join form took longer than expected, continuing anyway...")
        
        current_url = page.url
        print(f"[INFO] Current URL: {current_url}")
        
        # Set up dialog handler for any browser-level dialogs (just in case)
        async def handle_dialog(dialog):
            print(f"[INFO] Browser dialog detected: {dialog.message}")
            await dialog.dismiss()
            print("[OK] Dialog dismissed")
        
        page.on("dialog", handle_dialog)
        
        # We're now directly on the web client page - no need for dialog dismissal or "Join from browser" click!
        print("\n[INFO] On Zoom web client page - ready to join!")
        
        # Step 1: Enter name
        print("\n[INFO] Looking for name input...")
        
        # Wait for name input to appear
        name_entered = False
        try:
            # Wait for the input field to be visible
            await page.wait_for_selector('input[type="text"]', state='visible', timeout=10000)
            print("[OK] Name input field found!")
            
            # Try to fill it
            name_input = page.locator('input[type="text"]').first
            await name_input.fill("Meeting Assistant")
            print("[OK] Name entered: Meeting Assistant")
            name_entered = True
            await page.wait_for_timeout(500)
        except Exception as e:
            print(f"[WARN] Could not find or fill name input: {e}")
            await page.screenshot(path='zoom_name_input_not_found.png')
        
        # ── Robust media-toggle helper ────────────────────────────────────────
        async def ensure_device_off(
            device: str,
            off_labels: list,   # text/aria that means device IS already off
            on_labels: list,    # text/aria that means device IS on (click to turn off)
            keyword: str,       # broad keyword: "video" or "audio"
            shortcut: str,      # keyboard shortcut last resort e.g. "Alt+V"
        ) -> bool:
            """
            Turn off camera or microphone with 3 attempts and 5 escalating strategies.
            Returns True if we can confirm it is OFF.
            """
            print(f"\n[INFO] Ensuring {device} is OFF...")

            for attempt in range(1, 4):
                await page.wait_for_timeout(800 * attempt)

                # ── Strategy 1 & 2: check/act via text label on buttons ──────
                # Is it already OFF?
                for label in off_labels:
                    for loc in [
                        page.locator(f'button:has-text("{label}")').first,
                        page.locator(f'button[aria-label*="{label}" i]').first,
                    ]:
                        try:
                            if await loc.count() > 0 and await loc.is_visible():
                                print(f"[OK] {device} already OFF (found '{label}')")
                                return True
                        except Exception:
                            pass

                # Try to click the ON-state button to turn it off
                clicked = False
                for label in on_labels:
                    for loc in [
                        page.locator(f'button:has-text("{label}")').first,
                        page.locator(f'button[aria-label*="{label}" i]').first,
                        page.locator(f'button[title*="{label}" i]').first,
                    ]:
                        try:
                            if await loc.count() > 0 and await loc.is_visible():
                                txt = (await loc.inner_text()).strip()
                                aria = await loc.get_attribute('aria-label') or ''
                                print(f"[DEBUG] Attempt {attempt}: clicking '{txt}' | aria='{aria}'")
                                await loc.click()
                                await page.wait_for_timeout(700)
                                clicked = True
                                break
                        except Exception:
                            pass
                    if clicked:
                        break

                # ── Strategy 3: broad keyword scan ───────────────────────────
                if not clicked:
                    for loc_str in [
                        f'button[aria-label*="{keyword}" i]',
                        f'button[data-tooltip*="{keyword}" i]',
                        f'button[title*="{keyword}" i]',
                    ]:
                        loc = page.locator(loc_str).first
                        try:
                            if await loc.count() > 0 and await loc.is_visible():
                                aria = (await loc.get_attribute('aria-label') or '').lower()
                                # Only click if it looks like an "on" state (not already off)
                                if not any(w in aria for w in ['start', 'enable', 'unmute', 'turn on']):
                                    print(f"[DEBUG] Attempt {attempt}: broad click [{loc_str}] aria='{aria}'")
                                    await loc.click()
                                    await page.wait_for_timeout(700)
                                    clicked = True
                                    break
                        except Exception:
                            pass

                # ── Strategy 4: JavaScript DOM click fallback ─────────────────
                if not clicked:
                    try:
                        clicked_js = await page.evaluate(f"""() => {{
                            const ON_WORDS = ['stop', 'turn off', 'disable', 'mute'];
                            for (const btn of document.querySelectorAll('button')) {{
                                const text = (btn.textContent + ' ' +
                                    (btn.getAttribute('aria-label') || '') +
                                    (btn.getAttribute('title') || '')).toLowerCase();
                                if (text.includes('{keyword}') &&
                                    ON_WORDS.some(w => text.includes(w))) {{
                                    btn.click();
                                    return true;
                                }}
                            }}
                            return false;
                        }}""")
                        if clicked_js:
                            print(f"[OK] {device} toggled via JavaScript DOM fallback")
                            await page.wait_for_timeout(700)
                            clicked = True
                    except Exception as e:
                        print(f"[DEBUG] JS fallback failed: {e}")

                # ── Strategy 5: keyboard shortcut (last resort on final attempt)
                if not clicked and attempt == 3:
                    print(f"[INFO] Trying keyboard shortcut {shortcut}...")
                    await page.keyboard.press(shortcut)
                    await page.wait_for_timeout(700)
                    clicked = True  # optimistically assume it worked

                # ── Verify toggle took effect ─────────────────────────────────
                if clicked:
                    await page.wait_for_timeout(400)
                    for label in off_labels:
                        for loc in [
                            page.locator(f'button:has-text("{label}")').first,
                            page.locator(f'button[aria-label*="{label}" i]').first,
                        ]:
                            try:
                                if await loc.count() > 0 and await loc.is_visible():
                                    print(f"[OK] {device} OFF confirmed (saw '{label}')")
                                    return True
                            except Exception:
                                pass
                    print(f"[INFO] Attempt {attempt}: clicked but not yet confirmed — retrying...")

            # All attempts exhausted
            print(f"[WARN] Could not confirm {device} is OFF after 3 attempts")
            try:
                await page.screenshot(path=f'zoom_{device.lower()}_failed.png')
                print(f"[INFO] Saved zoom_{device.lower()}_failed.png for debugging")
            except Exception:
                pass
            return False

        # ── Step 2: Turn off camera and microphone before joining ─────────────
        # Wait for the pre-join UI to fully render
        await page.wait_for_timeout(2500)

        camera_off = await ensure_device_off(
            device="Camera",
            off_labels=["Start Video", "Start My Video", "Turn On Video", "Turn on camera"],
            on_labels=["Stop Video", "Stop My Video", "Turn Off Video", "Turn off camera"],
            keyword="video",
            shortcut="Alt+V",
        )
        mic_off = await ensure_device_off(
            device="Microphone",
            off_labels=["Unmute", "Unmute Audio", "Start Audio", "Turn on microphone"],
            on_labels=["Mute", "Mute Audio", "Stop Audio", "Turn off microphone"],
            keyword="audio",
            shortcut="Alt+A",
        )

        if not camera_off:
            print("[WARN] Camera may still be ON — joining anyway")
        if not mic_off:
            print("[WARN] Microphone may still be ON — joining anyway")


        
        # Step 3: Click Join button
        print("\n[INFO] Looking for Join button...")
        
        join_clicked = False
        try:
            # Wait for Join button to be clickable
            await page.wait_for_selector('button:has-text("Join")', state='visible', timeout=10000)
            join_button = page.locator('button:has-text("Join")').first
            await join_button.click()
            print("[OK] Join button clicked!")
            join_clicked = True
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[WARN] Could not find or click Join button: {e}")
            await page.screenshot(path='zoom_join_failed.png')
            print("[INFO] Screenshot saved: zoom_join_failed.png")
        
        # Step 5: Check for waiting room or success
        await page.wait_for_timeout(3000)
        
        # Check if in waiting room
        waiting_room_text = await page.content()
        if 'waiting room' in waiting_room_text.lower() or 'please wait' in waiting_room_text.lower():
            print("\n" + "=" * 60)
            print("[INFO] In waiting room - waiting for host to admit you...")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[SUCCESS] Joined Zoom meeting!")
            print("=" * 60)
        
        # ── Monitor meeting until it ends ────────────────────────────────
        print("\n[INFO] Monitoring for meeting end...")
        await monitor_and_complete(
            page=page,
            context=context,
            platform="zoom",
            meeting_id=meeting_id,
            api_url=api_url,
            api_secret=api_secret,
        )
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zoom Meeting Bot")
    parser.add_argument("url", help="Meeting URL")
    parser.add_argument("--meeting-id", default=None, help="Meeting ID for completion callback")
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1")
    parser.add_argument("--api-secret", default="")
    args = parser.parse_args()

    result = asyncio.run(join_zoom_meeting(
        args.url,
        meeting_id=args.meeting_id,
        api_url=args.api_url,
        api_secret=args.api_secret,
    ))

    if result:
        print("\n[SUCCESS] Zoom automation completed!")
    else:
        print("\n[INFO] Check browser or screenshots")
