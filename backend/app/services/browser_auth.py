import logging
import json
import asyncio
from typing import Dict, Optional, Tuple
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import Stealth

# Configure logging
logger = logging.getLogger(__name__)

class BrowserAuthService:
    """
    Service to handle browser-based authentication for various platforms.
    Uses Playwright to automate login flows and capture session cookies.
    """
    
    def __init__(self):
        self.headless = True  # Set to False for debugging
        self.timeout = 30000  # 30 seconds timeout
        
    async def verify_credentials(self, platform_type: str, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Verify credentials by attempting to log in via browser.
        Returns: (success, message, session_data)
        """
        logger.info(f"Starting browser verification for {platform_type} ({email})")
        
        async with async_playwright() as p:
            # Launch browser with stealth settings
            # Args to improve stealth and avoid common detection triggers
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
                ]
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            # Create page and apply stealth using Stealth class
            page = await context.new_page()
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            try:
                # Route to platform-specific handler
                if platform_type == "google_meet":
                    return await self._verify_google(page, email, password)
                elif platform_type == "microsoft_teams":
                    return await self._verify_microsoft(page, email, password)
                elif platform_type == "zoom":
                    return await self._verify_zoom(page, email, password)
                else:
                    return False, f"Unsupported platform: {platform_type}", None
                    
            except Exception as e:
                logger.error(f"Browser verification failed: {str(e)}")
                # Capture screenshot on failure for debugging (in real implementation, save to file)
                # await page.screenshot(path=f"error_{platform_type}.png")
                return False, f"Verification error: {str(e)}", None
                
            finally:
                await context.close()
                await browser.close()

    async def _verify_google(self, page: Page, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Google Login Strategy (Improved)"""
        try:
            await page.goto("https://accounts.google.com/ServiceLogin?service=mail", wait_until="networkidle")
            
            # Email Step
            await page.fill('input[type="email"]', email)
            await page.click('#identifierNext')
            
            # Wait for password field or error
            try:
                # Check for "Couldn't find your Google Account"
                try:
                    await page.wait_for_selector('text="Couldn\'t find your Google Account"', timeout=3000)
                    return False, "Email not found (Google rejected email)", None
                except:
                    pass

                await page.wait_for_selector('input[type="password"]', timeout=10000)
            except:
                # Check for CAPTCHA
                content = await page.content()
                if "CAPTCHA" in content or "robot" in content:
                    return False, "Google blocked due to automation (CAPTCHA)", None
                return False, "Email step timeout (Element not found)", None
                
            await page.fill('input[type="password"]', password)
            await page.click('#passwordNext')
            
            # Wait for navigation or error
            # Check for 2FA or success
            try:
                # Check for common success indicators (inbox URL, profile image, etc.)
                # Increased timeout for success redirect
                await page.wait_for_url('**/mail/u/0/**', timeout=15000)
                
                # Capture session
                cookies = await page.context.cookies()
                return True, "Login successful", {"cookies": cookies}
            except:
                # Check for specific error messages
                if await page.query_selector('text="Wrong password"') or \
                   await page.query_selector('text="Try again with your password"'):
                    return False, "Invalid password", None
                
                if await page.query_selector('text="2-Step Verification"') or \
                   await page.query_selector('text="Google sent a notification to your phone"'):
                    return False, "2FA required (Check your phone, but we can't automate this yet)", None
                    
                return False, "Login failed (timeout or unknown error)", None
                
        except Exception as e:
            return False, f"Google login error: {str(e)}", None

    async def _verify_microsoft(self, page: Page, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Microsoft Login Strategy (Improved)"""
        try:
            await page.goto("https://login.microsoftonline.com/")
            await page.fill('input[type="email"]', email)
            
            # Click Next (Try input then button then ID)
            try:
                await page.click('input[type="submit"]', timeout=3000)
            except:
                try:
                    await page.click('button[type="submit"]', timeout=3000)
                except:
                    await page.click('#idSIButton9', timeout=3000)

            # Wait for password
            try:
                await page.wait_for_selector('input[type="password"]', timeout=10000)
            except:
                # Check if it was "Email not found"
                if await page.query_selector('text="That Microsoft account doesn\'t exist"'):
                    return False, "Email not found", None
                return False, "Email step failed (timeout/not found)", None
                
            await page.fill('input[type="password"]', password)
            
            # Click Sign In (Try input then button then ID)
            try:
                await page.click('input[type="submit"]', timeout=3000)
            except:
                try:
                    await page.click('button[type="submit"]', timeout=3000)
                except:
                    await page.click('#idSIButton9', timeout=3000)
            
            # Handle "Stay signed in?"
            try:
                await page.wait_for_load_state('networkidle', timeout=5000)
                if await page.query_selector('text="Stay signed in?"') or await page.query_selector('input[value="Yes"]'):
                     try:
                        await page.click('input[value="Yes"]', timeout=3000)
                     except:
                        pass
            except:
                pass 

            # Check Success
            try:
                # Wait for redirect away from login
                await page.wait_for_url(lambda url: "login.microsoftonline.com" not in url, timeout=15000)
                cookies = await page.context.cookies()
                return True, "Login successful", {"cookies": cookies}
            except:
                return False, "Login failed (timeout or wrong password)", None

        except Exception as e:
            return False, f"Microsoft login error: {str(e)}", None

    async def _verify_zoom(self, page: Page, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Zoom Login Strategy (Improved)"""
        try:
            await page.goto("https://zoom.us/signin", wait_until="networkidle")
            
            # Cookie banner check - handle gracefully
            try:
                # Sometimes it's a different selector or text
                if await page.is_visible('#onetrust-accept-btn-handler'):
                    await page.click('#onetrust-accept-btn-handler', timeout=3000)
            except:
                pass

            # Wait for email field explicitly
            try:
                await page.wait_for_selector('input[name="email"]', timeout=10000)
            except:
                # Check for "Verify you are human"
                content = await page.content()
                if "Verify you are human" in content or "CAPTCHA" in content:
                    return False, "Zoom blocking automation (CAPTCHA/Challenge)", None
                return False, "Zoom login page didn't load properly", None

            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', password)
            
            # Click Sign In
            # Zoom signin button selector often changes or is generated
            # Try specific ID or by role
            try:
                await page.click('div.signin button.submit', timeout=3000)
            except:
                try:
                    await page.click('#login-form button[type="submit"]', timeout=3000)
                except:
                    # Generic fallback
                    await page.click('button:has-text("Sign In")', timeout=3000)
            
            # Check success (dashboard)
            try:
                # Wait for redirect to profile or meeting page
                await page.wait_for_url(lambda url: "/signin" not in url, timeout=15000)
                
                # Double check not on error page
                if await page.query_selector('.error-msg') or await page.query_selector('.alert-danger'):
                     return False, "Invalid credentials (Zoom rejected login)", None
                     
                cookies = await page.context.cookies()
                return True, "Login successful", {"cookies": cookies}
            except:
                if await page.query_selector('.error-msg'):
                     return False, "Invalid credentials", None
                return False, "Login failed (timeout or unknown error)", None

        except Exception as e:
            return False, f"Zoom login error: {str(e)}", None
