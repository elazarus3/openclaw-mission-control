# SEO Optimizer Subagent

## Task
Generate local SEO metadata for the blog post draft. Read the draft from the run folder.

## Colorado Local SEO — Non-Negotiable
- **Primary keyword** must be something CNC's patients in Colorado would search (e.g., "Denver weight loss", "GLP-1 doctor Colorado", "medical weight loss Greenwood Village")
- **Meta title**: ≤60 characters, include primary keyword + local marker ("Denver", "Colorado", or "Greenwood Village")
- **Meta description**: ≤155 characters, compelling, must include local marker
- **Focus keywords**: 3-5 terms, MUST include at least one Colorado/Denver keyword
- **Slug**: URL-friendly, include Denver or Colorado if possible

## Input
Read the draft from the run folder: `projects/blog-post/posts/YYYY-MM-DD/draft.md`

## Output
Save SEO metadata to: `projects/blog-post/posts/YYYY-MM-DD/seo.json`
