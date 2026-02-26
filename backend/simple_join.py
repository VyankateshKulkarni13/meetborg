"""
Automated Google Meet Join - Uses separate profile (no need to close Chrome)
"""
import asyncio
import argparse
from playwright.async_api import async_playwright
from meeting_monitor import monitor_and_complete

async def join_meeting_auto(meeting_url: str, meeting_id: str = None,
                            api_url: str = "http://localhost:8000/api/v1",
                            api_secret: str = ""):
    """
    Join Google Meet automatically 
    Note: You'll need to log in once, then it will remember your session
    """
    
    print("=" * 60)
    print("Automated Google Meet Join Bot")
    print("=" * 60)
    print(f"Meeting: {meeting_url}")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("\n[INFO] Launching Chrome...")
        
        # Use persistent context to reuse browser sessions and open in new tabs
        import os
        from pathlib import Path
        
        # Create user data directory for persistent browser profile
        user_data_dir = Path.home() / ".meetborg" / "chrome_profile"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Launch persistent context (reuses existing browser if running)
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
                '--window-size=1280,720',
                '--window-position=100,50',
            ],
            permissions=['camera', 'microphone'],
            viewport={'width': 1280, 'height': 720}
        )
        
        print("[OK] Chrome launched!")

        # Create new page (new tab in existing browser)
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

        print(f"\n[INFO] Navigating to meeting: {meeting_url}")
        await page.goto(meeting_url, wait_until='domcontentloaded')
        
        # Wait for page to load
        await page.wait_for_timeout(5000)
        
        current_url = page.url
        print(f"[INFO] Current URL: {current_url}")
        
        
        # Check if redirected to login
        if 'accounts.google.com' in current_url and 'signin' in current_url:
            print("\n[INFO] You need to log in first")
            print("[INFO] Please log in manually in the browser window")
            print("[INFO] After logging in, the bot will automatically join")
            print("[INFO] Waiting 60 seconds for login...")
            await page.wait_for_timeout(60000)
            
            # Check URL again after login
            current_url = page.url
            if 'meet.google.com' not in current_url:
                print("[WARN] Still not on meeting page after 60s")
                print("[INFO] Browser will stay open - you can continue manually")
                await page.wait_for_timeout(60000)
                await browser.close()
                return False
        
        # Now on meeting page
        if 'meet.google.com' in current_url:
            print("\n[SUCCESS] On Google Meet page!")
            
            # Wait for page to load completely
            print("\n[INFO] Waiting for page to load...")
            await page.wait_for_timeout(3000)
            
            # STEP 1: Turn off camera and microphone FIRST (on guest join screen)
            print("\n[INFO] Turning off camera and microphone...")
            
            async def toggle_device(device_name: str, max_retries: int = 3):
                """
                Robust device toggle with multiple strategies and retries
                device_name: 'camera' or 'microphone'
                """
                for attempt in range(max_retries):
                    try:
                        print(f"[INFO] {device_name.title()} toggle attempt {attempt + 1}/{max_retries}")
                        
                        # Strategy 1: Direct SVG icon click (most reliable for Meet)
                        result = await page.evaluate(f'''() => {{
                            const buttons = Array.from(document.querySelectorAll('div[role="button"], button'));
                            for (const btn of buttons) {{
                                const svg = btn.querySelector('svg');
                                if (!svg) continue;
                                
                                const ariaLabel = btn.getAttribute('aria-label') || '';
                                const dataTooltip = btn.getAttribute('data-tooltip') || '';
                                const combined = (ariaLabel + dataTooltip).toLowerCase();
                                
                                // Detect {device_name} button
                                const keywords = {['camera', 'cam', 'video'] if device_name == 'camera' else ['microphone', 'mic', 'audio']};
                                const hasKeyword = keywords.some(k => combined.includes(k));
                                
                                if (hasKeyword && !combined.includes('settings')) {{
                                    // Check if it's currently ON (we want to turn it OFF)
                                    const isOn = combined.includes('turn off') || 
                                               combined.includes('is on') ||
                                               !combined.includes('turn on');
                                    
                                    if (isOn) {{
                                        btn.click();
                                        return 'SUCCESS: Clicked to turn off - ' + ariaLabel;
                                    }} else {{
                                        return 'ALREADY OFF: ' + ariaLabel;
                                    }}
                                }}
                            }}
                            return 'NOT FOUND';
                        }}''')
                        
                        if 'SUCCESS' in result:
                            print(f"[OK] {device_name.title()} turned off (JavaScript SVG)")
                            return True
                        elif 'ALREADY OFF' in result:
                            print(f"[OK] {device_name.title()} already off")
                            return True
                        
                        # Strategy 2: CSS selector with aria-label
                        await page.wait_for_timeout(500)
                        selectors = []
                        if device_name == 'camera':
                            selectors = [
                                'button[aria-label*="Turn off camera" i]',
                                'div[role="button"][aria-label*="camera" i]:not([aria-label*="Turn on" i])',
                                'button[data-tooltip*="Turn off camera" i]'
                            ]
                        else:
                            selectors = [
                                'button[aria-label*="Turn off microphone" i]',
                                'button[aria-label*="Turn off mic" i]',
                                'div[role="button"][aria-label*="microphone" i]:not([aria-label*="Turn on" i])',
                                'button[data-tooltip*="Turn off microphone" i]'
                            ]
                        
                        for selector in selectors:
                            try:
                                btn = await page.query_selector(selector)
                                if btn and await btn.is_visible():
                                    await btn.click()
                                    print(f"[OK] {device_name.title()} turned off (CSS selector)")
                                    return True
                            except:
                                pass
                        
                        # Strategy 3: Find by index (camera is usually first, mic second)
                        await page.wait_for_timeout(500)
                        device_index = 0 if device_name == 'camera' else 1
                        result = await page.evaluate(f'''(index) => {{
                            const mediaButtons = Array.from(document.querySelectorAll('div[role="button"], button'))
                                .filter(btn => {{
                                    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                                    return (label.includes('camera') || label.includes('microphone') || 
                                           label.includes('mic') || label.includes('video') || label.includes('audio')) &&
                                           !label.includes('settings');
                                }});
                            
                            if (mediaButtons[index]) {{
                                mediaButtons[index].click();
                                return 'Clicked button at index ' + index;
                            }}
                            return 'Index not found';
                        }}''', device_index)
                        
                        if 'Clicked' in result:
                            print(f"[OK] {device_name.title()} toggle attempted (index method)")
                            return True
                        
                        if attempt < max_retries - 1:
                            await page.wait_for_timeout(1000)
                    
                    except Exception as e:
                        print(f"[WARN] {device_name.title()} toggle attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:
                            await page.wait_for_timeout(1000)
                
                print(f"[WARN] Could not toggle {device_name} after {max_retries} attempts")
                return False
            
            # Toggle camera with retries
            await toggle_device('camera', max_retries=3)
            await page.wait_for_timeout(800)
            
            # Toggle microphone with retries
            await toggle_device('microphone', max_retries=3)
            await page.wait_for_timeout(1000)
            
            # STEP 2: Now check if there's a name input (guest join)
            print("\n[INFO] Checking for guest name input...")
            
            try:
                # Look for name input field
                name_input_selectors = [
                    'input[placeholder*="name" i]',
                    'input[aria-label*="name" i]',
                    'input[type="text"]'
                ]
                
                name_input = None
                for selector in name_input_selectors:
                    try:
                        name_input = await page.query_selector(selector)
                        if name_input and await name_input.is_visible():
                            break
                    except:
                        pass
                
                if name_input:
                    print("[OK] Found name input field (guest join)")
                    print("[INFO] Entering name: 'Meeting Assistant'")
                    
                    # Clear and type name
                    await name_input.click()
                    await page.wait_for_timeout(300)
                    await name_input.fill('')
                    await name_input.type('Meeting Assistant', delay=50)
                    
                    print("[OK] Name entered successfully")
                    await page.wait_for_timeout(1000)
                else:
                    print("[INFO] No name input found (likely logged in)")
            except Exception as e:
                print(f"[WARN] Could not fill name: {e}")
            
            await page.wait_for_timeout(1500)
            
            # Find and click join button
            print("\n[INFO] Looking for join button...")
            print("[INFO] Waiting for page to fully load...")
            await page.wait_for_timeout(3000)  # Give page time to settle
            
            try:
                # Try multiple strategies to find and click the button
                clicked = False
                
                # Strategy 1: Use CSS selector with wait
                try:
                    join_btn = await page.wait_for_selector(
                        'button:has-text("Ask to join"), button:has-text("Join now"), button:has-text("Join")',
                        state='visible',
                        timeout=10000
                    )
                    if join_btn:
                        print("[OK] Found join button (Strategy 1)")
                        await join_btn.scroll_into_view_if_needed()
                        await page.wait_for_timeout(500)
                        await join_btn.click()
                        clicked = True
                except Exception as e:
                    print(f"[WARN] Strategy 1 failed: {e}")
                
                # Strategy 2: JavaScript click
                if not clicked:
                    try:
                        print("[INFO] Trying JavaScript click...")
                        result = await page.evaluate('''() => {
                            const buttons = Array.from(document.querySelectorAll('button, span[role="button"]'));
                            for (const btn of buttons) {
                                const text = btn.innerText || btn.textContent || '';
                                const label = btn.getAttribute('aria-label') || '';
                                if (text.includes('Ask to join') || text.includes('Join now') || 
                                    label.includes('Ask to join') || label.includes('Join now')) {
                                    btn.click();
                                    return 'Clicked: ' + text + ' / ' + label;
                                }
                            }
                            return 'Button not found';
                        }''')
                        print(f"[INFO] JavaScript result: {result}")
                        if 'Clicked' in result:
                            clicked = True
                    except Exception as e:
                        print(f"[WARN] Strategy 2 failed: {e}")
                
                if clicked:
                    print("\n" + "=" * 60)
                    print("[SUCCESS] Join button clicked!")
                    print("[SUCCESS] Check the browser - you should be joining")
                    print("=" * 60)
                else:
                    print("[WARN] Could not click join button with any strategy")
                    await page.screenshot(path='meeting_page.png')
                    print("[OK] Screenshot saved to: meeting_page.png")

            except Exception as e:
                print(f"[ERROR] Error during join: {e}")
                await page.screenshot(path='meeting_join_error.png')

        # ── Monitor meeting until it ends ────────────────────────────────────
        print("\n[INFO] Meeting joined — monitoring for meeting end...")
        await monitor_and_complete(
            page=page,
            context=context,
            platform="google_meet",
            meeting_id=meeting_id,
            api_url=api_url,
            api_secret=api_secret,
        )
        return True

    return False



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Meet Bot")
    parser.add_argument("url", help="Meeting URL")
    parser.add_argument("--meeting-id", default=None, help="Meeting ID for completion callback")
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1")
    parser.add_argument("--api-secret", default="")
    args = parser.parse_args()

    result = asyncio.run(join_meeting_auto(
        args.url,
        meeting_id=args.meeting_id,
        api_url=args.api_url,
        api_secret=args.api_secret,
    ))

    if result:
        print("\n[SUCCESS] Bot joined and meeting completed!")
    else:
        print("\n[INFO] Check browser or screenshot")
