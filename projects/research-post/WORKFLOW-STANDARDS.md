# Research Post Workflow — Standards

## Non-Negotiables

### 1. Timeliness — 24-Hour News Only
- The topic MUST be based on news published or breaking in the **last 24 hours**.
- If no compelling news has broken in the last 24 hours, output `ABORT_WORKFLOW` and exit.
- Do NOT fall back to older topics. Better no post than stale content.

### 2. Word Count — Under 500 Words
- Draft must be under 500 words (target: 380-480).
- This is firm. If draft exceeds 500 words, trim aggressively. Cut entire sections if needed.

### 3. Colorado Relevance
- Every post must include at least one of these local connections:
  - Reference to Colorado/Denver/Mile High geography
  - Colorado-based clinical context (e.g., altitude effects, state obesity rates)
  - Relevance to CNC's patients in Greenwood Village / Denver metro
- If the breaking news has no Colorado angle, add a local tie-in in the clinical takeaway.

### 4. SEO Metadata (Required Every Time)
- `meta_title`: ≤60 characters, include primary keyword + "Colorado" or "Denver"
- `meta_description`: ≤155 characters, compelling, includes local marker
- `focus_keywords`: 3-5 terms, MUST include at least one Colorado keyword
- `slug`: URL-friendly, includes Denver or Colorado if possible
- `alt_text` (for featured image): Plain-language description of image content, tied to topic

### 5. Tone
- Friendly, scientifically grounded, knowledgeable.
- A touch of humor is welcome — Dr. Lazarus's voice is precise but approachable.
- NO AI-speak. No "it's important to note that." No "in conclusion."
- Write like a smart doctor talking to a patient, not a textbook.

### 6. HTML Output
- All article content uploaded to WordPress must be HTML, not Markdown.
- Use the `md_to_html()` conversion function in the upload step.
- HTML must include: `<h2>` headers, `<p>` paragraphs, `<ul>/<li>` lists, `<strong>` bold terms.

### 7. Featured Image Alt Text
- Alt text is mandatory. Generate from the topic and SEO title.
- Must be descriptive, plain-language, specific to what the image depicts.
- Example: "A capsule medication beside a glass of water, representing an oral GLP-1 weight-loss option" — NOT "pill" or "medication icon."

### 8. Master Log — No Duplicates
- **Every completed post MUST be logged** in `master-log.json` before the workflow ends.
- Log entry must include: date, topic, title, WordPress link, primary keyword, Colorado keyword used.
- Before selecting a new topic, the topic-researcher MUST check `master-log.json` and `topic_log.json` to avoid duplication.
- If a similar topic has been covered in the last 30 days, pick a different angle or `ABORT_WORKFLOW`.

### 9. Email Notification
- Every completed post must be emailed to `ethanlazarus@gmail.com`.
- Email must include: full article text, featured image attachment, WordPress edit link, SEO metadata summary.
- Subject line: `[Research Post] Ready for Review: {title} — {date}`
