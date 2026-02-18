
import asyncio
from playwright.async_api import async_playwright
import argparse
import sys
import os

async def join_teams_meeting(meeting_url: str, display_name: str = "Meeting Assistant", mic_enabled: bool = False, camera_enabled: bool = False):
    print(f"Starting Teams Join for {meeting_url}")
    print(f"Name: {display_name}, Mic: {mic_enabled}, Cam: {camera_enabled}")
    
    async with async_playwright() as p:
        print(f"[DEBUG] Executable: {p.chromium.executable_path}")
        
        # Launch browser
        try:
            # Use minimal args that work
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--use-fake-ui-for-media-stream',
                    '--use-fake-device-for-media-stream'
                ]
            )
            print("[SUCCESS] Browser launched.")
        except Exception as e:
            print(f"[CRITICAL] Launch failed: {e}")
            return

        # Create context with permissions and user agent
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            permissions=['camera', 'microphone'],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print(f"[INFO] Navigating to meeting: {meeting_url}")
        try:
            await page.goto(meeting_url, wait_until='domcontentloaded')
            
            # 1. Handle "Open in Teams app" prompt
            print("[INFO] Checking for launcher page...")
            try:
                await page.wait_for_timeout(5000)
                # Click "Continue on this browser" if available
                selectors = [
                     'button[data-tid="joinOnWeb"]', 
                     'button:has-text("Continue on this browser")',
                     'button:has-text("Join on the web instead")',
                     'a:has-text("Continue on this browser")',
                     'a:has-text("Join on the web instead")',
                     'button[data-tid="launch-meeting-join-web-button"]'
                ]
                for sel in selectors:
                    try:
                        if await page.is_visible(sel):
                            btn = await page.query_selector(sel)
                            await btn.click()
                            print(f"[SUCCESS] Clicked '{sel}'")
                            break
                    except:
                        pass
            except Exception as e:
                print(f"[WARN] Error handling launcher: {e}")

            # 2. Wait for Pre-join screen
            print("[INFO] Waiting for pre-join screen (Name input)...")
            await page.wait_for_timeout(5000) 
            
            # STEP 3: Enter display name
            try:
                 name_input = await page.wait_for_selector(
                     'input[placeholder="Type your name"], input[data-tid="prejoin-display-name-input"]', 
                     timeout=15000
                 )
                 if name_input:
                     print(f"[INFO] Entering name: {display_name}")
                     await name_input.fill(display_name)
                     await page.keyboard.press("Enter") # Sometimes needed
                 else:
                     print("[INFO] Name input not found (maybe logged in)")
            except Exception as e:
                print(f"[WARN] Name input issue: {e}")

            # STEP 4: Audio/Video Handling
            print("[INFO] Configuring devices...")
            
            # Toggle Camera/Mic
            async def toggle_device(device_type, should_be_on):
                try:
                    # Generic toggle logic for Teams
                    # Look for buttons with arial-label containing "camera" or "microphone"
                    label_key = "camera" if device_type == 'camera' else "mic"
                    
                    # Logic: Find switch/button. Check state. Click if needed.
                    # This runs in browser context
                    result = await page.evaluate(f'''(args) => {{
                        const keyword = args.keyword;
                        const targetState = args.targetState;
                        const buttons = Array.from(document.querySelectorAll('button[role="switch"], div[role="switch"], button'));
                        
                        for (const b of buttons) {{
                             const label = (b.getAttribute('aria-label') || b.innerText || '').toLowerCase();
                             if (label.includes(keyword) && !label.includes('device')) {{
                                 // Check checked state
                                 const isChecked = b.getAttribute('aria-checked') === 'true';
                                 
                                 if (isChecked !== targetState) {{
                                     b.click();
                                     return 'Toggled ' + label + ' to ' + (targetState ? 'ON' : 'OFF');
                                 }}
                                 return 'Already ' + (targetState ? 'ON' : 'OFF');
                             }}
                        }}
                        return 'Control not found';
                    }}''', {{'keyword': label_key, 'targetState': should_be_on}})
                    
                    print(f"[{device_type.upper()}] {result}")
                except Exception as e:
                    print(f"[WARN] Error toggling {device_type}: {e}")

            await toggle_device('camera', camera_enabled)
            await toggle_device('mic', mic_enabled)

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
                else:
                    print("[ERR] Join button not found!")
            except Exception as e:
                 print(f"[ERR] Failed to click Join: {e}")
                 
            print("\n[SUCCESS] Script completed actions. Keeping browser open.")
            while True:
                await asyncio.sleep(10)

        except Exception as e:
            print(f"[CRITICAL] Error during session: {e}")
            import traceback
            traceback.print_exc()
            # Keep open on error to debug
            print("Keeping browser open for debugging...")
            while True:
                await asyncio.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Teams Join Bot')
    parser.add_argument('url', help='Meeting URL')
    parser.add_argument('--name', default="Meeting Assistant", help='Display Name')
    parser.add_argument('--mic', action='store_true', help='Enable microphone')
    parser.add_argument('--camera', action='store_true', help='Enable camera')
    
    args = parser.parse_args()
    
    asyncio.run(join_teams_meeting(
        meeting_url=args.url,
        display_name=args.name,
        mic_enabled=args.mic,
        camera_enabled=args.camera
    ))
