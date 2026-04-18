# Master Project Config

This file is the single source of truth for all projects in the `projects/` folder.
All orchestrators and subagents MUST reference this file for models, credentials, and settings.

---

## Model Routing

| Role | Model | When to Use |
|---|---|---|
| **Orchestrator** | `minimax/MiniMax-M2.7` | Default — all orchestrators |
| **Writer subagent (all content)** | `minimax/MiniMax-M2.7` | Default — all content writing |
| **Image Generation** | `google/gemini-3.1-flash-image-preview` (alias: `nano-banana`) | Always |
| **Sonnet (on request only)** | `anthropic/claude-sonnet-4-6` | Only when Dr. Lazarus specifically requests it |

**Rules:**
- All writing, SEO, uploads, scheduling: `minimax/MiniMax-M2.7` by default.
- Sonnet: only when Dr. Lazarus explicitly asks for it.
- If a model returns a 429, wait 5s, retry once, then retry on the same model or log failure.
- Never use local Ollama models.

---

## WordPress Credentials

**Main Site:** `https://www.clinicalnutritioncenter.com` (ALWAYS use `www` — non-www redirects break POST requests)
- REST API Base: `https://www.clinicalnutritioncenter.com/wp-json/wp/v2`
- Upload Endpoint: `/media` (POST multipart/form-data)
- **Research Post Endpoint: `/research_update` (POST JSON) — NOT `/posts`**
- Blog Post Endpoint: `/posts` (POST JSON)
- Auth: Application password — see `skills/wordpress/` skill for credential lookup

**Store Site:** `https://store.clinicalnutritioncenter.com`
- WooCommerce REST: `https://store.clinicalnutritioncenter.com/wp-json/wc/v3`
- Consumer Key: `[see .env — key: WOOCOMMERCE_CONSUMER_KEY]`
- Consumer Secret: `[see .env — key: WOOCOMMERCE_CONSUMER_SECRET]`

---

## Email (SendGrid SMTP)

```
SMTP_SERVER   = smtp.sendgrid.net
SMTP_PORT     = 465
SMTP_USERNAME = apikey
SMTP_PASSWORD = [see .env — key: SENDGRID_API_KEY]
FROM          = donotreply@clinicalnutritioncenter.com
TO            = ethanlazarus@gmail.com
```

**Rules:**
- Always use SendGrid SMTP. Do NOT use AgentMail (currently returns 403 Forbidden).
- For emails with image attachments, use Python's `email.mime` stack directly (see blog-post/subagents/notifier.md for template).
- Always send full article text + image attachment in notification emails (not just a summary/link).

---

## Notification Email Standards

Every project's notifier subagent MUST:
1. Send to `ethanlazarus@gmail.com` via SendGrid SMTP.
2. Include **full article/content** in email body (HTML formatted).
3. Attach the **featured image** as a MIME attachment.
4. Include the **WordPress edit link** prominently.
5. Subject format: `[Project Name] Ready for Review: {Title} — {Date}`

---

## WordPress Upload Standards

Every wp-article-uploader MUST:
0. **Convert Markdown → HTML before posting.** The WordPress REST API does NOT auto-convert markdown. Raw `#`/`##`/`**` will render as literal characters. Use Python `re` to convert headers, bold, italic, lists, and paragraphs to HTML tags before setting the `content` field.
1. Upload image to WordPress media first → get `media_id`.
2. Create post with `status: draft`, scheduled `+7 days` (blog) or `+2 days` (research).
3. Set `featured_media` to the returned `media_id`.
4. Inject AIOSEO meta fields: `_aioseo_title`, `_aioseo_description`, `_aioseo_keywords`.
5. Save `wordpress-link.txt` to the run folder with the edit URL.
6. Log success/failure explicitly.

---

## File Storage Standards

- All run artifacts go in: `projects/{project-name}/posts/YYYY-MM-DD/`
- Required files per run:
  - `draft.md` — raw article
  - `seo.json` — SEO metadata
  - `image.jpg` — featured image
  - `wordpress-link.txt` — WP edit URL
  - `topic-research.json` (research-post only)

---

## Environment Setup (CRITICAL for cron)

All Python trigger scripts MUST use this exact environment block before calling OpenClaw.
Two things are required: canonical PATH and explicit API key loading.

