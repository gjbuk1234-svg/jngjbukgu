#!/usr/bin/env python3
"""Build-time RSS fetcher for Netlify/Vercel/static hosting."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import json, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
RSS_URL = "https://www.korea.kr/rss/dept_mois.xml"
OUT = ROOT / "data" / "mois-rss.json"
FALLBACK = ROOT / "data" / "mois-rss-fallback.json"

def text(el, names):
    for name in names:
        child = el.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""

def fetch():
    req = Request(RSS_URL, headers={"User-Agent":"Mozilla/5.0 static-site-build"})
    with urlopen(req, timeout=20) as r:
        raw = r.read()
    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item"):
        title = text(item, ["title"])
        link = text(item, ["link"])
        date = text(item, ["pubDate", "date"])
        if title and link:
            items.append({"title":title, "url":link, "date":date, "source":"korea.kr RSS · 행정안전부"})
        if len(items) >= 5:
            break
    if len(items) < 5:
        raise RuntimeError("RSS에서 5건 미만의 항목을 받았습니다.")
    return items

try:
    items = fetch()
    status = "rss"
except Exception as e:
    # Checked-in fallback keeps the demo build reproducible if the RSS endpoint
    # is temporarily unavailable during a hosted build.
    items = json.loads(FALLBACK.read_text(encoding="utf-8"))
    status = "fallback"

OUT.write_text(json.dumps({
    "source_url": RSS_URL,
    "build_source": status,
    "items": items[:6]
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"RSS build complete: {status}, {len(items[:6])} items")
