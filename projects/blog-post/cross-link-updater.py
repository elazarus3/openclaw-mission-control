#!/usr/bin/env python3
"""Batch cross-link injector for CNC blog posts. Uses requests library."""
import json, re, time, base64, sys, os
import requests
from requests.auth import HTTPBasicAuth
from agentmail import AgentMail
from datetime import datetime

AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY", "am_us_f4966bf52dd46dda0021cc0bb8d91f6ec8971b725709f04b088104514035bc3e")
REPORT_TO = "ethanlazarus@gmail.com"
REPORT_FROM = "info@clinicalnutritioncenter.com"

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
            updated_ids.append(pid)
        else:
            print(f"\n✗ [{pid}] FAILED")
            errors += 1
        time.sleep(0.5)
    else:
        skipped += 1

print(f"\n=== DONE ===\n  Updated: {updated}\n  Skipped (no links): {skipped}\n  Errors: {errors}")

# ── Email Report ───────────────────────────────────────────────────────────────
def send_report(all_posts, updated_ids, skipped, errors):
    """Send pretty HTML report via AgentMail."""
    if not AGENTMAIL_API_KEY:
        print("[EMAIL] No API key, skipping report")
        return

    updated_posts = [p for p in all_posts if p["id"] in updated_ids]
    run_date = datetime.now().strftime("%B %d, %Y at %I:%M %p MST")

    # Build post rows
    rows = ""
    for p in updated_posts:
        title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))
        url = p.get("link", "")
        pid = p.get("id")
        date = p.get("date", "")[:10]
        rows += f"""<tr>
            <td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;font-size:13px;">{date}</td>
            <td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;"><a href="{url}" style="color:#1a5276;text-decoration:none;font-weight:500;">{title}</a></td>
            <td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;color:#555;font-size:12px;">#{pid}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cross-Link Report</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:700px;margin:40px auto;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1a5276,#1e8449);padding:32px 36px;border-radius:12px 12px 0 0;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:48px;height:48px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;">🔗</div>
        <div>
          <h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;">Cross-Link Update Complete</h1>
          <p style="margin:4px 0 0;color:rgba(255,255,255,0.8);font-size:13px;">{run_date}</p>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div style="background:#fff;padding:24px 36px;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0;">
      <div style="display:flex;gap:16px;">
        <div style="flex:1;background:#f0faf4;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #c8e6c9;">
          <div style="font-size:32px;font-weight:800;color:#1e8449;">{updated}</div>
          <div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Posts Updated</div>
        </div>
        <div style="flex:1;background:#fefaf5;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #ffe0b2;">
          <div style="font-size:32px;font-weight:800;color:#e67e22;">{skipped}</div>
          <div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Skipped</div>
        </div>
        <div style="flex:1;background:#fef5f5;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #ffcdd2;">
          <div style="font-size:32px;font-weight:800;color:#c0392b;">{errors}</div>
          <div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Errors</div>
        </div>
      </div>
    </div>

    <!-- Post Table -->
    <div style="background:#fff;padding:0 36px 24px;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0;">
      <h3 style="margin:0 0 16px;padding-top:20px;font-size:15px;color:#333;border-bottom:2px solid #1a5276;padding-bottom:10px;">
        Updated Posts — Clinical Nutrition Center
      </h3>
      <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.08);">
        <thead>
          <tr style="background:#1a5276;">
            <th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Date</th>
            <th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Post</th>
            <th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">WP ID</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <!-- Footer -->
    <div style="background:#f8f9fa;padding:20px 36px;border-radius:0 0 12px 12px;border:1px solid #e0e0e0;border-top:none;">
      <p style="margin:0;font-size:12px;color:#888;text-align:center;">
        Clinical Nutrition Center · Greenwood Village, CO · Automated Content Engine
      </p>
    </div>

  </div>
</body>
</html>"""

    try:
        client = AgentMail(api_key=AGENTMAIL_API_KEY)
        result = client.inboxes.messages.send(
            inbox_id="ethanlazarus@agentmail.to",
            to=REPORT_TO,
            subject=f"🔗 Cross-Link Report: {updated} posts updated — {datetime.now().strftime('%b %d, %Y')}",
            html=html
        )
        print(f"[EMAIL] Report sent: {result.message_id}")
    except Exception as e:
        print(f"[EMAIL] Failed to send report: {e}")

# ── Track updated post IDs for the report ─────────────────────────────────────
updated_ids = []  # track updated post IDs for the email report

print(f"\n=== DONE ===\n  Updated: {updated}\n  Skipped (no links): {skipped}\n  Errors: {errors}\n")

# Send report
try:
    send_report(all_posts, updated_ids, skipped, errors)
except Exception as e:
    print(f"[EMAIL] Report error: {e}")
