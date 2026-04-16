# Newsletter Notifier

## Task
Send a full report email to ethanlazarus@gmail.com when the newsletter is scheduled.

## Input
Read from the run folder:
- `schedule_result.json` — for campaign ID, scheduled time, subject
- `newsletter_v2.html` — the final HTML
- `segment-context.json` — the audience focus
- `hook.html` — subject line variants

## Email
Send to: ethanlazarus@gmail.com
Subject: "📧 Newsletter Scheduled — [SUBJECT LINE] | [DATE]"
Format: HTML email with a summary table + the full newsletter HTML attached/copied

## Summary Table (plain text in email body)
| Field | Value |
|---|---|
| Scheduled | [Date + Time MST] |
| Subject Line | [Subject] |
| Audience Focus | [active / lapsed] |
| Campaign ID | [ID] |
| Recipients | ~6,000 |

## Also Include
- The best 3 subject line variants (so Dr. Lazarus can pick if he wants to change it)
- The full newsletter HTML inline or as an attachment so he can preview it

## Sending
Use the smtp-sendgrid skill or himalaya skill. Check which is configured and use it.

## Model
minimax/MiniMax-M2.7
