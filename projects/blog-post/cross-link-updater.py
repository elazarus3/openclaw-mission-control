#!/usr/bin/env python3
"""Batch cross-link injector for CNC blog posts."""
import json, re, time, base64, os, html
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from agentmail import AgentMail

WORDPRESS = "https://www.clinicalnutritioncenter.com"
USER_PASS = "drlazarus:1ggq 5syX 9ztB YhUs P2FH aEEh"
b64_auth = base64.b64encode(USER_PASS.encode()).decode()
SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Basic {b64_auth}",
    "Content-Type": "application/json",
    "User-Agent": "curl/7.88.1"
})
AGENTMAIL_API_KEY = os.getenv(
    "AGENTMAIL_API_KEY",
    "am_us_f4966bf52dd46dda0021cc0bb8d91f6ec8971b725709f04b088104514035bc3e"
)
REPORT_TO = "ethanlazarus@gmail.com"
REPORT_FROM = "info@clinicalnutritioncenter.com"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def api_get(url, params=None):
    r = SESSION.get(url, params=params, timeout=30)
    return r.json() if r.ok else None

def api_post(url, data):
    r = SESSION.post(url, json=data, timeout=30)
    return r.json() if r.ok else None

def get_link_regions(html_text):
    """Return list of (start, end) char positions of existing <a> tags."""
    regions = []
    for m in re.finditer(r'<a\b[^>]*>.*?</a>', html_text, re.DOTALL | re.IGNORECASE):
        regions.append((m.start(), m.end()))
    return regions

def strip_all_links(html_text):
    """Remove ALL <a> tags, keeping inner text. Use this before re-injecting to prevent nested links."""
    result = re.sub(r'<a\b[^>]*>([^<]*)</a>', r'\1', html_text, flags=re.IGNORECASE | re.DOTALL)
    result = re.sub(r'<a\b[^>]*/?>', '', result)
    result = re.sub(r'</a>', '', result)
    return result

def build_char_map(html_text):
    """
    Walk html_text directly (NOT a pre-unescaped copy) and build:
    - plain text
    - char_map: plain_pos -> html_pos
    This avoids the offset-mismatch bug where char_map positions don't match
    the original HTML when entities are present.
    """
    plain_chars = []
    char_map = []
    hp = 0
    html_len = len(html_text)

    while hp < html_len:
        c = html_text[hp]
        if c == '<':
            while hp < html_len and html_text[hp] != '>':
                hp += 1
            hp += 1
        elif c == '&':
            end = hp + 1
            while end < html_len and html_text[end] not in ' \n\t<>;' and end - hp < 15:
                end += 1
            if end < html_len and html_text[end] == ';':
                end += 1
            entity_decoded = html.unescape(html_text[hp:end])
            for ch in entity_decoded:
                char_map.append((len(plain_chars), hp))
                plain_chars.append(ch)
            hp = end
        else:
            char_map.append((len(plain_chars), hp))
            plain_chars.append(c)
            hp += 1

    return char_map, ''.join(plain_chars)

