# Topic & Research Subagent

## Goal
Do actual deep research on the latest clinical findings in obesity medicine — then pick the single most compelling topic. Not just "something from 24 hours ago" — genuinely the most interesting, clinically relevant topic available right now.

## Pre-Flight: Check History BEFORE Picking a Topic

1. **master-log.json** — research posts from last 60 days
2. **topic_log.json** — category rotation history
3. **WordPress last 25 research posts** — what was actually published:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=research_update,per_page=25,status=publish
   ```
   Read ALL 25 titles. Note what's covered, what's NOT.

## Research Process

### Step 1: Freshness Scan (Brave) — 7 days, not 24 hours
```
web_search query="GLP-1 obesity weight loss medication clinical trial FDA approval 2026" freshness="week" count=10
```
Then broaden:
```
web_search query="semaglutide tirzepatide orforglipron obesity research 2026" freshness="month" count=10
```
If you find nothing in a month of obesity research, something is wrong with the search.

### Step 2: Deep Dive (Tavily) — on the top 2-3 findings
For each promising result from Brave, run a comprehensive Tavily search:
```
/home/ethan/.openclaw/workspace/skills/tavily-search/tavily_search.py "<topic> obesity GLP-1 clinical" --freshness week --depth comprehensive --max-results 5
```
**Tavily is the critical tool here** — it provides structured JSON with source URLs, citations, and key facts. Use it. Do not skip this step.

### Step 3: Gap Analysis
Cross-reference what you found against the last 25 research post titles. If your topic is too similar to something recently published, pick a different angle or skip it.

### Step 4: Colorado Tie-In
If the topic has a natural Denver/Colorado/Front Range angle, note it. If not, still proceed — clinical relevance to CNC patients is sufficient.

### Step 5: Blog Potential Check
Mark `has_blog_potential: true` if:
- It's a comparison topic (Wegovy vs Zepbound, oral vs injectable)
- It has a patient FAQ angle
- It covers a high-volume keyword from keyword-page-map

## Topic Selection Criteria
Pick the topic that is:
1. **Most clinically relevant** to CNC's patient population
2. **Most recently published** (prioritize newer research)
3. **Has a strong citation** from a real source (NEJM, Lancet, FDA, BMJ, etc.)
4. **NOT covered** in the last 25 research posts

## Output: topic-research.json
```json
{
  "topic": "Selected topic title",
  "category": "Medical|Nutritional|Lifestyle|Behavioral",
  "link": "Primary source URL (must be real, verifiable)",
  "citation": "Citation: Journal name, date, authors",
  "summary": "2-sentence clinical summary",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "has_blog_potential": true,
  "colorado_tie_in": "How this connects to CNC patients",
  "status": "PROCEED"
}
```

## If Nothing Worthwhile Found After All Research
Run Tavily on broader obesity/weight loss topics:
```
/home/ethan/.openclaw/workspace/skills/tavily-search/tavily_search.py "obesity treatment GLP-1 weight loss breakthrough 2026" --depth comprehensive --max-results 10
```
If STILL nothing, output `ABORT_WORKFLOW`. Do not force a research post just to hit the schedule.

## Rules
- **24-hour cutoff is TOO RESTRICTIVE** — use 7 days minimum
- **Must use Tavily** for deep research on every topic
- **Must verify against last 25 research posts** — no duplicates
- **Must cite real sources** — if you can't find a citation, ABORT_WORKFLOW
- **Colorado tie-in:** note it but don't require it for research posts

## Model
`minimax/MiniMax-M2.7`
