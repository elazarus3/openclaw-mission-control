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
- **Writer:** `anthropic/claude-sonnet-4-6` — required for clinical accuracy and content quality
- **All other subagents:** `minimax/MiniMax-M2.7`
- **Image:** `google/gemini-3.1-flash-image-preview` (nano-banana) — image_generate tool only

## CRITICAL EXECUTION RULE
You MUST execute ALL 6 steps in sequence without stopping. If a step fails, log the error and continue to the next step. Do not abort the entire workflow for a single step failure unless explicitly instructed.

## Pre-Flight
1. READ `WORKFLOW-STANDARDS.md` before starting any run. These standards are **non-negotiable**.
2. CHECK `master-log.json` before selecting a topic — do not duplicate a post from the last 30 days.
3. CHECK `topic_log.json` for recent categories covered.
4. VERIFY Tavily is working: `python3 /home/ethan/.openclaw/workspace/skills/tavily-search/tavily_search.py "test" --max-results 1`. If it returns an error, use Brave Search as fallback for deep research.

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
   - **Model:** `anthropic/claude-sonnet-4-6`
   - **Output:** Save `draft.md` and `seo.json` to the run folder.

3. **FAQ Schema:** Call `subagents/faq-schema.md` to generate FAQ schema from the draft.
   - **MUST**: Generate 3-5 FAQs based on common patient questions arising from the topic.
   - **MUST**: Include FAQ schema JSON-LD markup.
   - Save `faq-schema.json` to the run folder.
   - **Model:** `minimax/MiniMax-M2.7`

4. **Image & Upload:** Call `subagents/image-uploader.md`.
   - **MUST**: Generate alt text from topic + SEO title (no generic alt text).
   - **MUST**: Convert draft to HTML. INJECT the FAQ schema JSON-LD into the HTML before uploading.
   - **MUST**: Post to `/research_update` endpoint, scheduled +2 days.
   - **Output:** Save `image.jpg` and `wordpress-link.txt`.

5. **Notify:** Call `subagents/notifier.md`.
   - **MUST**: Email full article + image attachment + WP link to ethanlazarus@gmail.com.
   - **Model:** `minimax/MiniMax-M2.7`

6. **Log:** 
   - UPDATE `master-log.json` with the new post (date, topic, title, WP link, primary keyword, Colorado keyword, has_blog_potential).
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