def inject_links(html_text, keyword_url_map):
    """
    Inject <a href> links around keyword occurrences in HTML.
    Skips keywords already inside existing <a> tags.
    Returns (new_html, list_of_injected_words).
    """
    char_map, plain = build_char_map(html_text)
    if not plain:
        return html_text, []

    link_regions = get_link_regions(html_text)

    def inside_link(pos):
        for s, e in link_regions:
            if s <= pos < e:
                return True
        return False

    result = html_text
    shifts = 0
    last_pos = len(result) + 1000000
    injected = []

    # Process longest keywords first to avoid partial replacements
    for keyword, target_url in sorted(keyword_url_map.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(rf'\b({re.escape(keyword)})\b', re.IGNORECASE)

        for m in pattern.finditer(plain):
            ps, pe = m.start(), m.end()
            hs = he = None
            for (pp, ph) in char_map:
                if pp == ps and hs is None:
                    hs = ph
                if pe > 0 and pp == pe - 1:
                    he = ph + 1
            if hs is None or he is None:
                continue

            adj_s = hs + shifts
            adj_e = he + shifts

            if adj_s >= last_pos:
                continue
            if inside_link(adj_s) or inside_link(adj_e - 1):
                continue

            ctx_start = max(0, adj_s - 20)
            snippet = result[ctx_start:adj_e + 5]
            if 'href=' in snippet[:adj_s - ctx_start + 5]:
                continue

            tag = f'<a href="{target_url}">{keyword}</a>'
            result = result[:adj_s] + tag + result[adj_e:]
            shifts += len(tag) - (adj_e - adj_s)
            last_pos = adj_s
            injected.append(keyword)
            link_regions.append((adj_s, adj_s + len(tag)))

    return result, injected

# ─── Fetch posts ──────────────────────────────────────────────────────────────

print("Fetching blog posts...")
all_posts = []
page = 1
while True:
    posts = api_get(f"{WORDPRESS}/wp-json/wp/v2/posts", {
        "post_type": "post", "per_page": 50, "status": "publish",
        "_embed": 1, "orderby": "date", "order": "asc",
        "after": "2025-01-01T00:00:00", "page": page
    })
    if not posts:
        break
    all_posts.extend(posts)
    print(f"  Page {page}: {len(posts)} (total: {len(all_posts)})")
    if len(posts) < 50:
        break
    page += 1
    time.sleep(0.4)

print(f"\nTotal: {len(all_posts)}")

# ─── Build link map ───────────────────────────────────────────────────────────

LINK_TARGETS = {
    "wegovy": [], "ozempic": [], "semaglutide": [],
    "tirzepatide": [], "zepbound": [], "mounjaro": [],
    "orforglipron": [], "foundayo": [],
    "glp-1": [], "glp-1 medications": [],
    "registered dietitian": [], "dietitian near me": [],
    "medical weight loss denver": [], "denver": [],
    "greenwood village": [], "colorado": [],
    "fsa": [], "hsa": [],
    "fatty liver": [], "mash": [], "nash": [],
    "heart health": [], "cardiovascular": [],
    "type 2 diabetes": [],
    "plateau": [], "stall": [],
    "oral glp-1": [], "injection": [],
    "side effect": [], "sulfur burps": [],
    "surgery safety": [], "fasting": [],
    "compounded": [],
    "protein strategy": [], "protein on glp-1": [],
    "muscle": [], "exercise": [], "workout": [],
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

for kw in LINK_TARGETS:
    seen = set()
    LINK_TARGETS[kw] = [e for e in LINK_TARGETS[kw] if e["id"] not in seen and not seen.add(e["id"])]

print("\nKeyword map:")
for kw, targets in sorted(LINK_TARGETS.items(), key=lambda x: -len(x[1])):
    if targets:
        print(f"  '{kw}': {len(targets)} posts")

# ─── Update posts ─────────────────────────────────────────────────────────────

print("\nUpdating posts...")
updated = skipped = errors = 0
updated_ids = []

for p in all_posts:
    pid = p["id"]
    title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))
    content_html = p.get("content", {}).get("rendered", "")
    # Strip all existing links first — prevents nested/duplicate link corruption
    clean_base = strip_all_links(content_html)
    links_added = []

    # Build keyword -> url map for this post (skip self-links)
    kw_map = {}
    for keyword, targets in sorted(LINK_TARGETS.items(), key=lambda x: -len(x[0])):
        if not targets:
            continue
        target = next((t for t in targets if t["id"] != pid), None)
        if target:
            kw_map[keyword] = target["url"]

    new_html, injected = inject_links(clean_base, kw_map)
    for kw, url in [(k, v) for k, v in kw_map.items() if k in injected]:
        target_title = next((t["title"][:40] for t in LINK_TARGETS.get(kw, []) if t["url"] == url), kw)
        links_added.append(f"  + '{kw}' → {target_title}")

    if links_added:
        result = api_post(f"{WORDPRESS}/wp-json/wp/v2/posts/{pid}", {"content": new_html})
        if result and "id" in result:
            print(f"\n✓ [{pid}] {title[:55]}")
            for l in links_added[:6]:
                print(l)
            updated += 1
            updated_ids.append(pid)
        else:
            print(f"\n✗ [{pid}] FAILED")
            errors += 1
        time.sleep(0.5)
    else:
        skipped += 1

