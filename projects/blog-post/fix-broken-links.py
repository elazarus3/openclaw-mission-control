#!/usr/bin/env python3
"""
Fix broken nested links in CNC posts.
Step 1: Strip ALL <a> tags, keeping inner text
Step 2: Re-inject clean links using the working inject_links approach
"""
import requests, base64, re, html, time
from requests.auth import HTTPBasicAuth

USER_PASS = 'drlazarus:1ggq 5syX 9ztB YhUs P2FH aEEh'
import os, json
from datetime import datetime
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def cleanup_old_backups(days=6):
    cutoff = time.time() - (days * 86400)
    for fn in os.listdir(BACKUP_DIR):
        fp = os.path.join(BACKUP_DIR, fn)
        if os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
            os.remove(fp)

def backup_post(pid, content):
    date_str = datetime.now().strftime('%Y%m%d')
    path = os.path.join(BACKUP_DIR, f'{pid}_{date_str}.json')
    with open(path, 'w') as f:
        json.dump({'post_id': pid, 'date': date_str, 'content': content}, f)

cleanup_old_backups()
b64 = base64.b64encode(USER_PASS.encode()).decode()
s = requests.Session()
s.headers.update({'Authorization': f"Basic {b64}", 'User-Agent': 'curl/7.88.1'})
WORDPRESS = "https://www.clinicalnutritioncenter.com"

def api_post(pid, data):
    r = s.post(f"{WORDPRESS}/wp-json/wp/v2/posts/{pid}", json=data, timeout=30)
    return r.json() if r.ok else None

def strip_all_links(html_text):
    """Remove ALL <a> tags from HTML, keeping inner text. Skip JSON-LD script blocks."""
    parts = re.split(r'(<script[^>]*type="application/ld\+json"[^>]*>.*?</script>)',
                     html_text, flags=re.IGNORECASE | re.DOTALL)
    result_parts = []
    for i, part in enumerate(parts):
        if re.match(r'<script[^>]*type="application/ld\+json"[^>]*>', part, re.IGNORECASE):
            result_parts.append(part)  # keep JSON-LD untouched
        else:
            part = re.sub(r'<a\b[^>]*>([^<]*)</a>', r'\1', part, flags=re.IGNORECASE | re.DOTALL)
            part = re.sub(r'<a\b[^>]*/?>', '', part)
            part = re.sub(r'</a>', '', part)
            result_parts.append(part)
    return ''.join(result_parts)

def sync_plain(html_text):
    """
    Walk html_text and build plain text + char_map (plain_pos -> html_pos).
    Skips HTML tags, decodes entities character-by-character.
    """
    plain_chars = []
    char_map = []
    hp = 0
    html_len = len(html_text)

    while hp < html_len:
        c = html_text[hp]
        if c == '<':
            match = re.match(r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>',
                             html_text[hp:], re.IGNORECASE | re.DOTALL)
            if match:
                hp += len(match.group(0))
                continue
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

    return ''.join(plain_chars), char_map

def get_link_regions(html_text):
    return [(m.start(), m.end()) for m in re.findall(r'<a\b[^>]*>.*?</a>', html_text, re.IGNORECASE | re.DOTALL)]

def inject_links(html_text, keyword_url_map, skip_pid=None):
    """
    Inject <a href> links into html_text.
    keyword_url_map: {keyword: url}
    skip_pid: don't link to this post's own URL
    Returns (new_html, list_of_injected_keywords)
    """
    plain, char_map = sync_plain(html_text)
    if not plain:
        return html_text, []

    regions = get_link_regions(html_text)
    result = html_text
    shifts = 0
    last_pos = len(result) + 1000000
    injected = []

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

            # Check inside existing tag
            in_tag = any(s <= adj_s < e for s, e in regions)
            if in_tag:
                continue

            # Context check: should not be inside href=
            ctx_s = max(0, adj_s - 20)
            snippet = result[ctx_s:adj_e + 5]
            if 'href=' in snippet[:adj_s - ctx_s + 5]:
                continue

            tag = f'<a href="{target_url}">{keyword}</a>'
            result = result[:adj_s] + tag + result[adj_e:]
            shifts += len(tag) - (adj_e - adj_s)
            last_pos = adj_s
            injected.append(keyword)
            regions.append((adj_s, adj_s + len(tag)))

    return result, injected

# ── Fetch all posts ──────────────────────────────────────────────────────────

print("Fetching posts...")
all_posts = []
page = 1
while True:
    posts = s.get(f"{WORDPRESS}/wp-json/wp/v2/posts", params={
        "post_type": "post", "per_page": 50, "status": "publish",
        "_embed": 1, "orderby": "date", "order": "asc",
        "after": "2025-01-01T00:00:00", "page": page
    }, timeout=30).json()
    if not posts:
        break
    all_posts.extend(posts)
    if len(posts) < 50:
        break
    page += 1
    time.sleep(0.3)

print(f"Total: {len(all_posts)}")

# ── Build keyword URL map ────────────────────────────────────────────────────
KEYWORDS = [
    "wegovy","ozempic","semaglutide","tirzepatide","zepbound","mounjaro",
    "orforglipron","foundayo","glp-1","glp-1 medications",
    "registered dietitian","dietitian near me","medical weight loss denver",
    "denver","greenwood village","colorado","fsa","hsa","fatty liver",
    "mash","nash","heart health","cardiovascular","type 2 diabetes",
    "plateau","stall","oral glp-1","injection","side effect","sulfur burps",
    "surgery safety","fasting","compounded","protein strategy",
    "protein on glp-1","muscle","exercise","workout",
]

kw_map = {}  # kw -> url
for p in all_posts:
    title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", "")).lower()
    url = p.get("link", "")
    pid = p.get("id")
    for kw in KEYWORDS:
        if kw in title and url:
            if kw not in kw_map:
                kw_map[kw] = {"url": url, "pid": pid}

print(f"Keyword map: {len(kw_map)} keywords")

# ── Fix all posts ─────────────────────────────────────────────────────────────
fixed = errors = clean = 0

for p in all_posts:
    pid = p["id"]
    content = p.get("content", {}).get("rendered", "")

    # Backup original before fixing
    backup_post(pid, content)

    bad = re.findall(r'href="[^"]*<a [^"]*"', content)
    nested = re.findall(r'<a\b[^>]*><a\b[^>]*>', content)

    if not bad and not nested:
        clean += 1
        continue

    title = re.sub(r'<[^>]+>', '', p.get("title", {}).get("rendered", ""))[:50]

    # Step 1: strip ALL links
    clean_html = strip_all_links(content)

    # Step 2: re-inject links (skip self-links)
    link_map = {kw: info["url"] for kw, info in kw_map.items() if info["pid"] != pid}
    final_html, injected = inject_links(clean_html, link_map, skip_pid=pid)

    # Step 3: verify
    still_bad = re.findall(r'href="[^"]*<a [^"]*"', final_html)
    still_nested = re.findall(r'<a\b[^>]*><a\b[^>]*>', final_html)

    if still_bad or still_nested:
        print(f"⚠️  [{pid}] {title} — STILL BROKEN (bad:{len(still_bad)} nested:{len(still_nested)})")
        errors += 1
        continue

    result = api_post(pid, {"content": final_html})
    if result and "id" in result:
        print(f"✓  [{pid}] {title} — {len(injected)} links")
        fixed += 1
    else:
        print(f"✗  [{pid}] save failed")
        errors += 1
    time.sleep(0.5)

print(f"\n=== DONE ===  Fixed: {fixed}  Clean: {clean}  Errors: {errors}")
