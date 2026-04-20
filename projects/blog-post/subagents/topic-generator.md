# Blog Topic Generator

## Goal
Generate 3 ranked blog post topic recommendations — backed by real research into what's missing from the existing content library. Pick topics that are genuinely interesting, not just SEO-compliant.

## When This Agent Runs
- If orchestrator is called **without** a specific topic → run this first
- If a topic IS provided → skip this agent

## Pre-Flight: Read ALL of These BEFORE generating recommendations

1. **`projects/blog-post/master-log.json`** — all posts from the last 90 days
2. **`projects/website-orchestrator/memory/keyword-page-map.md`** — Tier 1-3 SEO keywords
3. **`projects/website-orchestrator/memory/keyword-research.md`** — search volume and competition
4. **WordPress last 25 published blog posts** — actual published titles and topics:
   ```
   node /home/ethan/.openclaw/workspace/skills/wordpress/scripts/wp-cli.js posts:list --query post_type=post,per_page=25,status=publish
   ```
   Read ALL 25 titles. Identify patterns: what categories are oversaturated? What's missing?
5. **Seasonal calendar** — factor in timing (New Year: Jan, Obesity Week: March, summer: May-June, back-to-school: Aug, OMA conference: Oct-Nov)

## Topic Research Process (Do This Before Writing Recommendations)

### Step 1: Audit the Last 25 Posts
For each of the last 25 posts, note:
- Title
- Category (Medical/Nutritional/Lifestyle/Behavioral)
- Keyword targeted

Then ask: **What is genuinely missing from this list?**
- Which categories are oversaturated?
- Which SEO keywords from keyword-page-map are NOT covered?
- What would a real patient in Denver actually search for that CNC hasn't addressed?

### Step 2: Find the Gaps
Cross-reference the last 25 titles against the priority keyword list. Look for:
- High-volume keywords with NO post (wegovy vs zepbound, telehealth weight loss denver)
- Patient questions that haven't been answered (side effects, what to eat, how to titrate)
- Colorado-specific angles on topics CNC HAS covered generically

### Step 3: Pick 3 Topics from Real Gaps
Recommend only topics that:
1. Map to an actual keyword in keyword-page-map with real search volume
2. Fill a genuine gap in the last 25 posts (no similar titles)
3. Have a natural Colorado/Denver anchor
4. Are genuinely interesting to a patient — not just "good for SEO"

## Output Format
Save to `projects/blog-post/posts/YYYY-MM-DD/topic-recommendations.json`:
```json
{
  "date": "YYYY-MM-DD",
  "audit_of_last_25": "Brief note: what categories are oversaturated, what's missing",
  "recommendations": [
    {
      "rank": 1,
      "topic": "Topic title",
      "primary_keyword": "...",
      "colorado_anchor": "...",
      "seo_tier": "Tier 1|2|3",
      "rationale": "Why THIS topic now, what's missing from last 25 posts",
      "category": "Medical|Nutritional|Lifestyle|Behavioral",
      "has_blog_potential": true
    }
  ],
  "selected": null,
  "status": "AWAITING_APPROVAL"
}
```

## Priority Keywords — Target These First (from keyword-page-map)
| Keyword | Monthly Searches | Status in Last 25 Posts? |
|---|---|---|
| medical weight loss denver | geo | ??? |
| registered dietitian near me | 6,600 | Done Apr 16 |
| wegovy vs zepbound | low comp | ??? |
| telehealth weight loss denver | emerging | ??? |
| nutritionist in denver | 390 | ??? |
| glp-1 side effects | high | ??? |
| highlands ranch weight loss | geo | ??? |

## Rules
- **No duplication within 90 days**
- **Must fill a real gap** — not a variation of a recent post
- **Colorado anchor** required
- **Genuinely interesting** to a real patient — not just keyword-stuffed

## If All Gaps Are Covered
If every priority keyword is already in the last 25 posts, output `ABORT_WORKFLOW` with a note listing what's already covered. Do NOT force a topic.

## Model
`minimax/MiniMax-M2.7`
