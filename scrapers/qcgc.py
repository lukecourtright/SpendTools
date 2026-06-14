import os
from playwright.async_api import Browser


async def fetch_rates(browser: Browser) -> list[dict]:
    email = os.environ["QCGC_EMAIL"]
    password = os.environ["QCGC_PASSWORD"]

    context = await browser.new_context()
    page = await context.new_page()

    try:
        # --- Login ---
        await page.goto("https://portal.qcgc.io/login")
        await page.wait_for_load_state("networkidle")

        # Livewire forms require type() to fire input events that wire:model listens to
        await page.locator('input[id="form.email"]').click()
        await page.locator('input[id="form.email"]').type(email)
        await page.locator('input[id="form.password"]').click()
        await page.locator('input[id="form.password"]').type(password)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_url(lambda url: "login" not in url, timeout=15000)

        # --- Extract rates across all pages ---
        await page.goto("https://portal.qcgc.io/rates")
        await page.wait_for_load_state("networkidle")

        rates = []

        while True:
            rows = await page.query_selector_all("tr.fi-ta-row")
            for row in rows:
                brand_td = await row.query_selector('td[class*="fi-ta-cell-brand"]')
                denom_td = await row.query_selector("td.fi-ta-cell-denomination")
                rate_td  = await row.query_selector("td.fi-ta-cell-payout-rate")

                if not (brand_td and denom_td and rate_td):
                    continue

                brand_el = await brand_td.query_selector(".fi-ta-text")
                denom_el = await denom_td.query_selector(".fi-ta-text")
                rate_el  = await rate_td.query_selector(".fi-ta-text")

                if not (brand_el and denom_el and rate_el):
                    continue

                brand     = (await brand_el.inner_text()).strip()
                denom_raw = (await denom_el.inner_text()).replace("$", "").replace(",", "").strip()
                rate_raw  = (await rate_el.inner_text()).replace("%", "").strip()

                try:
                    rates.append({"brand": brand, "denomination": float(denom_raw), "qcgc": float(rate_raw)})
                except ValueError:
                    continue

            # Advance to next page if available
            next_btn = page.locator('button.fi-pagination-next-btn:not([disabled])')
            if await next_btn.count() == 0:
                break
            await next_btn.dispatch_event("click")
            # Livewire does an AJAX swap; wait for the loading attr to clear
            await page.wait_for_function(
                "() => !document.querySelector('button.fi-pagination-next-btn[disabled]')"
                " && document.querySelectorAll('tr.fi-ta-row').length > 0"
            )

        return rates

    finally:
        await context.close()
