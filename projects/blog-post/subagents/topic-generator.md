# Blog Topic Generator

## Goal
Generate 3 ranked blog post topic recommendations based on SEO value, patient interest, and Colorado/Denver relevance — then save them for the orchestrator to pick from.

## When This Agent Runs
- If the orchestrator is called **without** a specific topic provided → run topic generator first
- If a topic IS provided → skip this agent and pass the provided topic to Writer

## Inputs to Read Before Generating
1. **`projects/blog-post/master-log.json`** — what was published in the last 60 days (avoid duplicates)
2. **`projects/website-orchestrator/memory/keyword-page-map.md`** — Tier 1-3 SEO keywords (use these as topic seeds)
3. **`projects/website-orchestrator/memory/keyword-research.md`** — search volume and competition data
4. **WordPress last 20 posts** — most recent published blog posts:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=post,per_page=20,status=publish
   ```
5. **Current date** — factor in seasonal relevance (New Year: Jan, Obesity Week: March, summer: May-June, back-to-school: Aug, OMA conference: Oct-Nov)

## Topic Generation Rules
- **SEO-first**: Every topic must map to a keyword in the keyword-page-map with meaningful search volume or low competition opportunity
- **Colorado/Denver anchor**: Each topic must have a natural local tie-in (Denver, Greenwood Village, Front Range, Colorado, Mile High)
- **Patient-facing**: Topics should be things a patient considering CNC would search (not purely academic)
- **No duplication**: Topics covered in the last 60 days are disqualified
- **Diversity**: Aim for variety across categories: Medical (GLP-1, medications), Nutritional (diet strategies), Lifestyle (exercise, sleep), Behavioral (mindset, habits)

## Priority Keyword Targets (from keyword-page-map.md — use these first)
1. "medical weight loss denver" — Tier 1, own this
2. "registered dietitian near me" — 6,600 searches, huge opportunity
3. "wegovy vs zepbound" — comparison, low competition, high intent
4. "telehealth weight loss denver" — emerging, first-mover
5. "nutritionist in denver" / "dietitian denver" — 390 searches, low competition
6. "highlands ranch weight loss" — geo expansion
7. "glp-1 side effects" — high volume, patient concern
8. "protein on GLP-1" — high engagement, CNC already strong here

## Output Format
Save to `projects/blog-post/posts/YYYY-MM-DD/topic-recommendations.json`:
```json
{
  "date": "YYYY-MM-DD",
  "recommendations": [
    {
      "rank": 1,
      "topic": "Topic title",
      "primary_keyword": "...",
      "colorado_anchor": "...",
      "seo_tier": "Tier 1|2|3",
      "search_volume_note": "...",
      "rationale": "Why this topic, why now",
      "category": "Medical|Nutritional|Lifestyle|Behavioral"
    },
    { "rank": 2, ... },
    { "rank": 3, ... }
  ],
  "selected": null,
  "status": "AWAITING_APPROVAL"
}
```

The orchestrator will auto-select rank 1 unless Dr. Lazarus overrides.

## Model
`minimax/MiniMax-M2.7`

## If No Topic Found
If all priority keywords are covered in the last 60 days and no seasonal opportunity exists, output `ABORT_WORKFLOW` with a note.