print(f"\n=== DONE ===  Updated: {updated}  Skipped: {skipped}  Errors: {errors}")

# ─── Email Report ─────────────────────────────────────────────────────────────

def send_report():
    if not AGENTMAIL_API_KEY:
        print("[EMAIL] No API key, skipping")
        return
    updated_posts = [p for p in all_posts if p["id"] in updated_ids]
    run_date = datetime.now().strftime("%B %d, %Y at %I:%M %p MST")

    rows = ""
    for p in updated_posts:
        t = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))
        u = p.get("link", "")
        pid = p.get("id")
        d = p.get("date", "")[:10]
        rows += f'<tr><td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;font-size:13px;">{d}</td><td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;"><a href="{u}" style="color:#1a5276;text-decoration:none;font-weight:500;">{t}</a></td><td style="padding:10px 14px;border-bottom:1px solid #e8e8e8;color:#555;font-size:12px;">#{pid}</td></tr>'

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:700px;margin:40px auto;">
    <div style="background:linear-gradient(135deg,#1a5276,#1e8449);padding:32px 36px;border-radius:12px 12px 0 0;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:48px;height:48px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;">🔗</div>
        <div><h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;">Cross-Link Update Complete</h1>
        <p style="margin:4px 0 0;color:rgba(255,255,255,0.8);font-size:13px;">{run_date}</p></div>
      </div>
    </div>
    <div style="background:#fff;padding:24px 36px;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0;">
      <div style="display:flex;gap:16px;">
        <div style="flex:1;background:#f0faf4;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #c8e6c9;"><div style="font-size:32px;font-weight:800;color:#1e8449;">{updated}</div><div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Posts Updated</div></div>
        <div style="flex:1;background:#fefaf5;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #ffe0b2;"><div style="font-size:32px;font-weight:800;color:#e67e22;">{skipped}</div><div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Skipped</div></div>
        <div style="flex:1;background:#fef5f5;border-radius:10px;padding:18px 20px;text-align:center;border:1px solid #ffcdd2;"><div style="font-size:32px;font-weight:800;color:#c0392b;">{errors}</div><div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;">Errors</div></div>
      </div>
    </div>
    <div style="background:#fff;padding:0 36px 24px;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0;">
      <h3 style="margin:0 0 16px;padding-top:20px;font-size:15px;color:#333;border-bottom:2px solid #1a5276;padding-bottom:10px;">Updated Posts — Clinical Nutrition Center</h3>
      <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.08);">
        <thead><tr style="background:#1a5276;"><th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Date</th><th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Post</th><th style="padding:10px 14px;text-align:left;color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">WP ID</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <div style="background:#f8f9fa;padding:20px 36px;border-radius:0 0 12px 12px;border:1px solid #e0e0e0;border-top:none;">
      <p style="margin:0;font-size:12px;color:#888;text-align:center;">Clinical Nutrition Center · Greenwood Village, CO · Automated Content Engine</p>
    </div>
  </div>
</body></html>"""

    try:
        client = AgentMail(api_key=AGENTMAIL_API_KEY)
        result = client.inboxes.messages.send(
            inbox_id="ethanlazarus@agentmail.to",
            to=REPORT_TO,
            subject=f"🔗 Cross-Link Report: {updated} posts updated — {datetime.now().strftime('%b %d, %Y')}",
            html=html
        )
        print(f"[EMAIL] Sent: {result.message_id}")
    except Exception as e:
        print(f"[EMAIL] Failed: {e}")

send_report()
