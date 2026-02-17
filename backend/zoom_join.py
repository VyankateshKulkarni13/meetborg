"""
Automated Zoom Meeting Join - Browser Automation
Handles Zoom web client join flow with camera/mic controls
"""
import asyncio
from playwright.async_api import async_playwright

async def join_zoom_meeting(meeting_url: str):
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
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            channel='chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                # Bypass external protocol handler dialogs
                '--disable-features=ExternalProtocolDialogInProductHelp',
                '--disable-external-intent-requests',
                # Auto-dismiss protocol handler prompts
                '--no-first-run',
                '--no-default-browser-check'
            ],
            permissions=['camera', 'microphone'],
            viewport={'width': 1920, 'height': 1080},
            # Bypass download prompts
            accept_downloads=False
        )
        
        print("[OK] Chrome launched!")
        
        # Create new page
        page = await context.new_page()
        
        # Convert Zoom meeting URL to web client URL
        # From: https://zoom.us/j/86010230348?pwd=abc123
        # To:   https://app.zoom.us/wc/join/86010230348?pwd=abc123
        print(f"\n[INFO] Original meeting URL: {meeting_url}")
        
        import re
        from urllib.parse import urlparse, parse_qs, urlencode
        
        # Extract meeting ID and password from URL
        meeting_id = None
        password = None
        
        # Pattern 1: zoom.us/j/[ID]?pwd=[PWD]
        match = re.search(r'zoom\.us/j/(\d+)', meeting_url)
        if match:
            meeting_id = match.group(1)
            # Extract password if present
            parsed = urlparse(meeting_url)
            params = parse_qs(parsed.query)
            if 'pwd' in params:
                password = params['pwd'][0]
        
        if meeting_id:
            # Construct direct web client URL
            web_client_url = f"https://app.zoom.us/wc/join/{meeting_id}"
            if password:
                web_client_url += f"?pwd={password}"
            
            print(f"[INFO] Converted to web client URL: {web_client_url}")
            meeting_url = web_client_url
        else:
            print("[WARN] Could not extract meeting ID, using original URL")
        
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
        
        # Step 2: Toggle camera and microphone OFF
        print("\n[INFO] Turning off camera and microphone...")
        
        # Wait a moment for the UI to fully load
        await page.wait_for_timeout(2000)
        
        # DEBUG: Save page HTML and screenshot for analysis
        print("[DEBUG] Saving page state for analysis...")
        page_html = await page.content()
        with open('zoom_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_html)
        await page.screenshot(path='zoom_ui_state.png', full_page=True)
        print("[DEBUG] Saved: zoom_page_debug.html and zoom_ui_state.png")
        
        # DEBUG: List all buttons on the page
        print("[DEBUG] Finding all buttons on the page...")
        all_buttons = await page.locator('button').all()
        print(f"[DEBUG] Found {len(all_buttons)} buttons total")
        
        for i, btn in enumerate(all_buttons[:20]):  # Check first 20 buttons
            try:
                text = await btn.inner_text()
                aria_label = await btn.get_attribute('aria-label')
                is_visible = await btn.is_visible()
                print(f"[DEBUG] Button {i}: text='{text}' | aria-label='{aria_label}' | visible={is_visible}")
            except:
                pass
        
        # Look for video button (camera) - improved logic with debugging
        camera_toggled = False
        print("\n[INFO] Checking camera state...")
        
        try:
            # First, check if "Start Video" button exists (camera already OFF)
            start_video_btn = page.locator('button:has-text("Start Video")').first
            start_video_count = await start_video_btn.count()
            
            if start_video_count > 0:
                print("[INFO] Camera is already OFF (found 'Start Video' button)")
                camera_toggled = True
            else:
                # Camera is ON, look for "Stop Video" button
                print("[INFO] Camera appears to be ON, looking for toggle button...")
                
                # Try multiple selector strategies with more variations
                selectors_to_try = [
                    'button:has-text("Stop Video")',
                    'button:has-text("Turn Off Video")',
                    'button:has-text("stop video")',  # case variations
                    'button[aria-label*="video" i][aria-label*="stop" i]',
                    'button[aria-label*="video" i][aria-label*="turn off" i]',
                    'button[aria-label*="Stop video" i]',
                    'button[aria-label*="Turn off video" i]',
                    'button[data-tooltip*="video" i]',
                    'button[title*="video" i][title*="stop" i]',
                    # Try finding by icon/class patterns
                    'button[class*="video" i]',
                ]
                
                video_button_found = False
                for selector in selectors_to_try:
                    try:
                        print(f"[DEBUG] Trying selector: {selector}")
                        btn_locator = page.locator(selector).first
                        btn_count = await btn_locator.count()
                        
                        if btn_count > 0:
                            is_visible = await btn_locator.is_visible()
                            print(f"[DEBUG] Found {btn_count} elements, visible: {is_visible}")
                            
                            if is_visible:
                                # Get button details before clicking
                                btn_text = await btn_locator.inner_text()
                                btn_aria = await btn_locator.get_attribute('aria-label')
                                print(f"[DEBUG] Clicking button - text: '{btn_text}', aria: '{btn_aria}'")
                                
                                await btn_locator.click()
                                print(f"[OK] Camera toggled OFF (clicked using selector: {selector})")
                                camera_toggled = True
                                video_button_found = True
                                await page.wait_for_timeout(1000)
                                break
                    except Exception as e:
                        print(f"[DEBUG] Selector failed: {e}")
                        continue
                
                if not video_button_found:
                    print("[WARN] Could not find video toggle button with any selector")
                    await page.screenshot(path='zoom_camera_not_found.png')
                    print("[INFO] Screenshot saved: zoom_camera_not_found.png")
        except Exception as e:
            print(f"[ERROR] Camera toggle failed: {e}")
            await page.screenshot(path='zoom_camera_error.png')
        
        
        # Look for microphone button - improved logic with debugging
        mic_toggled = False
        print("\n[INFO] Checking microphone state...")
        
        try:
            # First, check if "Unmute" button exists (mic already OFF)
            unmute_btn = page.locator('button:has-text("Unmute")').first
            unmute_count = await unmute_btn.count()
            
            if unmute_count > 0:
                print("[INFO] Microphone is already muted (found 'Unmute' button)")
                mic_toggled = True
            else:
                # Microphone is ON, look for "Mute" button
                print("[INFO] Microphone appears to be ON, looking for mute button...")
                
                # Try multiple selector strategies with more variations
                selectors_to_try = [
                    'button:has-text("Mute")',
                    'button:has-text("Mute Audio")',
                    'button:has-text("mute")',  # case variations
                    'button[aria-label*="mute" i]:not([aria-label*="unmute" i])',
                    'button[aria-label*="audio" i][aria-label*="mute" i]',
                    'button[aria-label*="Mute audio" i]',
                    'button[aria-label*="Mute microphone" i]',
                    'button[data-tooltip*="mute" i]',
                    'button[title*="mute" i]:not([title*="unmute" i])',
                    # Try finding by icon/class patterns
                    'button[class*="audio" i]',
                    'button[class*="microphone" i]',
                ]
                
                mute_button_found = False
                for selector in selectors_to_try:
                    try:
                        print(f"[DEBUG] Trying selector: {selector}")
                        btn_locator = page.locator(selector).first
                        btn_count = await btn_locator.count()
                        
                        if btn_count > 0:
                            is_visible = await btn_locator.is_visible()
                            print(f"[DEBUG] Found {btn_count} elements, visible: {is_visible}")
                            
                            if is_visible:
                                # Get button details before clicking
                                btn_text = await btn_locator.inner_text()
                                btn_aria = await btn_locator.get_attribute('aria-label')
                                print(f"[DEBUG] Clicking button - text: '{btn_text}', aria: '{btn_aria}'")
                                
                                await btn_locator.click()
                                print(f"[OK] Microphone toggled OFF (clicked using selector: {selector})")
                                mic_toggled = True
                                mute_button_found = True
                                await page.wait_for_timeout(1000)
                                break
                    except Exception as e:
                        print(f"[DEBUG] Selector failed: {e}")
                        continue
                
                if not mute_button_found:
                    print("[WARN] Could not find microphone toggle button with any selector")
                    await page.screenshot(path='zoom_mic_not_found.png')
                    print("[INFO] Screenshot saved: zoom_mic_not_found.png")
        except Exception as e:
            print(f"[ERROR] Microphone toggle failed: {e}")
            await page.screenshot(path='zoom_mic_error.png')
        
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
        
        print("\n[INFO] Browser will stay open - close it manually when done")
        print("[INFO] Meeting automation complete!")
        
        # Keep browser open indefinitely
        try:
            while True:
                await page.wait_for_timeout(60000)  # Wait 1 minute at a time
        except KeyboardInterrupt:
            print("\n[INFO] Closing browser...")
            await context.close()
            return True
        except Exception:
            # Browser was closed manually
            return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        meeting_url = sys.argv[1]
    else:
        meeting_url = "https://zoom.us/j/1234567890"
        print("[WARN] No meeting URL provided, using test URL")
    
    result = asyncio.run(join_zoom_meeting(meeting_url))
    
    if result:
        print("\n[SUCCESS] Zoom automation completed!")
    else:
        print("\n[INFO] Check browser or screenshots")
