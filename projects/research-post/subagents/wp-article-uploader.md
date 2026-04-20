# WordPress Article Uploader Agent (wp-article-uploader.md)

## Task
Upload the finalized research post to WordPress with proper internal cross-links.

## Pre-Upload: Research Internal Cross-Links

**BEFORE uploading**, do this:

1. **Fetch last 15 published research posts** and **last 15 blog posts**:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=research_update,per_page=15,status=publish --query _embed=1
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=post,per_page=15,status=publish --query _embed=1
   ```
2. **Parse all titles and URLs** into a mapping table. Group by topic:
   - GLP-1 studies → link to other GLP-1 content
   - Medication comparisons → link to blog posts explaining patient implications
   - Obesity research → link to other obesity research

3. **Find cross-link opportunities in the research content:**
   - Scan content for medication names (Wegovy, Zepbound, semaglutide, tirzepatide, orforglipron)
   - Scan for study citations, FDA announcements, clinical trial mentions
   - Look for phrases like "our patients," "at our Greenwood Village clinic," "Colorado patients"

4. **Build cross-links to inject:**
   For every relevant mention, link to the most relevant existing post. For research posts:
   - Link research-to-research (clinical finding → related clinical finding)
   - Link research-to-blog when the finding has patient-facing implications (e.g., new medication → blog post about that medication for patients)
   - Use meaningful anchor text (post title or medication name, not "read more")

5. **Rules for cross-links:**
   - 3 to 6 relevant cross-links per research post
   - Link to most relevant post, not just any post
   - When citing a study that CNC also has a blog post about — link both directions

## Instructions

1. Use the **wordpress** skill (`node skills/wordpress/scripts/wp-cli.js`).
2. **CRITICAL: Post to `/wp-json/wp/v2/research_update` — NOT `/posts`.**
3. **CRITICAL: Always use `https://www.clinicalnutritioncenter.com` (with `www`).**
4. **Inject cross-links into research content** before creating the payload.
5. **Add AIOSEO metadata** via the `meta` field:
   - `_aioseo_title`: SEO Title (≤60 chars)
   - `_aioseo_description`: Meta Description (≤155 chars)
   - `_aioseo_keywords`: comma-separated keywords
6. **Save payload** to `projects/research-post/posts/payload.json`.
7. **Create post:**
   - `title`: From SEO data
   - `content`: Research HTML with cross-links
   - `status`: **future**
   - `date`: **2 days from today** (publish after research post is reviewed)
   - `featured_media`: Media ID from wp-media-uploader
8. Upload via:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js request POST /research_update @/home/ethan/.openclaw/workspace/projects/research-post/posts/payload.json
   ```
9. Record **Post ID**, **Post URL**, **Publish Date**.

## Cross-Link Quick Reference
Build this during pre-upload:

| Keyword/Phrase in Research | Link To |
|---|---|
| "Wegovy" / "semaglutide" | Research or blog post about Wegovy |
| "Zepbound" / "tirzepatide" | Research or blog post about Zepbound |
| "GLP-1 medications" | General GLP-1 explainer post |
| "Clinical Nutrition Center" | Main clinic page or blog post |
| "Greenwood Village" | Blog post about the clinic |
| "orforglipron" | Blog post about oral GLP-1 options |

## Input
- Final Content: {{final_content}}
- SEO Data: {{seo_data}}
- Media ID: {{media_id}}

## Output
- Post ID: {{post_id}}
- Post URL: {{post_url}}