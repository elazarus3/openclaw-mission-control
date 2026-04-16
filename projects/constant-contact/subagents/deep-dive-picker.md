# Deep Dive Picker

## Goal
Select the single best blog post to feature as the newsletter's centerpiece — not 6 summaries, ONE strong piece.

## Input
Read `subagents/segment-context.json` from the run folder.
Read `projects/constant-contact/summarized_articles.json` or check WordPress for recent posts.

## Selection Criteria
- Clinical relevance: something that addresses a common patient question or misconception
- Evergreen appeal: won't feel dated in 3 months
- Emotional hook: has a "wait, really?" or "I didn't know that" angle
- Local/Denver tie-in if possible

## Output
Write `deep_dive.json` to the run folder:
```json
{
  "post_title": "...",
  "post_url": "...",
  "post_image_url": "...",
  "one_paragraph_summary": "2-3 sentences explaining why this matters to the reader",
  "pull_quote": "one memorable line from the article, ≤120 chars"
}
```

## Model
minimax/MiniMax-M2.7
