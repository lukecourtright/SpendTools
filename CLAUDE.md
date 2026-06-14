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
# (On Linux/Render only) playwright install-deps chromium

# One-time interactive setup for Aligned Incentives (opens real browser for manual Google login)
python save_session_aligned.py
```

Credentials go in `.env` (see `.env.example`). Aligned Incentives uses `aligned_session.json` instead of a stored password.

## Debugging Scrapers

Use `test_scraper.py` to test a single scraper in isolation with a visible browser:

```bash
python test_scraper.py
```

Swap the imported scraper module at the top of the file (`qcgc`, `cardcenter`, or `aligned`) to test each one.

## Deployment

Render.com via `render.yaml`. Build/start commands and env vars are declared there. Credentials are set as Render environment variables, not in `.env`.

## Architecture

**Backend (`main.py`):**
- `POST /api/refresh` — launches headless Chromium, runs all 3 scrapers concurrently, caches results in-memory
- `GET /api/rates` — returns cached results
- Static `index.html` is served at `/`

**Scrapers (`scrapers/`):**
- Each exports `async def fetch_rates(browser: Browser) -> list[dict]`
- Returns records with keys: `brand`, `denomination`, and a source-specific rate key (`qcgc`, `cardcenter`, or `aligned`)
- `aligned.py` reuses `aligned_session.json` instead of logging in fresh each time

**Merge logic (`main.py`):**
- Groups records by `(brand.lower(), denomination)` key
- Upserts each source's rate into a unified record; missing sources default to `None`
- Returns list sorted by brand + denomination

**Frontend (`static/index.html`):**
- Vanilla JS SPA; calls `/api/refresh` then `/api/rates`
- Highlights the best (highest) rate per row in green
- No bundler or framework — edit directly

## Scraper Implementation Notes

**QCGC (`scrapers/qcgc.py`):**
- Login at `https://portal.qcgc.io/login` (not qcgc.io)
- Uses Livewire/Filament — must use `.type()` (not `.fill()`) to trigger wire:model bindings
- Paginates through results using `button.fi-pagination-next-btn` via `dispatch_event("click")` (button is in DOM but not visible)
- Row selector: `tr.fi-ta-row`; cells: `td[class*="fi-ta-cell-brand"]`, `td.fi-ta-cell-denomination`, `td.fi-ta-cell-payout-rate`
- Text lives inside `.fi-ta-text` inside each cell

**CardCenter (`scrapers/cardcenter.py`):**
- Login at `https://cardcenter.cc/Account/Login`; rates at `https://cardcenter.cc/Rates`
- Login field IDs: `#Email`, `#Password`; submit: `button[type="submit"]`
- Table uses a two-row pattern per brand: a header row (`td[colspan='100']` with `span.fw-semibold`) followed by data rows
- Data rows identified by `td a[href^="/Rates/"]`; denomination in `tds[0]`, rate in `tds[1]`

**Aligned Incentives (`scrapers/aligned.py`):**
- Rates are on the Deals page: `https://portal.alignedincentiv.es/Seller/Deals`
- Google OAuth blocks Playwright's bundled Chromium for login, so `save_session_aligned.py` uses a real Chrome install to log in and exports both `.chrome_profile/` and `aligned_session.json`
- Auth priority in `fetch_rates`: (1) `ALIGNED_SESSION` env var → decoded to `aligned_session.json` (Render), (2) `aligned_session.json` with Playwright Chromium, (3) `.chrome_profile/` with Chrome as local fallback
- Each row (`tr.expandable`) is a deal with multiple brand/denomination pairs in `.brands-column div` and matching rates in `.buy-rate-column div`; parsed via regex `$<denom> <brand>`
- Runs headless in all cases

**Deployment (Render):**
- Run `save_session_aligned.py` locally after logging in — it prints a base64 string to use as the `ALIGNED_SESSION` env var in Render
- `render.yaml` declares `ALIGNED_SESSION`, `QCGC_EMAIL`, `QCGC_PASSWORD`, `CARDCENTER_EMAIL`, `CARDCENTER_PASSWORD`
