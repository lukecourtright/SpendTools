import os
from playwright.async_api import Browser


async def fetch_rates(browser: Browser) -> list[dict]:
    context = await browser.new_context()
    page = await context.new_page()

    try:
        email    = os.environ["CARDCENTER_EMAIL"]
        password = os.environ["CARDCENTER_PASSWORD"]
        await page.goto("https://cardcenter.cc/Account/Login")
        await page.wait_for_load_state("networkidle")
        await page.locator('#Email').click()
        await page.locator('#Email').type(email)
        await page.locator('#Password').click()
        await page.locator('#Password').type(password)
        await page.locator('button[type="submit"]').click()
        await page.wait_for_url(lambda url: "Login" not in url, timeout=15000)

        await page.goto("https://cardcenter.cc/Rates")
        await page.wait_for_load_state("networkidle")

        # The table uses a two-row pattern per brand:
        #   Row 1: <td colspan="100"> with <span class="fw-semibold">Brand Name</span>
        #   Row 2+: data rows where the first <td> is a /Rates/ link (denomination)
        #           and the second <td> is the rate percentage
        rates = []
        current_brand = None
        rows = await page.query_selector_all("tr")

        for row in rows:
            # Brand header row
            header_td = await row.query_selector("td[colspan='100']")
            if header_td:
                brand_span = await header_td.query_selector("span.fw-semibold")
                if brand_span:
                    current_brand = (await brand_span.inner_text()).strip()
                continue

            # Data row: must have a /Rates/ link and a known brand
            if not current_brand:
                continue
            denom_link = await row.query_selector('td a[href^="/Rates/"]')
            if not denom_link:
                continue

            tds = await row.query_selector_all("td")
            if len(tds) < 2:
                continue

            denom_raw = (await tds[0].inner_text()).replace("$", "").replace(",", "").strip()
            rate_raw  = (await tds[1].inner_text()).replace("%", "").strip()

            try:
                rates.append({
                    "brand": current_brand,
                    "denomination": float(denom_raw),
                    "cardcenter": float(rate_raw),
                })
            except ValueError:
                continue

        return rates

    finally:
        await context.close()
