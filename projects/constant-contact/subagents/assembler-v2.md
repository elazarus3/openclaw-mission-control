# Newsletter Assembler v2 — Funnel Edition

## Goal
Assemble a full HTML newsletter following the funnel structure. This is NOT a blog digest — it is a reactivation and nurturing tool.

## Input
Read from the run folder:
- `segment-context.json`
- `hook.html`
- `deep_dive.json`
- `summarized_articles.json` (any remaining blog posts to optionally feature in a sidebar/brief mentions)

## Newsletter Structure

```
[HEADER — CNC Logo + Month]

[HOOK SECTION — The "We Miss You" or "Check-In" opener]
  - Subject line, preview text

[DEEP DIVE — Single featured article, full treatment]
  - Image, pull quote, one paragraph, CTA button

[BY THE NUMBERS — Social proof strip]
  - 3 stats in a row (patients served, weight lost, GLP-1 programs)

[NEW AT CNC — What's new at the clinic]
  - New services, new staff, seasonal tips, or quick clinical Q&A

[QUICK Q&A — One common patient question answered in 2 sentences]
  - Example: "Can I drink alcohol on Zepbound?" / "Is it OK to skip a dose?"

[FOOTER — CTA + Contact info]
  - ONE primary CTA (Call to book, for lapsed: "Call us — no lecture, just help")
  - Phone: (303) 750-9454
  - Address: 7780 South Hill Road, Greenwood Village, CO 80112
  - "You're receiving this because you're on our mailing list. Update preferences."
```

## Design Rules
- Clean, mobile-responsive HTML (600px max-width, email-safe table layout)
- CNC brand colors: navy (#2c3e50), white, light blue accent (#4a90e2)
- Fonts: Helvetica Neue, Arial, sans-serif (email-safe)
- No markdown — pure HTML
- Images: use actual image URLs from WordPress/media library
- CTA button: Navy background, white text, rounded corners, prominent

## Output
Write `newsletter_v2.html` to the run folder. This is the final HTML ready for Constant Contact upload.

## Model
minimax/MiniMax-M2.7
