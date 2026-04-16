# Topic & Research Subagent

## Goal
Select a relevant clinical research topic AND scan the web for the latest news in one step.

## Input
- None (self-sourcing) OR a specific topic provided by the orchestrator.

## Steps
1. **History Check:** Read `projects/research-post/master-log.json` and `topic_log.json` to avoid duplicating topics covered in the last 30 days.
2. **Web Research FIRST:** Search for clinical news published in the **last 24 hours only**. Use `web_search` with `freshness: "day"`. Search for: GLP-1 medications, obesity treatments, FDA approvals, new clinical studies, major medical conference announcements.
3. **Topic Selection:**
   - If compelling 24-hour news found: use it as the topic.
   - If no topic provided AND no compelling 24-hour news: output `ABORT_WORKFLOW` and exit. Do NOT fall back to older news.
   - If topic provided by orchestrator: verify it has 24-hour relevance before proceeding.
4. **Colorado Relevance Check:** Confirm the topic has a Colorado/Denver angle before proceeding. If the news has no Colorado connection, note how it connects to CNC's patients in Greenwood Village/Denver metro.
5. **Duplicate Check:** Cross-reference `master-log.json` and `topic_log.json`. If the same or very similar topic was covered in the last 30 days, pick a different angle or `ABORT_WORKFLOW`.
6. **Output:** Save a JSON file `topic-research.json` with:
   ```json
   {
     "topic": "Selected topic title",
     "category": "Category name",
     "link": "Primary source URL",
     "summary": "2-sentence summary of the news",
     "key_points": ["Point 1", "Point 2", "Point 3"],
     "status": "PROCEED" or "ABORT_WORKFLOW"
   }
   ```

## Model
`anthropic/claude-haiku-4-5`

## Output Location
`projects/research-post/posts/YYYY-MM-DD/topic-research.json`
