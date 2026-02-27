
"""
Automated Microsoft Teams Join - Browser Automation
"""
import asyncio
import argparse
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright
from meeting_monitor import monitor_and_complete

async def join_teams_meeting(meeting_url: str, meeting_id: str = None,
                            api_url: str = "http://localhost:8000/api/v1",
                            api_secret: str = ""):
    print("=" * 60)
    print("Automated Microsoft Teams Join Bot")
    print("=" * 60)
    print(f"Meeting: {meeting_url}")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Create user data directory for persistent browser profile
        user_data_dir = Path.home() / ".meetborg" / "chrome_profile"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        docker_args = ["--no-sandbox", "--disable-dev-shm-usage"] if os.environ.get("DOCKER_ENV") == "1" else []
        
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            channel='chrome',
            args=docker_args + [
                '--disable-blink-features=AutomationControlled',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--window-size=1280,720',
                '--window-position=100,50',
            ],
            permissions=['camera', 'microphone'],
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        print("[OK] Chrome launched!")
        page = await context.new_page()
        
        # Help Teams bypass the "Open app" popup
        print(f"\n[INFO] Navigating to meeting: {meeting_url}")
        await page.goto(meeting_url, wait_until='domcontentloaded')
        
        # 1. Handle "Open in Teams app" prompt
        print("[INFO] Handling launcher page...")
        try:
            # Click "Continue on this browser"
            selectors = [
                 'button[data-tid="joinOnWeb"]', 
                 'button:has-text("Continue on this browser")',
                 'button:has-text("Join on the web instead")',
                 'button[data-tid="launch-meeting-join-web-button"]'
            ]
            
            clicked_launcher = False
            for _ in range(5): # retry for 5 seconds
                for sel in selectors:
                    try:
                        if await page.is_visible(sel):
                            await page.click(sel)
                            print(f"[SUCCESS] Clicked browser join button")
                            clicked_launcher = True
                            break
                    except:
                        pass
                if clicked_launcher: break
                await asyncio.sleep(1)
        except Exception as e:
            print(f"[WARN] Launcher handling skipped/failed: {e}")

        # 2. Wait for Pre-join screen
        print("[INFO] Waiting for pre-join screen...")
        await asyncio.sleep(5)
        
        # STEP 3: Enter display name
        try:
             # Wait for name input
             name_input = await page.wait_for_selector(
                 'input[placeholder="Type your name"], input[data-tid="prejoin-display-name-input"]', 
                 timeout=15000
             )
             if name_input:
                 print(f"[INFO] Entering name: Meeting Assistant")
                 await name_input.fill("Meeting Assistant")
                 await asyncio.sleep(1)
             else:
                 print("[INFO] Name input not found (maybe logged in)")
        except Exception as e:
            print(f"[WARN] Name input issue: {e}")

        # STEP 4: Audio/Video Handling
        print("[INFO] Configuring devices...")
        # Teams often has toggles for camera/mic on the pre-join screen
        try:
            # JavaScript to find and turn off if they are on
            await page.evaluate('''() => {
                const buttons = Array.from(document.querySelectorAll('button[role="switch"], div[role="switch"], button'));
                for (const b of buttons) {
                    const label = (b.getAttribute('aria-label') || b.innerText || '').toLowerCase();
                    if ((label.includes('camera') || label.includes('mic')) && !label.includes('device')) {
                        const isChecked = b.getAttribute('aria-checked') === 'true';
                        if (isChecked) b.click();
                    }
                }
            }''')
            print("[OK] Devices toggled (if found)")
        except Exception as e:
            print(f"[WARN] Device toggle error: {e}")

        # STEP 5: Click Join
        print("[INFO] Looking for Join button...")
        try:
            join_btn = await page.wait_for_selector(
                'button[data-tid="prejoin-join-button"], button:has-text("Join now")', 
                timeout=10000
            )
            if join_btn:
                print("[SUCCESS] Clicking 'Join now'...")
                await join_btn.click()
                await asyncio.sleep(5)
            else:
                print("[ERR] Join button not found!")
        except Exception as e:
             print(f"[ERR] Failed to click Join: {e}")
             
        # 6. Monitor
        print("\n[INFO] Monitoring for meeting end...")
        await monitor_and_complete(
            page=page,
            context=context,
            platform="microsoft_teams",
            meeting_id=meeting_id,
            api_url=api_url,
            api_secret=api_secret,
        )
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Teams Join Bot')
    parser.add_argument('url', help='Meeting URL')
    parser.add_argument('--meeting-id', default=None)
    parser.add_argument('--api-url', default="http://localhost:8000/api/v1")
    parser.add_argument('--api-secret', default="")
    
    args = parser.parse_args()
    
    asyncio.run(join_teams_meeting(
        meeting_url=args.url,
        meeting_id=args.meeting_id,
        api_url=args.api_url,
        api_secret=args.api_secret
    ))