```python
# Build clean cron-safe environment
env = os.environ.copy()
# Canonical PATH: includes opt/node/bin for openclaw, linuxbrew/bin for node
env["PATH"] = f"/home/linuxbrew/.linuxbrew/opt/node/bin:/home/linuxbrew/.linuxbrew/bin:/usr/local/bin:/usr/bin:{env.get('PATH', '')}"
# Explicitly load API keys (api_keys.env may not be in cron environment)
api_keys_file = "/home/ethan/.openclaw/api_keys.env"
if os.path.exists(api_keys_file):
    with open(api_keys_file) as kf:
        for line in kf:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"')
result = subprocess.run(cmd, capture_output=True, text=True, env=env)
```

OpenClaw binary: `/home/linuxbrew/.linuxbrew/bin/openclaw`
Node binary: `/home/linuxbrew/.linuxbrew/opt/node/bin/node`
API keys file: `/home/ethan/.openclaw/api_keys.env`

### Systemd Service Drop-in
The gateway service (`openclaw-gateway.service`) loads `api_keys.env` via a drop-in:
`~/.config/systemd/user/openclaw-gateway.service.d/override.conf`
This ensures agents/subagents spawned by the gateway inherit all API keys.
The trigger scripts also load the file explicitly as a belt-and-suspenders fallback for direct cron invocations.

---

## Crontab (Reference)

```
# Morning Report — Daily 6AM UTC (midnight MST)
0 6 * * *   /bin/bash ~/workspace/projects/morning-report/daily_morning_report.sh >> .../cron.log 2>&1

# Research Post — Weekdays 8AM UTC
0 8 * * 1-5 /usr/bin/python3 ~/workspace/projects/research-post/trigger_daily_research.py >> .../cron.log 2>&1

# Blog Post — Every Monday 9AM UTC
0 9 * * 1   /usr/bin/python3 ~/workspace/projects/blog-post/trigger_blog.sh >> .../cron.log 2>&1

# Store Newsletter — 1st Monday of month, 7AM UTC
0 7 * * 1   /bin/bash ~/workspace/projects/constant-contact/trigger_if_first_monday.sh >> .../cron.log 2>&1

# Store Newsletter (WooCommerce) — 2nd Monday of month, 7AM UTC
0 7 * * 1   /bin/bash ~/workspace/projects/store-newsletter/trigger_if_second_monday.sh >> .../cron.log 2>&1

# GMC SEO — Daily 1PM UTC
0 13 * * *  cd ~/workspace/projects/woo-commerce-seo && /usr/bin/python3 trigger_gmc_orchestrator.py >> .../gmc-cron.log 2>&1
```

---

## Payments Report — Known Senders

These are verified payment sender addresses for Dr. Lazarus's income tracking:

| Company | Sender Address | Category |
|---|---|---|
| Novo Nordisk (via IQVIA) | novonordiskgeneral@iqvia.com | Pharma-Novo Nordisk |
| Eli Lilly (via FIS) | fisip.payments@e.fisglobal.com | Pharma-Lilly |
| Boehringer Ingelheim (via PropelHealth) | bimer_noreply@propelhealth.com | Pharma-BI |
| Guidepoint (consulting) | *@guidepoint.com | Consulting-Guidepoint |
| Atheneum (consulting) | *@atheneum-partners.com | Consulting-Atheneum |

Google Sheet ID: `1P2CT51ovhvpQRg0-A2tpSLg_JsT076l36QDQGMi3eVY`
Sheet URL: https://docs.google.com/spreadsheets/d/1P2CT51ovhvpQRg0-A2tpSLg_JsT076l36QDQGMi3eVY

---


## Google Search Console (GSC)

| Site | URL | Access |
|---|---|---|
| Store | https://store.clinicalnutritioncenter.com/ | OAuth (token in `store-orchestrator/memory/gsc_tokens.json`) |
| Clinic | https://www.clinicalnutritioncenter.com/ | Google API Key |

- **Google API Key:** `[see .env — key: GOOGLE_API_KEY]`
- **OAuth Client ID:** `[see .env — key: GOOGLE_OAUTH_CLIENT_ID]`
- **OAuth Client Secret:** `[see .env — key: GOOGLE_OAUTH_CLIENT_SECRET]`
- **Shared config:** `~/.openclaw/workspace/shared/gsc-config.md`

---

## Anti-Hallucination Rules

- NEVER fabricate medication prices, dosages, or package insert data.
- NEVER discuss compounded medications in patient-facing content.
- NEVER invent citations — only cite sources found via web_search.
- Articles must be written by a human physician voice, not an AI voice.
