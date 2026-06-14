"""
Run this script once to log into Aligned Incentives with Google.
It opens a real browser window so you can click "Sign in with Google" normally.

Two things are saved:
  - .chrome_profile/   — persistent Chrome session for local use
  - aligned_session.json — exported cookies for Render deployment

How to run: python save_session_aligned.py
"""
import asyncio
import base64
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_FILE  = Path(__file__).parent / "aligned_session.json"
CHROME_PROFILE = Path(__file__).parent / ".chrome_profile"


async def main():
    print("Opening browser for Aligned Incentives login...")
    print("Sign in with Google as you normally would.")
    print("Once you can see the Deals page, come back here and press Enter.\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = await context.new_page()
        await page.goto("https://portal.alignedincentiv.es/")

        input("Press Enter once you are fully logged in and on the Deals page... ")

        # Save Chrome profile state (local use)
        await context.storage_state(path=str(SESSION_FILE))
        await context.close()

    print(f"\nSaved: {SESSION_FILE}")
    print(f"Saved: {CHROME_PROFILE}/\n")

    # Print the base64 value needed for Render's ALIGNED_SESSION env var
    session_b64 = base64.b64encode(SESSION_FILE.read_bytes()).decode()
    print("--- For Render deployment ---")
    print("Set this as the ALIGNED_SESSION environment variable in Render:")
    print(f"\n{session_b64}\n")


asyncio.run(main())
