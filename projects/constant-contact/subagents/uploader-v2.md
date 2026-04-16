# Constant Contact Uploader v2

## Task
Upload the newsletter HTML to Constant Contact and schedule the campaign.

## Input
Read `newsletter_v2.html` from the run folder.
Read `hook.html` from the run folder for subject lines.

## Instructions
1. Use the `constant-contact` skill (read its SKILL.md first).
2. Find the list ID for "General Interest" list.
3. Create a new campaign:
   - **Subject line**: Use the best subject line from `hook.html` (first variant)
   - **Preview text**: Use the preview text from `hook.html`
   - **From name**: "Dr. Ethan Lazarus | Clinical Nutrition Center"
   - **From email**: Use whatever is configured in the Constant Contact skill
   - **HTML content**: From `newsletter_v2.html`
   - **List**: "General Interest"
   - **Schedule**: Next Wednesday at 10:30 AM MST
     - Calculate: if today is Wednesday before 10:30 AM, use today. Otherwise use next Wednesday.
     - Format: ISO 8601 datetime in local timezone (America/Denver)

## Output
Write `schedule_result.json` to the run folder:
```json
{
  "campaign_id": "...",
  "scheduled_time": "2026-04-23T10:30:00-06:00",
  "subject_line": "...",
  "recipients": 6000
}
```

## Model
minimax/MiniMax-M2.7
