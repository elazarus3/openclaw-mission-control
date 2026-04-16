# WordPress Article Uploader Agent (wp-article-uploader.md)

## Task
Upload the finalized blog post and metadata to the WordPress site.

## Instructions
1. Use the **wordpress** skill (`node skills/wordpress/scripts/wp-cli.js`).
2. **CRITICAL: Post to `/wp-json/wp/v2/posts` — this is a blog post, NOT `research_update`.**
3. **CRITICAL: Always use `https://www.clinicalnutritioncenter.com` (with `www`) — non-www redirects break POST requests.**
4. **Read FAQ Schema:** Load `faq-schema.json` from the run folder. Extract the `json_ld` field and the `faqs` array. If the file doesn't exist, skip FAQ injection.
5. **Convert Markdown to HTML** before uploading:
   ```python
   import re
   def md_to_html(md):
       md = re.sub(r'^# .+\n?', '', md, count=1)
       md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md, flags=re.MULTILINE)
       md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md, flags=re.MULTILINE)
       md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
       md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
       md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md)
       md = re.sub(r'^[-*] (.+)$', r'<li>\1</li>', md, flags=re.MULTILINE)
       md = re.sub(r'(<li>.*?</li>\n?)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', md, flags=re.DOTALL)
       paras = re.split(r'\n{2,}', md.strip())
       out = []
       for p in paras:
           p = p.strip()
           if p and not p.startswith('<'):
               p = '<p>' + p.replace('\n', ' ') + '</p>'
           out.append(p)
       return '\n'.join(out)
   ```
6. **Build final HTML with FAQ section:**
   - Convert draft to HTML using `md_to_html()`
   - If `faq-schema.json` exists: wrap in full HTML document:
     ```html
     <html>
     <head>
       <title>TITLE</title>
       JSON_LD_SCRIPT_HERE
     </head>
     <body>
       ARTICLE_HTML_CONTENT
       <hr>
       <h2>Frequently Asked Questions</h2>
       FAQ_QA_HTML
     </body>
     </html>
     ```
   - JSON-LD `<script>` goes in `<head>`
   - Add visible FAQ Q&A at end of body
   - If no FAQ schema: upload converted HTML content as-is (no document wrapper)
7. **Create the post:**
   - `title`: From SEO data meta_title.
   - `content`: Full HTML document (with FAQ section + JSON-LD if available).
   - `status`: **draft**.
   - `date`: Set to **7 days from today**.
   - `featured_media`: Use the Media ID provided.
8. **Add AIOSEO metadata** via the `meta` field:
   - `_aioseo_title`: SEO Title (≤60 chars).
   - `_aioseo_description`: Meta Description (≤155 chars).
   - `_aioseo_keywords`: Primary and focus keywords (comma-separated).
9. Record the final **Post ID**, **Post URL**, and **Publish Date**.

## Input
- Final Content: `posts/YYYY-MM-DD/draft.md` (read from run folder)
- SEO Data: `posts/YYYY-MM-DD/seo.json` (read from run folder)
- Media ID: returned by wp-media-uploader
- FAQ Schema: `posts/YYYY-MM-DD/faq-schema.json` (read if exists)

## Output
- Post ID: {{post_id}}
- Post URL: {{post_url}}
