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

def build_char_map(html_text):
    """
    Build a mapping from plain-text positions to HTML character positions.
    Returns list of (plain_pos, html_pos) for each character in plain text.
    Also returns the plain text itself.
    """
    html_unescaped = html.unescape(html_text)
    plain = re.sub(r'<[^>]+>', '', html_unescaped)
    plain = re.sub(r'\s+', ' ', plain).strip()

    char_map = []
    hp = 0
    pp = 0
    html_len = len(html_unescaped)
    plain_len = len(plain)

    while hp < html_len and pp < plain_len:
        c = html_unescaped[hp]
        if c == '<':
            while hp < html_len and html_unescaped[hp] != '>':
                hp += 1
            hp += 1
        elif c == '&':
            end = hp
            while (end < html_len and html_unescaped[end] not in ' \n\t<>;' and end - hp < 15):
                end += 1
            if end < html_len and html_unescaped[end] == ';':
                end += 1
            entity = html.unescape(html_unescaped[hp:end])
            for ch in entity:
                if pp < plain_len:
                    char_map.append((pp, hp))
                    pp += 1
            hp = end
        else:
            char_map.append((pp, hp))
            pp += 1
            hp += 1

    return char_map, plain

def inject_links(html_text, keyword, target_url, max_injections=1):
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

    pattern = re.compile(rf'\b({re.escape(keyword)})\b', re.IGNORECASE)
    html_positions = []

    for m in pattern.finditer(plain):
        ps, pe = m.start(), m.end()
        hs = he = None
        for (pp, ph) in char_map:
            if pp == ps and hs is None:
                hs = ph
            if pe > 0 and pp == pe - 1:
                he = ph + 1
        if hs is not None and he is not None:
            if not inside_link(hs) and not inside_link(he - 1):
                html_positions.append((hs, he, m.group(0)))

    # Sort descending so replacements don't shift offsets
    html_positions.sort(key=lambda x: -x[0])

    result = html_text
    injected = []
    for hs, he, word in html_positions[:max_injections]:
        # Final safety check on the surrounding HTML context
        ctx_start = max(0, hs - 5)
        ctx_end = min(len(result), he + 5)
        context = result[ctx_start:ctx_end]
        if 'href=' in context or '</a>' in context[:10]:
            continue
        tag = f'<a href="{target_url}">{word}</a>'
        result = result[:hs] + tag + result[he:]
        injected.append(word)
        # After replacing, rebuild link regions (offsets shifted)
        # Since we go in descending order, existing regions are still valid
        # but new region at hs will affect positions < hs — but we don't touch those

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
    new_html = content_html
    links_added = []

    for keyword, targets in sorted(LINK_TARGETS.items(), key=lambda x: -len(x[0])):
        if not targets:
            continue
        # Pick target that's not the current post
        target = None
        for t in targets:
            if t["id"] != pid:
                target = t
                break
        if not target:
            continue

        new_html, words = inject_links(new_html, keyword, target["url"], max_injections=1)
        if words:
            links_added.append(f"  + '{words[0]}' → {target['title'][:40]}")

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
