#!/usr/bin/env python3
"""Batch cross-link injector for CNC blog posts. Uses requests library."""
import json, re, time, base64
import requests
from requests.auth import HTTPBasicAuth

WORDPRESS = "https://www.clinicalnutritioncenter.com"
USER_PASS = "drlazarus:1ggq 5syX 9ztB YhUs P2FH aEEh"
AUTH = HTTPBasicAuth(*USER_PASS.split(":", 1))
SESSION = requests.Session()
SESSION.headers.update({"Authorization": f"Basic {base64.b64encode(USER_PASS.encode()).decode()}", "Content-Type": "application/json", "User-Agent": "curl/7.88.1"})

def get(url, params=None):
    r = SESSION.get(url, params=params, timeout=30)
    print(f"GET {r.url[:80]} → {r.status_code}")
    return r.json() if r.ok else None

def post(url, data):
    r = SESSION.post(url, json=data, timeout=30)
    print(f"POST {url[:80]} → {r.status_code}")
    return r.json() if r.ok else None

# ── Step 1: Fetch all posts ────────────────────────────────────────────────────
print("Fetching blog posts...")
all_posts = []
page = 1
while True:
    url = f"{WORDPRESS}/wp-json/wp/v2/posts"
    params = {"post_type": "post", "per_page": 50, "status": "publish", "_embed": 1,
              "orderby": "date", "order": "asc", "after": "2025-01-01T00:00:00", "page": page}
    posts = get(url, params)
    if not posts:
        break
    all_posts.extend(posts)
    print(f"  Page {page}: {len(posts)} posts (total: {len(all_posts)})")
    if len(posts) < 50:
        break
    page += 1
    time.sleep(0.4)

print(f"\nTotal posts: {len(all_posts)}")

# ── Step 2: Build cross-link map ──────────────────────────────────────────────
# Maps keyword → (url, id, title) of posts that are good targets for that keyword
LINK_TARGETS = {
    "wegovy":          [],
    "ozempic":         [],
    "semaglutide":     [],
    "tirzepatide":     [],
    "zepbound":        [],
    "mounjaro":        [],
    "orforglipron":    [],
    "foundayo":        [],
    "glp-1":           [],
    "glp-1 medications": [],
    "registered dietitian": [],
    "dietitian near me":  [],
    "medical weight loss denver": [],
    "denver":          [],
    "greenwood village": [],
    "colorado":        [],
    "fsa":             [],
    "hsa":             [],
    "fatty liver":     [],
    "mash":            [],
    "nash":            [],
    "heart health":    [],
    "cardiovascular":  [],
    "type 2 diabetes": [],
    "plateau":         [],
    "stall":           [],
    "oral glp-1":      [],
    "injection":       [],
    "side effect":     [],
    "sulfur burps":    [],
    "surgery safety":  [],
    "fasting":         [],
    "compounded":      [],
    "protein strategy": [],
    "protein on glp-1": [],
    "muscle":          [],
    "exercise":        [],
    "workout":         [],
}

for p in all_posts:
    title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))
    title_lc = title.lower()
    url = p.get("link", "")
    pid = p.get("id")
    entry = {"id": pid, "title": title, "url": url}
    for kw in LINK_TARGETS:
        if kw in title_lc and url:
            LINK_TARGETS[kw].append(entry)

# Deduplicate each list by id
for kw in LINK_TARGETS:
    seen = set()
    LINK_TARGETS[kw] = [e for e in LINK_TARGETS[kw] if e["id"] not in seen and not seen.add(e["id"])]

print("\nKeyword map built:")
for kw, targets in sorted(LINK_TARGETS.items(), key=lambda x: -len(x[1])):
    if targets:
        print(f"  '{kw}': {len(targets)} posts")

# ── Step 3: Update each post ──────────────────────────────────────────────────
print("\nUpdating posts...")
updated = skipped = errors = 0

for p in all_posts:
    pid = p["id"]
    title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))
    content_html = p.get("content", {}).get("rendered", "")

    new_html = content_html
    links_added = []

    for keyword, targets in sorted(LINK_TARGETS.items(), key=lambda x: -len(x[0])):
        if not targets:
            continue
        for target in targets:
            if target["id"] == pid:
                continue
            # Only link first occurrence of each keyword
            pattern = re.compile(rf'\b({re.escape(keyword)})\b', re.IGNORECASE)
            match = pattern.search(new_html)
            if match:
                # Avoid double-linking
                start = max(0, match.start() - 6)
                end = min(len(new_html), match.end() + 8)
                snippet = new_html[start:end]
                if "href=" in snippet:
                    continue
                safe_repl = f'<a href="{target["url"]}">{match.group(0)}</a>'
                new_html = new_html[:match.start()] + safe_repl + new_html[match.end():]
                links_added.append(f"  + '{keyword}' → {target['title'][:40]}")
                break  # one link per keyword per post

    if links_added:
        result = post(f"{WORDPRESS}/wp-json/wp/v2/posts/{pid}", {"content": new_html})
        if result and "id" in result:
            print(f"\n✓ [{pid}] {title[:55]}")
            for l in links_added[:5]:
                print(l)
            updated += 1
        else:
            print(f"\n✗ [{pid}] FAILED")
            errors += 1
        time.sleep(0.5)
    else:
        skipped += 1

print(f"\n=== DONE ===\n  Updated: {updated}\n  Skipped (no links): {skipped}\n  Errors: {errors}")
