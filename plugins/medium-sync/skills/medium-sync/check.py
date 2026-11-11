"""List posts from your site's RSS feed that are new or changed since they were synced to Medium.

State lives in ~/.medium-sync/ (outside the plugin):
  config.json     {"feed": "https://example.com/rss.xml"}
  published.json  written by --record

Usage: python check.py                          -> prints JSON {new: [...], changed: [...]}
       python check.py --record URL MEDIUM_URL  -> store the current hash for URL
"""
import hashlib, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOME = Path.home() / ".medium-sync"
CONFIG = HOME / "config.json"
LOG = HOME / "published.json"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "medium-sync"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")


def article_hash(url):
    # Hash only the <article> body so nav or footer changes don't count as edits.
    html = get(url)
    m = re.search(r"<article[^>]*>(.*?)</article>", html, re.S)
    return hashlib.sha256((m.group(1) if m else html).encode()).hexdigest()[:16]


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    log = load(LOG)
    if sys.argv[1:2] == ["--record"]:
        url, medium = sys.argv[2], sys.argv[3]
        log[url] = {"medium": medium, "hash": article_hash(url)}
        HOME.mkdir(exist_ok=True)
        LOG.write_text(json.dumps(log, indent=2))
        print("recorded", url)
        sys.exit()

    feed = load(CONFIG).get("feed")
    if not feed:
        sys.exit(f'No feed configured. Write {CONFIG} as {{"feed": "https://your-site/rss.xml"}}')

    out = {"new": [], "changed": []}
    for item in ET.fromstring(get(feed)).iter("item"):
        url = item.findtext("link")
        post = {"url": url, "title": item.findtext("title"),
                "tags": [c.text for c in item.iter("category")][:5]}
        if url not in log:
            out["new"].append(post)
        elif log[url]["hash"] != article_hash(url):
            out["changed"].append({**post, "medium": log[url]["medium"]})
    print(json.dumps(out, indent=2))
