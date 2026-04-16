# Newsletter Assembler v2 — Funnel Edition

## Goal
Assemble a full HTML newsletter following the funnel structure. Works for BOTH active and lapsed patients — universal tone.

## Input
Read from the run folder:
- `segment-context.json`
- `hook.html`
- `deep_dive.json`
- `summarized_articles.json` (or fetched from WordPress directly)

## NON-NEGOTIABLE RULES (Always Apply)

### Contact Info — ALWAYS CORRECT
- Address: **5995 Greenwood Plaza Blvd, Suite 150, Greenwood Village, CO 80111**
- Phone: **(303) 750-9454**
- Website: clinicalnutritioncenter.com

### Data — ONLY VERIFIED NUMBERS
- 35–50 lbs avg weight loss on GLP-1s (cite: Novo Nordisk & Eli Lilly data)
- 22 years under Dr. Lazarus
- 5,000+ patients in Denver Metro
- **Never invent numbers. If unsure, remove the section.**

### Sender & CTA
- From: `info@clinicalnutritioncenter.com`
- Reply-to: `info@clinicalnutritioncenter.com`
- CTA button MUST link to: `https://www.clinicalnutritioncenter.com/contact-us`
- Never say "reply to this email"

## Newsletter Structure

```
[HEADER — CNC Logo + Month]
[HOOK — Warm universal welcome from Dr. Lazarus]
[BY THE NUMBERS — 3 verified stats, navy background, white text]
[RESEARCH SPOTLIGHT — Best research post with image, excerpt, CTA]
[BLOG HIGHLIGHTS — 1-2 blog posts with thumbnail, title, excerpt, link]
[QUICK Q&A — One common patient question, 2 sentences]
[CTA SECTION — "Contact Us Now" → /contact-us]
[FOOTER — Address, phone, unsubscribe, medical disclaimer]
```

## Design Rules
- Clean, mobile-responsive HTML (600px max-width, email-safe table layout)
- CNC brand: navy (#2c3e50), white, light blue accent (#4a90e2), red accent (#e74c3c) for research
- Fonts: Helvetica Neue, Arial, sans-serif (email-safe)
- No markdown — pure HTML
- CTA button: Navy background, white text, rounded corners, links to `/contact-us`
- Images: use actual WordPress media URLs
- Subject line: Compelling, clinical, not salesy

## Output
Write `newsletter_v2.html` to the run folder.

## Model
minimax/MiniMax-M2.7
