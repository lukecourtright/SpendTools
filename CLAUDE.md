# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Windows (opens browser automatically)
run.bat

# Direct
python -m uvicorn main:app --port 8000
```

App serves at `http://localhost:8000`. No build step needed.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
# (On Linux only) playwright install-deps chromium

# One-time interactive setup for Aligned Incentives (opens real Chrome for manual Google login)
python save_session_aligned.py
```

Credentials go in `.env` (see `.env.example`). Aligned Incentives uses `aligned_session.json` and `.chrome_profile/` instead of a stored password.

## Deployment

Deployed to Railway at `https://spendtools-production-501e.up.railway.app/` via `railway.toml`. Railway auto-deploys on every push to `main`.

**Required Railway env vars:** `QCGC_EMAIL`, `QCGC_PASSWORD`, `CARDCENTER_EMAIL`, `CARDCENTER_PASSWORD`, `ALIGNED_SESSION`

To refresh `ALIGNED_SESSION` when the Aligned session expires:
1. Run `python save_session_aligned.py` locally and log in with Google
2. Open `aligned_session_b64.txt` on the Desktop (written by the script)
3. Copy the entire contents and paste into the `ALIGNED_SESSION` env var in Railway

## Brand Name Normalization

`brand_aliases.py` maps brand name variations across sources to a canonical display name. Edit this file to fix duplicate brands in the table — changes take effect on the next Refresh Rates click without restarting the server.

## Architecture

**Backend (`main.py`):**
- `POST /api/refresh` — launches headless Chromium (with `--no-sandbox` for Linux), runs all 3 scrapers concurrently via `asyncio.gather`, caches results in-memory
- `GET /api/rates` — returns cached results
- Brand names normalized via `_normalize_brand()` before merging; `brand_aliases.ALIASES` reloaded on every refresh

**Scrapers (`scrapers/`):**
- Each exports `async def fetch_rates(browser: Browser) -> list[dict]`
- Returns records with keys: `brand`, `denomination`, and a source-specific rate key (`qcgc`, `cardcenter`, or `aligned`)

**Merge logic (`main.py`):**
- Groups records by `(normalized_brand.lower(), denomination)` key
- Upserts each source's rate into a unified record; missing sources default to `None`
- Returns list sorted by brand + denomination

**Frontend (`static/index.html`):**
- Vanilla JS SPA; calls `/api/refresh` then `/api/rates`
- Sortable columns (click header), live search bar filtering by brand name
- Highlights the best (highest) rate per row in green
- No bundler or framework — edit directly

## Scraper Implementation Notes

**QCGC (`scrapers/qcgc.py`):**
- Login at `https://portal.qcgc.io/login` (not qcgc.io)
- Uses Livewire/Filament — must use `.type()` (not `.fill()`) to trigger wire:model bindings; wait for URL change after submit
- Paginates through results: `button.fi-pagination-next-btn` clicked via `dispatch_event("click")` (button is in DOM but not visible)
- Row selector: `tr.fi-ta-row`; cells: `td[class*="fi-ta-cell-brand"]`, `td.fi-ta-cell-denomination`, `td.fi-ta-cell-payout-rate`; text inside `.fi-ta-text`

**CardCenter (`scrapers/cardcenter.py`):**
- Login at `https://cardcenter.cc/Account/Login`; rates at `https://cardcenter.cc/Rates`
- Must use `.type()` (not `.fill()`) for login fields; submit selector: `button[type="submit"]:not([name="provider"])` (excludes Google SSO button)
- Wait for URL change after login (not networkidle)
- Table uses a two-row pattern: header row has `td[colspan='100']` with `span.fw-semibold` (brand name); data rows have `td a[href^="/Rates/"]` (denomination in `tds[0]`, rate in `tds[1]`)

**Aligned Incentives (`scrapers/aligned.py`):**
- Rates at `https://portal.alignedincentiv.es/Seller/Deals`
- Google OAuth blocks Playwright's Chromium, so login uses real Chrome via `save_session_aligned.py`
- Auth priority: (1) `ALIGNED_SESSION` env var → decoded to `aligned_session.json` (Railway), (2) `aligned_session.json` with Playwright Chromium, (3) `.chrome_profile/` with Chrome as local fallback
- Each `tr.expandable` row is a deal with multiple brands: `.brands-column div` entries like `$100 Amazon.com` paired with `.buy-rate-column div` rates; parsed via regex
- Runs headless in all paths
