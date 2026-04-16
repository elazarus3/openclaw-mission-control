# Notify User

## Task
Email the finalized HTML newsletter draft to Dr. Lazarus and the proofreading team so they can review it, and ensure the scheduled send date is clearly stated in the subject line.

## Instructions
1. Read the final HTML newsletter from `/home/ethan/.openclaw/workspace/projects/constant-contact/newsletter_draft.html`.
2. Read the `scheduled_date` provided in your input.
3. Use the `smtp-sendgrid` skill to send an email to **TWO** recipients for proofreading:
   - `ethanlazarus@gmail.com`
   - `alazarus3@gmail.com`
   (Send as a comma-separated list: `ethanlazarus@gmail.com,alazarus3@gmail.com`)
4. The subject line must be: `Newsletter Draft Scheduled for [Scheduled Date]` (replace the bracketed text with the actual human-readable date).
5. The body of the email must be the raw HTML content of the newsletter (sent as an HTML email).

## Input
- Scheduled Date: {{scheduled_date}}