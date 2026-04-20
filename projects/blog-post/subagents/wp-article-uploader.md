# WordPress Article Uploader Agent (wp-article-uploader.md)

## Task
Upload the finalized blog post or research post to WordPress with proper internal cross-links.

## Pre-Upload: Research Internal Cross-Links

**BEFORE converting markdown to HTML**, do this:

1. **Fetch last 25 published blog posts** (for blog posts) or **last 15 research posts** (for research posts):
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=post,per_page=25,status=publish --query _embed=1
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=research_update,per_page=15,status=publish --query _embed=1
   ```
2. **Parse all titles and URLs** into a mapping table. Group by topic category:
   - GLP-1 / medication posts → link to each other when the current post mentions those topics
   - Nutrition posts → link to other nutrition posts
   - Colorado / local posts → link to other Colorado posts

3. **Find cross-link opportunities in the draft:**
   - Scan draft content for mentions of medications (Wegovy, Zepbound, semaglutide, tirzepatide, GLP-1)
   - Scan for mentions of other procedures or conditions that have dedicated posts
   - Scan for keywords that match existing post titles

4. **Build cross-links to inject:**
   For every relevant mention in the draft, wrap the natural phrase in an `<a href="[existing-post-url]">` pointing to the related post. Prioritize:
   - Same-type links (GLP-1 post → GLP-1 post)
   - Bidirectional when appropriate (if post A mentions post B, post B should mention post A)
   - Colorado posts linking to other Colorado posts

5. **Rules for cross-links:**
   - Use meaningful anchor text (not "click here" or "read more" — use the actual post title or keyword)
   - Don't over-link — 3 to 6 relevant cross-links per post is ideal
   - Link to the most relevant existing post, not just any post on the site
   - For research posts: link to other research posts when sharing clinical findings; link to blog posts for patient-facing explanations

## Instructions

1. Use the **wordpress** skill (`node skills/wordpress/scripts/wp-cli.js`).
2. **CRITICAL for Blog:** Post to `/wp-json/wp/v2/posts` — NOT `research_update`.
   **CRITICAL for Research:** Post to `/wp-json/wp/v2/research_update` — NOT `posts`.
3. **CRITICAL: Always use `https://www.clinicalnutritioncenter.com` (with `www`).**
4. **Read FAQ Schema:** Load `faq-schema.json` from the run folder if it exists.
5. **Inject cross-links into draft markdown** before converting to HTML (use the cross-link research above).
6. **Convert Markdown to HTML:**
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
7. **Build final HTML with FAQ section:**
   - JSON-LD `<script>` in `<head>` if FAQ schema exists
   - Visible FAQ Q&A at end of body
8. **Create the post:**
   - `title`: From SEO data meta_title
   - `content`: Full HTML with cross-links + FAQ
   - `status`: **draft**
   - `date`: **7 days from today** (blog) or **2 days from today** (research)
   - `featured_media`: Use the Media ID provided
9. **Add AIOSEO metadata:**
   - `_aioseo_title`: ≤60 chars
   - `_aioseo_description`: ≤155 chars
   - `_aioseo_keywords`: comma-separated
10. Record **Post ID**, **Post URL**, **Publish Date**.

## Cross-Link Quick Reference Table
Build this during pre-upload step and use it to inject links:

| Keyword/Phrase in Draft | Link To |
|---|---|
| "Wegovy" | /wegovy-post-url |
| "Zepbound" | /zepbound-post-url |
| "semaglutide" | /semaglutide-post-url |
| "tirzepatide" | /tirzepatide-post-url |
| "GLP-1" | /glp-1-explainer-post |
| "registered dietitian" | /rd-near-me-post |
| etc. |

## Input
- Final Content: `posts/YYYY-MM-DD/draft.md`
- SEO Data: `posts/YYYY-MM-DD/seo.json`
- Media ID: from wp-media-uploader
- FAQ Schema: `posts/YYYY-MM-DD/faq-schema.json` (if exists)

## Output
- Post ID: {{post_id}}
- Post URL: {{post_url}}