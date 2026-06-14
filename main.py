import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

import importlib
import brand_aliases

from scrapers.qcgc import fetch_rates as fetch_qcgc
from scrapers.cardcenter import fetch_rates as fetch_cardcenter
from scrapers.aligned import fetch_rates as fetch_aligned


def _normalize_brand(name: str, aliases: dict) -> str:
    """Return a canonical brand name for grouping and display."""
    lower = name.strip().lower()
    if lower in aliases:
        return aliases[lower]
    if lower.startswith("the "):
        stripped = name.strip()[4:]
        if stripped.lower() in aliases:
            return aliases[stripped.lower()]
        return stripped
    return name.strip()

app = FastAPI()

_cache: dict = {"rates": [], "last_updated": None, "errors": []}


def _merge(qcgc_list, cc_list, aligned_list) -> list[dict]:
    importlib.reload(brand_aliases)  # pick up edits to brand_aliases.py without restarting
    aliases = brand_aliases.ALIASES
    combined: dict[tuple, dict] = {}

    def upsert(rows, field):
        for r in rows:
            canonical = _normalize_brand(r["brand"], aliases)
            key = (canonical.lower(), r["denomination"])
            combined.setdefault(key, {"brand": canonical, "denomination": r["denomination"]})
            combined[key][field] = r.get(field)

    upsert(qcgc_list, "qcgc")
    upsert(cc_list, "cardcenter")
    upsert(aligned_list, "aligned")

    for entry in combined.values():
        entry.setdefault("qcgc", None)
        entry.setdefault("cardcenter", None)
        entry.setdefault("aligned", None)

    return sorted(combined.values(), key=lambda x: (x["brand"].lower(), x["denomination"]))


@app.post("/api/refresh")
async def refresh():
    results = {"qcgc": [], "cardcenter": [], "aligned": []}
    errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        qcgc_r, cc_r, aligned_r = await asyncio.gather(
            fetch_qcgc(browser),
            fetch_cardcenter(browser),
            fetch_aligned(browser),
            return_exceptions=True,
        )
        await browser.close()

    for label, result, key in [
        ("QCGC", qcgc_r, "qcgc"),
        ("CardCenter", cc_r, "cardcenter"),
        ("Aligned Incentives", aligned_r, "aligned"),
    ]:
        if isinstance(result, Exception):
            errors.append(f"{label}: {result}")
        else:
            results[key] = result

    _cache["rates"] = _merge(results["qcgc"], results["cardcenter"], results["aligned"])
    _cache["last_updated"] = datetime.now(timezone.utc).isoformat()
    _cache["errors"] = errors
    return _cache


@app.get("/api/rates")
async def get_rates():
    return _cache


app.mount("/", StaticFiles(directory="static", html=True), name="static")
