# Upload & Schedule Newsletter

## Task
Take the final HTML newsletter and schedule it in Constant Contact.

## Logic Requirements
1. **Target Date:** Calculate the date and time for the immediate upcoming Wednesday at 10:30 AM MST (convert this to UTC ISO 8601 for the API). Since you are running on Monday, this will be exactly 48 hours later.
   - **CRITICAL:** Do not use a fixed day of the month. Always calculate "next Wednesday" from the current run date (which is Monday).
2. **List Lookup:** Use the `constant-contact` skill (`list-groups`) to find the ID for the "General Interest" list.
3. **Save File:** Save the HTML to `/home/ethan/.openclaw/workspace/projects/constant-contact/newsletter_draft.html`.
4. **Schedule:** Use the `constant-contact` skill (`create-schedule`) to draft and schedule the email.

## Example Command
```bash
python3 /home/ethan/.openclaw/workspace/skills/constant-contact/cc_manager.py create-schedule \
  --name "CNC Newsletter - Month Year" \
  --subject "Latest Updates from Clinical Nutrition Center" \
  --list-ids "<retrieved_list_id>" \
  --date "<calculated_iso_date>" \
  --html-file "/home/ethan/.openclaw/workspace/projects/constant-contact/newsletter_draft.html" \
  --from-email "ethanlazarus@gmail.com" \
  --from-name "Dr. Ethan Lazarus"
```

## Output
- Scheduled Date: {{scheduled_date}}
