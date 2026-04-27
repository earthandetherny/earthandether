"""
scrape.py — Earth + Ether listing updater
Runs in GitHub Actions every Monday. Uses Playwright (headless Chromium)
to visit the live Chairish shop, extract active listings, and write listings.json.
"""

import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SHOP_URL   = "https://www.chairish.com/shop/earthandether"
OUT_FILE   = Path(__file__).parent.parent / "listings.json"
MAX_ITEMS  = 10

# ── Selectors to try for product cards ──────────────────────────
# Chairish is a React SPA; class names may change, so we try several.
CARD_SELECTORS = [
    "article[data-product-id]",
    "[data-testid='listing-card']",
    ".listing-card",
    ".product-card",
    "li.chakra-wrap__listitem",
]

def scrape_shop(page):
    print(f"Navigating to {SHOP_URL} …")
    page.goto(SHOP_URL, wait_until="domcontentloaded", timeout=30_000)

    # Wait for at least one card selector to appear
    found_selector = None
    for sel in CARD_SELECTORS:
        try:
            page.wait_for_selector(sel, timeout=8_000)
            found_selector = sel
            print(f"Found cards with selector: {sel}")
            break
        except PWTimeout:
            continue

    if not found_selector:
        # Last resort: let the page fully settle and grab every product link
        time.sleep(5)

    # Extract all listing data via JS evaluation
    items = page.evaluate("""() => {
        const results = [];
        const seen    = new Set();

        // Strategy 1: data-product-id attributes
        document.querySelectorAll('[data-product-id]').forEach(card => {
            const a     = card.querySelector('a[href*="/product/"]');
            const img   = card.querySelector('img');
            const title = card.querySelector('h2,h3,[class*="title"],[class*="Title"]');
            if (!a || !img) return;
            const url  = a.href.split('?')[0];
            const src  = img.dataset.src || img.dataset.lazySrc || img.src || '';
            const text = (title?.textContent || '').trim();
            if (url && src && !seen.has(url)) {
                seen.add(url);
                results.push({ url, img: src, title: text });
            }
        });

        // Strategy 2: any <a> linking to a /product/ page
        if (results.length === 0) {
            document.querySelectorAll('a[href*="chairish.com/product/"]').forEach(a => {
                const card  = a.closest('li,article,div[class*="card"],div[class*="item"]') || a;
                const img   = card.querySelector('img');
                const title = card.querySelector('h2,h3,p[class*="title"]');
                if (!img) return;
                const url  = a.href.split('?')[0];
                const src  = img.dataset.src || img.src || '';
                const text = (title?.textContent || a.title || '').trim();
                if (url && src && !seen.has(url)) {
                    seen.add(url);
                    results.push({ url, img: src, title: text });
                }
            });
        }

        return results;
    }""")

    print(f"Raw items found: {len(items)}")
    return items


def verify_active(page, url):
    """Return True if the product page still looks active (not sold)."""
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=15_000)
        if resp and resp.status in (404, 410):
            return False
        # Check for sold / unavailable signals in the page
        body = page.content().lower()
        sold_signals = ["this item has been sold", "item is no longer available",
                        "sold out", "unavailable", "/shop/earthandether\""]
        if any(s in body for s in sold_signals[:3]):   # last entry is a redirect signal
            return False
        return True
    except Exception as e:
        print(f"  verify error for {url}: {e}")
        return True   # assume active on error


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx  = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = ctx.new_page()

        # ── Step 1: scrape the shop page ────────────────────────
        try:
            raw = scrape_shop(page)
        except Exception as e:
            print(f"ERROR scraping shop: {e}", file=sys.stderr)
            # Keep existing listings.json unchanged
            sys.exit(0)

        if not raw:
            print("No items found — keeping existing listings.json", file=sys.stderr)
            sys.exit(0)

        # ── Step 2: verify each item is still active ─────────────
        active = []
        for item in raw[:MAX_ITEMS + 5]:   # check a few extras
            print(f"Checking: {item['url'][:70]} …", end=" ")
            if verify_active(page, item["url"]):
                print("✓ active")
                active.append(item)
            else:
                print("✗ sold/removed — skipping")
            if len(active) >= MAX_ITEMS:
                break

        browser.close()

    if not active:
        print("No active items after verification — keeping existing file")
        sys.exit(0)

    # ── Step 3: write listings.json ──────────────────────────────
    out = json.dumps(active[:MAX_ITEMS], indent=2, ensure_ascii=False)
    OUT_FILE.write_text(out, encoding="utf-8")
    print(f"\n✅  Wrote {len(active)} active listings to {OUT_FILE}")


if __name__ == "__main__":
    main()
