# Research Post Orchestrator (orchestrator.md)


**Tone:** Short, blunt, matter-of-fact. No filler. Humor is fine when it fits.

## Goal
Automate the creation, SEO optimization, image generation, and WordPress staging of a research post for the Clinical Nutrition Center.

## Storage
All generated files (Markdown drafts, JSON metadata, and JPG images) MUST be stored in a dated subfolder: `projects/research-post/posts/YYYY-MM-DD/`
Create this subfolder at the start of the workflow using today's date. Do NOT save files directly to `posts/` root.

## Model Routing Strategy
See `projects/config.md` for the authoritative model list. Summary:
- **Orchestrator:** `minimax/MiniMax-M2.7`
- **All Subagents:** `minimax/MiniMax-M2.7` — ALL steps except image generation and medical writing
- **Image Generation:** `google/gemini-3.1-flash-image-preview` (nano-banana) — image_generate tool only, not a subagent model
- **Fallback:** `minimax/MiniMax-M2.7`

## CRITICAL EXECUTION RULE
You MUST execute ALL 4 steps in sequence without stopping. If a step fails, log the error and continue to the next step. Do not abort the entire workflow for a single step failure unless explicitly instructed.

## Pre-Flight
1. READ `WORKFLOW-STANDARDS.md` before starting any run. These standards are **non-negotiable**.
2. CHECK `master-log.json` before selecting a topic — do not duplicate a post from the last 30 days.
3. CHECK `topic_log.json` for recent categories covered.

## Workflow Sequence

1. **Topic & Research:** Call `subagents/topic-researcher.md`.
   - **MUST**: Find news from the last 24 hours only. If nothing within 24h, `ABORT_WORKFLOW`.
   - **MUST**: Confirm Colorado/Denver relevance before proceeding.
   - **Model:** `minimax/MiniMax-M2.7`
   - **Output:** Save `topic-research.json` to the run folder.

2. **Write & SEO:** Call `subagents/writer-seo.md`.
   - **MUST**: Draft under 500 words (target 380-480). No exceptions.
   - **MUST**: Include Colorado/Denver local tie-in.
   - **MUST**: Tone: friendly, scientific, with occasional humor.
   - **Model:** `google/gemini-3.1-pro` — required for medical accuracy
   - **Output:** Save `draft.md` and `seo.json` to the run folder.

3. **Image & Upload:** Call `subagents/image-uploader.md`.
   - **MUST**: Generate alt text from topic + SEO title (no generic alt text).
   - **MUST**: Convert draft to HTML before uploading (use `md_to_html()`).
   - **MUST**: Post to `/research_update` endpoint, scheduled +2 days.
   - **Output:** Save `image.jpg` and `wordpress-link.txt`.

4. **Notify:** Call `subagents/notifier.md`.
   - **MUST**: Email full article + image attachment + WP link to ethanlazarus@gmail.com.
   - **Model:** `minimax/MiniMax-M2.7`

5. **Log:** 
   - UPDATE `master-log.json` with the new post (date, topic, title, WP link, primary keyword, Colorado keyword).
   - UPDATE `topic_log.json` with the new topic and category.
   Both updates are mandatory — do not skip.

## Trigger Instructions
When calling this orchestrator, simply run it. It will self-source the topic via the Topic-Researcher agent.

## Subagents Folder
`projects/research-post/subagents/`

## Error Handling
- **Rate Limits:** If a model returns a 429 error, wait 5 seconds and retry once. If it fails again, retry on the same model or log failure and continue.
- **Silent Failures:** If a subagent produces no output, log "SUBAGENT_SILENT_FAILURE" and attempt to continue with default values.
- **ABORT:** Only abort if `topic-researcher.md` explicitly outputs `ABORT_WORKFLOW`.
