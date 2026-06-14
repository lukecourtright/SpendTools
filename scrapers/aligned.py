import base64
import os
import re
from pathlib import Path
from playwright.async_api import Browser, async_playwright

SESSION_FILE  = Path(__file__).parent.parent / "aligned_session.json"
CHROME_PROFILE = Path(__file__).parent.parent / ".chrome_profile"


def _ensure_session_file():
    """On Render, decode ALIGNED_SESSION env var to aligned_session.json."""
    session_b64 = os.environ.get("ALIGNED_SESSION")
    if session_b64 and not SESSION_FILE.exists():
        SESSION_FILE.write_bytes(base64.b64decode(session_b64))


async def fetch_rates(browser: Browser) -> list[dict]:
    _ensure_session_file()

    if SESSION_FILE.exists():
        # Use saved session with the shared Playwright Chromium browser (works on Render)
        context = await browser.new_context(storage_state=str(SESSION_FILE))
        page = await context.new_page()
        try:
            return await _scrape(page)
        finally:
            await context.close()

    elif CHROME_PROFILE.exists():
        # Local fallback: use the persistent Chrome profile saved by save_session_aligned.py
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE),
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
            )
            page = await context.new_page()
            try:
                return await _scrape(page)
            finally:
                await context.close()

    else:
        raise RuntimeError(
            "No Aligned Incentives session found. "
            "Run save_session_aligned.py first, log in with Google, then press Enter."
        )


async def _scrape(page) -> list[dict]:
    await page.goto("https://portal.alignedincentiv.es/Seller/Deals")
    await page.wait_for_load_state("networkidle")

    if "login" in page.url.lower() or "signin" in page.url.lower():
        if SESSION_FILE.exists():
            SESSION_FILE.unlink(missing_ok=True)
        raise RuntimeError("Aligned Incentives session expired. Run save_session_aligned.py again.")

    rates = []
    rows = await page.query_selector_all("tr.expandable")

    for row in rows:
        brand_divs = await row.query_selector_all(".brands-column div")
        rate_divs  = await row.query_selector_all(".buy-rate-column div")

        for brand_div, rate_div in zip(brand_divs, rate_divs):
            brand_text = (await brand_div.inner_text()).strip()
            rate_text  = (await rate_div.inner_text()).replace("%", "").strip()

            # Format: "$100 Amazon.com" or "$1,000 Walmart/Sam's Club"
            match = re.match(r'^\$([0-9,]+(?:\.\d+)?)\s+(.+)$', brand_text)
            if not match:
                continue

            denom_raw = match.group(1).replace(",", "")
            brand     = match.group(2).strip()

            try:
                rates.append({
                    "brand": brand,
                    "denomination": float(denom_raw),
                    "aligned": float(rate_text),
                })
            except ValueError:
                continue

    return rates
