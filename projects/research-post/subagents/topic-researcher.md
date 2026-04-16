# Topic & Research Subagent

## Goal
Select a relevant clinical research topic AND scan the web for the latest news in one step.

## Input
- None (self-sourcing) OR a specific topic provided by the orchestrator.

## Steps
1. **History Check:** Read `projects/research-post/master-log.json` and `topic_log.json` to avoid duplicating topics covered in the last 30 days.
2. **WordPress Check:** Fetch the last 20 published research posts from WordPress:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=research_update,per_page=20,status=publish
   ```
   Parse the titles. If a published post covers the same/similar angle, skip it.
3. **Web Research — Freshness First (Brave):** Search for clinical news published in the **last 24 hours only** using Brave Search:
   ```
   web_search query="GLP-1 OR obesity OR FDA approval OR weight loss medication clinical study" freshness="day" count=10
   ```
   If nothing found in 24 hours, output `ABORT_WORKFLOW` and exit. No fallback to older news.
4. **Deep Research (Tavily):** For the top result(s) from the Brave freshness search, run a comprehensive Tavily search to get clinical depth:
   ```
   /home/ethan/.openclaw/workspace/skills/tavily-search/tavily_search.py "<topic> clinical research obesity GLP-1" --freshness day --depth comprehensive --max-results 5
   ```
   Use Tavily's JSON output (`--json` flag) to get structured results with source URLs and key facts.
5. **Topic Selection:**
   - If compelling 24-hour news found from Brave+Tavily: use it as the topic.
   - If no topic AND no compelling 24-hour news: `ABORT_WORKFLOW`. Never fall back.
   - If orchestrator provides a topic: verify 24-hour relevance before proceeding.
6. **Colorado Relevance Check:** Confirm the topic has a Denver/Colorado angle. If not, note the local tie-in for CNC's Greenwood Village patients in the output.
7. **Blog Potential Check:** Evaluate whether this topic has a strong patient-facing blog angle (comparison content, local SEO, how-to, FAQ-type topic). Set `has_blog_potential: true` if:
   - It's a comparison topic (e.g., "Wegovy vs Zepbound")
   - It has a local Colorado search angle
   - It's a patient FAQ-type question
   - It covers a high-volume keyword from the keyword-page-map
8. **Duplicate Check:** Cross-reference `master-log.json`, `topic_log.json`, AND WordPress titles. If duplicate, pick a different angle or `ABORT_WORKFLOW`.
9. **Output:** Save a JSON file `topic-research.json` with:
   ```json
   {
     "topic": "Selected topic title",
     "category": "Category name",
     "link": "Primary source URL",
     "summary": "2-sentence summary of the news",
     "key_points": ["Point 1", "Point 2", "Point 3"],
     "has_blog_potential": true,
     "colorado_tie_in": "How this connects to CNC patients in Greenwood Village / Denver metro",
     "status": "PROCEED" or "ABORT_WORKFLOW"
   }
   ```

## Model
`anthropic/claude-haiku-4-5`

## Output Location
`projects/research-post/posts/YYYY-MM-DD/topic-research.json`
