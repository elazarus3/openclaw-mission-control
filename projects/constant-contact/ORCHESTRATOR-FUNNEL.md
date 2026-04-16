# Constant Contact Newsletter — Funnel Orchestrator v2

**Goal:** Transform the newsletter from a blog digest into a reactivation and nurturing funnel.

**Audience split:**
- **Active patients** (~600): Keep them engaged, upsell services, reinforce adherence
- **Lapsed patients** (~5,400): Bring them back — this is the goldmine

**Monthly structure (5 sections, ONE CTA):**

| Section | Active patients | Lapsed patients |
|---|---|---|
| **Hook** | "Quick check-in from Dr. Lazarus" | "It's been a while — we miss you" |
| **Deep dive** | 1 compelling clinical topic | 1 compelling clinical topic |
| **By the numbers** | Social proof of outcomes | Social proof of outcomes |
| **New at CNC** | New services / tips | Why to come back |
| **CTA** | "Book your next visit" | "Call us — no judgment" |

## Subagents
- `subagents/segment-researcher.md` — check patient segments, determine focus
- `subagents/reactivation-writer.md` — generate the hook + reactivation angle for this month
- `subagents/deep-dive-picker.md` — pick the single best blog post to feature
- `subagents/assembler-v2.md` — build the full HTML newsletter
- `subagents/uploader-v2.md` — upload to Constant Contact
- `subagents/notifier.md` — email full report to ethanlazarus@gmail.com

## Execution
Spawn subagents sequentially. Use model `minimax/MiniMax-M2.7` for all.
