import asyncio
from playwright.async_api import async_playwright
import os

async def diag():
    async with async_playwright() as p:
        print(f"Playwright version: {p.chromium.name}")
        exe = p.chromium.executable_path
        print(f"Executable path: {exe}")
        
        if not os.path.exists(exe):
            print("ERROR: Browser executable not found at path!")
            return

        print("Attempting minimal launch...")
        try:
            browser = await p.chromium.launch(headless=False)
            print("SUCCESS: Browser launched!")
            page = await browser.new_page()
            await page.goto("https://google.com")
            print("SUCCESS: Page loaded!")
            await browser.close()
        except Exception as e:
            print(f"ERROR launching minimal: {e}")
            
        print("\nAttempting with args...")
        try:
            browser = await p.chromium.launch(
                headless=False,
                args=['--use-fake-ui-for-media-stream']
            )
            print("SUCCESS: Browser launched with args!")
            await browser.close()
        except Exception as e:
            print(f"ERROR launching with args: {e}")

if __name__ == "__main__":
    asyncio.run(diag())
