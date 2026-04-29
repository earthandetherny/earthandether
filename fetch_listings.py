"""
fetch_listings.py — Earth + Ether
Fetches active Etsy listings via official API v3.
Sold items are automatically excluded (state=active).
Writes listings.json to repo root.

Required GitHub Secret: ETSY_API_KEY
"""

import json, os, sys, urllib.request, urllib.error
from pathlib import Path

SHOP     = "earthandetherny"
API_KEY  = os.environ.get("ETSY_API_KEY", "")
OUT_FILE = Path(__file__).parent / "listings.json"
LIMIT    = 12   # number of cards on the website

def etsy(path, params):
    url = f"https://api.etsy.com/v3/application/{path}?{params}"
    req = urllib.request.Request(url, headers={
        "x-api-key": API_KEY,
        "Accept": "application/json",
    })
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def best_img(images):
    for key in ("url_fullxfull", "url_570xN", "url_170x135"):
        v = images[0].get(key, "") if images else ""
        if v: return v
    return ""

def main():
    if not API_KEY:
        print("ERROR: ETSY_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching active listings from Etsy shop '{SHOP}' …")

    try:
        data = etsy(
            f"shops/{SHOP}/listings/active",
            f"includes=Images&limit={LIMIT}&sort_on=created&sort_order=down&state=active"
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body[:300]}", file=sys.stderr)
        sys.exit(1)

    results = data.get("results", [])
    print(f"  → {data.get('count')} total active listings, got {len(results)}")

    items, seen = [], set()
    for r in results:
        lid = r.get("listing_id")
        if not lid or lid in seen:
            continue
        seen.add(lid)
        img = best_img(r.get("images", []))
        if not img:
            continue
        items.append({
            "url":   f"https://www.etsy.com/listing/{lid}",
            "img":   img,
            "title": r.get("title", "").strip(),
        })

    if not items:
        print("No active listings with images found — keeping existing file")
        sys.exit(0)

    OUT_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    print(f"  ✓ Wrote {len(items)} listings to listings.json")
    for i in items:
        print(f"    • {i['title'][:65]}")

if __name__ == "__main__":
    main()
