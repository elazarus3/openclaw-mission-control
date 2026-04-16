# Constant Contact Uploader v2

## Task
Upload the newsletter HTML to Constant Contact and schedule the campaign.

## CRITICAL: From Email
- **Always use:** `info@clinicalnutritioncenter.com` — this is the verified sender
- Do NOT use `noreply@clinicalnutritioncenter.com` or personal Gmail addresses
- If `info@clinicalnutritioncenter.com` fails, stop and report the error

## Input
Read `newsletter_v2.html` from the run folder.
Read `hook.html` from the run folder for subject lines.

## Instructions
1. Use the `constant-contact` skill (read its SKILL.md first).
2. Refresh the access token using the refresh_token from `.env`. **Must include `User-Agent: Mozilla/5.0` header** or Cloudflare will block the request.
3. Find the list ID for "General Interest" list: `c2114ee0-fa84-11ea-82b3-d4ae527536d1`
4. Create a new campaign via `POST /emails`:
   - **Subject line**: From `hook.html` subject variants (pick the best)
   - **Preview text**: From `hook.html`
   - **From name**: "Dr. Ethan Lazarus | Clinical Nutrition Center"
   - **From email**: `info@clinicalnutritioncenter.com`
   - **Reply-to**: `info@clinicalnutritioncenter.com`
   - **HTML content**: From `newsletter_v2.html`
   - **List**: `c2114ee0-fa84-11ea-82b3-d4ae527536d1`
5. Schedule: Next Wednesday at 10:30 AM MDT
   - Format: `2026-04-23T16:30:00Z` (ISO 8601 UTC)

## Output
Write `schedule_result.json` to the run folder:
```json
{
  "campaign_id": "...",
  "scheduled_time": "2026-04-23T10:30:00-06:00",
  "subject_line": "...",
  "list": "General Interest"
}
```

## Model
minimax/MiniMax-M2.7
