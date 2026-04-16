# Summarize Articles

## Task
Take the provided list of articles from the previous month and write a brief, engaging summary for each.

## Requirements
- Format each item for a newsletter.
- Include the featured picture (as an HTML `<img>` tag or placeholder).
- Include a clear call-to-action link to read the full article on the website.
- Tone: Professional, clinical, yet engaging.

## CRITICAL: Avoid Duplicate Articles
1. **Check Previous Newsletter:** Before generating summaries, you MUST read the last saved newsletter draft at `/home/ethan/.openclaw/workspace/projects/constant-contact/newsletter_draft.html` (or the most recent archived copy if it exists).
2. **Extract Titles:** Parse the previous newsletter to extract the titles of all articles that were already included.
3. **Filter:** If any of the current month's articles match a title (or very similar title) from the previous newsletter, **SKIP** that article. Do not include it in the new newsletter.
4. **Fallback:** If the previous newsletter file does not exist or is empty, proceed with all articles.

## Output
Return a list of summaries for the **unique** articles only.