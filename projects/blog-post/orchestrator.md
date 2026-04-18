# Blog Post Orchestrator (orchestrator.md)


**Tone:** Short, blunt, matter-of-fact. No filler. Humor is fine when it fits.

## Goal
Automate the creation, SEO optimization, image generation, and WordPress staging of a blog post for the Clinical Nutrition Center.

## Storage
All generated files (Markdown drafts, JSON metadata, and JPG images) MUST be stored in a dated subfolder: `projects/blog-post/posts/YYYY-MM-DD/`
Create this subfolder at the start of the workflow using today's date. Do NOT save files directly to `posts/` root.

## Model Routing Strategy
See `projects/config.md` for the authoritative model list. Summary:
- **Orchestrator:** `minimax/MiniMax-M2.7`
- **Writer:** `minimax/MiniMax-M2.7` (default — Sonnet on request only)
- **All other subagents:** `minimax/MiniMax-M2.7`
- **Image:** `google/gemini-3.1-flash-image-preview` (nano-banana) — do NOT use any other image model variant

## CRITICAL EXECUTION RULE
You MUST execute ALL 9 steps in sequence without stopping or asking for permission. Do not stop after writing or SEO — complete the image, upload, notification, and logging steps even if earlier steps return partial results. If a subagent fails, log the error and continue to the next step.

## Pre-Flight
1. READ `WORKFLOW-STANDARDS.md` before starting any run. These standards are **non-negotiable**.
2. CHECK `master-log.json` — do not duplicate a post from the last 60 days.
3. CHECK the `posts/` folder for recently covered topics.
4. FETCH the last 20 published blog posts from WordPress:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=post,per_page=20,status=publish
   ```
   Parse the titles. If the provided topic matches or closely overlaps with a recently published post, flag it. If the same topic was published in the last 60 days, ask the orchestrator to pick a different topic before proceeding.

## Workflow Sequence
1. **Create Run Folder:** Create `projects/blog-post/posts/YYYY-MM-DD/` using today's date before any other step.
2. **Topic Generator (conditional):** If no topic was provided, call `subagents/topic-generator.md` to generate 3 ranked topic recommendations from the keyword map. Auto-select rank 1. If topic WAS provided, skip this step and use the provided topic.
3. **Writer:** Call `subagents/writer.md` with the topic and any provided link to draft the post. Save to run folder. **MUST: Under 500 words (target: 380-480).** **Model:** `minimax/MiniMax-M2.7`
4. **SEO:** Call `subagents/seo-optimizer.md` with the draft to generate local SEO metadata. **MUST: Include Colorado/Denver keywords in title, description, and focus keywords.** Save to run folder. **Model:** `minimax/MiniMax-M2.7`
5. **Image:** Call `subagents/image-generator.md` with the topic and SEO title to generate the featured image using `google/gemini-3.1-flash-image-preview` (alias: `nano-banana`). Save image to run folder. **Model:** `google/gemini-3.1-flash-image-preview` — do NOT use `gemini-3.1-pro-image-preview-v2` or any other image model variant.
6. **Editor:** Call `subagents/editor.md` to assemble the post, ensuring an 8th-grade reading level and "pretty" formatting. Tone: friendly, scientific, with occasional humor. Save to run folder. **Model:** `minimax/MiniMax-M2.7`
7. **FAQ Schema:** Call `subagents/faq-schema.md` to generate FAQ schema for the post. Inject the FAQ into the HTML before upload. Save `faq-schema.json` to run folder. **Model:** `minimax/MiniMax-M2.7`
8. **Media Upload:** Call `subagents/wp-media-uploader.md` to upload the generated image to WordPress. **MUST: Pass descriptive alt_text generated from topic and SEO title.** **Model:** `minimax/MiniMax-M2.7`
9. **Article Upload:** Call `subagents/wp-article-uploader.md` to create a draft post on WordPress, scheduled for +7 days, with the featured image, SEO metadata, and FAQ schema. **Model:** `minimax/MiniMax-M2.7`
10. **Notify:** Call `subagents/notifier.md` to email the final copy and WordPress link to Dr. Lazarus for review. **Model:** `minimax/MiniMax-M2.7`
11. **Log:** UPDATE `master-log.json` with the new post (date, topic, title, WP link, primary keyword, Colorado keyword). Flag `has_blog_potential: false` (blog posts don't feed themselves). This step is mandatory — do not skip.

## Trigger Instructions
When calling this orchestrator:
- If `topic` is provided: skip Step 0, go directly to Step 2 (Writer).
- If no `topic` provided: run Step 0 (Topic Generator) first to get recommendations.
- `link` (optional): A URL to summarize or use as a source.

## Subagents Folder
`projects/blog-post/subagents/`
