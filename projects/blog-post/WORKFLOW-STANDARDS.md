# Blog Post Workflow — Standards

## Non-Negotiables

### 1. Timeliness — Within the Last 7 Days
- The topic must be based on news, research, or clinical developments from the **last 7 days**.
- If nothing compelling has emerged in the last 7 days, `ABORT_WORKFLOW` and exit.
- Do NOT fall back to evergreen topics. Better no post than a stale one.

### 2. Word Count — Under 500 Words
- Draft must be under 500 words (target: 380-480).
- This is firm. Trim ruthlessly. Short = readable.

### 3. Colorado Relevance — Every Post
- Every post must have a Colorado/Denver local connection woven in naturally:
  - Greenwood Village, Denver metro, Colorado, Mile High City, Front Range, etc.
- Suitable angles: altitude effects, Colorado obesity rates, regional diet/activity patterns, relevance to CNC's patients.
- SEO title and meta description must include a local marker (e.g., "Denver," "Colorado," "Greenwood Village").

### 4. SEO Metadata (Required Every Time)
- `meta_title`: ≤60 characters, primary keyword + local marker
- `meta_description`: ≤155 characters, compelling, local marker included
- `focus_keywords`: 3-5 terms, MUST include Colorado/Denver keyword
- `slug`: URL-friendly, includes Denver or Colorado if possible
- `alt_text` (for featured image): Descriptive, plain-language, topic-specific

### 5. Tone
- Friendly, scientific, knowledgeable — with occasional humor.
- Dr. Lazarus's voice: clinical precision with a dry wit. Never boring. Never condescending.
- Person-first language always: "person with obesity" NOT "obese person."
- 8th-grade reading level. Short sentences. Short paragraphs.

### 6. HTML Output
- All WordPress content must be HTML, not Markdown.
- Use the `md_to_html()` conversion function before uploading.
- Structure: `<h2>` headers, `<p>` paragraphs, `<ul>/<li>` lists, `<strong>` key terms.

### 7. Featured Image Alt Text
- Alt text is mandatory. Generate from topic and SEO title.
- Must be descriptive and specific to the image content.
- Example: "A scenic mountain landscape at sunrise representing Denver's natural weight-loss environment" — NOT "mountains" or "landscape photo."

### 8. Master Log — No Duplicates
- **Every completed post MUST be logged** in `master-log.json` before the workflow ends.
- Log entry: date, topic, title, WordPress link, primary keyword, local keyword used.
- Before selecting a topic, the writer must check `master-log.json` and the `posts/` folder to avoid duplication.
- If the same or very similar topic was covered in the last 60 days, pick a different angle.

### 9. Email Notification
- Every completed post must be emailed to `ethanlazarus@gmail.com`.
- Email includes: full article text, featured image attachment, WordPress edit link, SEO metadata.
- Subject: `[Blog Post] Ready for Review: {title} — {date}`
