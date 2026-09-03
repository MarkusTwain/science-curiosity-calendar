#!/usr/bin/env python3
"""
Daily science/curiosity news collector.

No API key is required. It reads RSS feeds, filters to recent items,
deduplicates them, assigns categories, and writes data.json + data.js.

The source article is always linked; the RSS description is used as the
short summary rather than copying article text.
"""
from __future__ import annotations
import json, re, html, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "data.json"
DATA_JS = ROOT / "data.js"

# Google News RSS gives us broad coverage while preserving links to the
# original publishers. Queries deliberately target different curiosity areas.
FEEDS = [
    ("Science", "https://news.google.com/rss/search?q=science+discovery+when:7d&hl=en-US&gl=US&ceid=US:en"),
    ("Space", "https://news.google.com/rss/search?q=space+NASA+astronomy+when:7d&hl=en-US&gl=US&ceid=US:en"),
    ("Nature", "https://news.google.com/rss/search?q=nature+wildlife+climate+discovery+when:7d&hl=en-US&gl=US&ceid=US:en"),
    ("Archaeology", "https://news.google.com/rss/search?q=archaeology+ancient+discovery+when:7d&hl=en-US&gl=US&ceid=US:en"),
    ("AI & Robotics", "https://news.google.com/rss/search?q=artificial+intelligence+AI+robot+robotics+when:7d&hl=en-US&gl=US&ceid=US:en"),
    ("Technology", "https://news.google.com/rss/search?q=technology+innovation+breakthrough+when:7d&hl=en-US&gl=US&ceid=US:en"),
]

KEYWORDS = {
    "AI & Robotics": ["artificial intelligence", " ai ", "robot", "robotics", "humanoid", "machine learning", "agentic", "autonomous"],
    "Space": ["space", "nasa", "esa", "astronomy", "planet", "moon", "mars", "asteroid", "telescope", "galaxy", "rocket"],
    "Archaeology": ["archaeology", "archaeological", "ancient", "excavation", "tomb", "ruins", "skeleton", "artifact"],
    "Nature": ["wildlife", "animal", "species", "forest", "ocean", "coral", "climate", "drought", "ecosystem", "biodiversity"],
    "Technology": ["technology", "innovation", "chip", "quantum", "battery", "computer", "engineering"],
    "Science": ["science", "research", "study", "discovery", "experiment", "physics", "biology", "chemistry"],
}

def clean(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()

def parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s[:25], "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        try:
            return datetime.strptime(s[:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        except Exception:
            return None

def fetch(url):
    req = Request(url, headers={"User-Agent": "ScienceCuriosityCalendar/1.0"})
    with urlopen(req, timeout=25) as r:
        return r.read()

def category_for(title, desc, fallback):
    text = f" {title.lower()} {desc.lower()} "
    if fallback == "AI & Robotics":
        return fallback
    # Give specialist feeds priority, but allow cross-category classification.
    for cat in ["AI & Robotics", "Space", "Archaeology", "Nature", "Technology", "Science"]:
        if any(k in text for k in KEYWORDS[cat]):
            return cat
    return fallback

def parse_feed(xml_bytes, fallback):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.findall(".//item"):
        title = clean(item.findtext("title", ""))
        link = clean(item.findtext("link", ""))
        desc = clean(item.findtext("description", ""))
        pub = parse_date(item.findtext("pubDate", ""))
        source_el = item.find("source")
        source = clean(source_el.text if source_el is not None else "")
        if not title or not link:
            continue
        out.append({
            "title": title,
            "url": link,
            "summary": desc[:500],
            "source": source or "News source",
            "published": pub.isoformat() if pub else None,
            "category": category_for(title, desc, fallback),
        })
    return out

def short_summary(desc, title):
    if not desc:
        return f"New reporting on {title.lower()}."
    desc = re.sub(r"\s+", " ", desc).strip()
    # Keep the card readable; RSS descriptions vary by publisher.
    return desc[:360].rstrip(" .") + ("…" if len(desc) > 360 else "")

def make_story(x):
    published = x["published"] or datetime.now(timezone.utc).isoformat()
    dt = datetime.fromisoformat(published)
    return {
        "date": dt.date().isoformat(),
        "category": x["category"],
        "title": x["title"],
        "summary": short_summary(x["summary"], x["title"]),
        "why": "A recent development selected for the calendar because it connects to a broader question, discovery, technology or event worth following.",
        "source": x["source"],
        "url": x["url"],
    }

def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    candidates = []
    for cat, url in FEEDS:
        try:
            for x in parse_feed(fetch(url), cat):
                if x["published"]:
                    dt = datetime.fromisoformat(x["published"])
                    if dt >= cutoff:
                        candidates.append(x)
        except Exception as e:
            print(f"Feed failed: {cat}: {e}")

    # Deduplicate by URL and normalized title.
    seen, fresh = set(), []
    for x in sorted(candidates, key=lambda z: z["published"] or "", reverse=True):
        key = (x["url"], re.sub(r"\W+", "", x["title"].lower()))
        if key in seen:
            continue
        seen.add(key)
        fresh.append(make_story(x))

    # Keep a rolling 60-day archive. Prefer no more than 8 stories/category/week
    # to prevent one news-heavy topic from taking over the calendar.
    old = json.loads(DATA_JSON.read_text(encoding="utf-8")) if DATA_JSON.exists() else []
    merged = fresh + [s for s in old if s.get("date", "") >= (now - timedelta(days=60)).date().isoformat()]
    unique = {}
    for s in merged:
        unique[s["url"]] = s
    merged = list(unique.values())

    # Limit the number of items per category per week.
    counts = {}
    selected = []
    for s in sorted(merged, key=lambda z: (z.get("date",""), z.get("title","")), reverse=True):
        week = s["date"][:8]
        key = (week, s["category"])
        if counts.get(key, 0) >= 8:
            continue
        counts[key] = counts.get(key, 0) + 1
        selected.append(s)

    selected.sort(key=lambda s: (s["date"], s["title"]), reverse=True)
    DATA_JSON.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    DATA_JS.write_text(
        "// Automatically updated by GitHub Actions. Do not edit manually.\nconst STORIES = "
        + json.dumps(selected, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8"
    )
    print(f"Updated {len(selected)} stories.")

if __name__ == "__main__":
    main()
