# Constant Contact Newsletter — Funnel Orchestrator v2

**Goal:** Transform the newsletter from a blog digest into a reactivation and nurturing funnel. Works for BOTH active and lapsed patients — universal tone, never alienating.

---

## NON-NEGOTIABLE RULES (Apply to Every Newsletter)

### Data & Accuracy
- **NEVER hallucinate data.** Only use numbers provided by Dr. Lazarus or cited from verifiable sources (Novo Nordisk, Eli Lilly, clinical trials).
- **Verified clinic stats (safe to use):**
  - Patients on GLP-1 medications lose an average of **35–50 lbs** (source: Novo Nordisk & Eli Lilly clinical data)
  - CNC has been under the direction of **Dr. Lazarus for 22 years**
  - CNC has served **5,000+ people** in the Denver Metro area
- If real data isn't available, remove the section — never make up numbers.

### Contact Info (Always Correct)
- **Address:** 5995 Greenwood Plaza Blvd, Suite 150, Greenwood Village, CO 80111
- **Phone:** (303) 750-9454
- **Website:** clinicalnutritioncenter.com

### Sender & Technical
- **From email:** `info@clinicalnutritioncenter.com` (always verified — do NOT use other addresses)
- **CTA button:** Must link to `https://www.clinicalnutritioncenter.com/contact-us`
- **Reply-to:** Do NOT say "reply to this email" — use "Call us at (303) 750-9454"

### Content Requirements
- **Research spotlight:** Link to the most compelling research article of the month
- **Blog highlights:** Link to 1–2 most compelling blog posts (fetch from WordPress `post_type=post`)
- **Quick Q&A:** Include one common patient question answered in 2 sentences
- **Tone:** Universal — works for active patients AND lapsed patients. Avoid language that assumes someone has fallen away.

---

## Monthly Newsletter Structure

| Section | Content |
|---|---|
| **Header** | CNC logo + month badge |
| **Hook** | Warm welcome from Dr. Lazarus, universal tone |
| **By the Numbers** | 3 verified stats (use only the 3 above) |
| **Research Spotlight** | Most compelling research post of the month (fetch from WP `post_type=research_update`) |
| **Blog Highlights** | 1–2 most-read blog posts with thumbnails |
| **Quick Q&A** | One common patient question, 2-sentence answer |
| **CTA** | "Contact Us Now" button → `/contact-us` |
| **Footer** | Address, phone, unsubscribe link, medical disclaimer |

---

## Subagents
- `subagents/segment-researcher.md` — fetch latest posts from WordPress, pick the best research + blog content
- `subagents/reactivation-writer.md` — write hook, by-the-numbers copy, quick Q&A
- `subagents/assembler-v2.md` — build the full HTML newsletter
- `subagents/uploader-v2.md` — upload to Constant Contact, schedule
- `subagents/notifier.md` — send full report to ethanlazarus@gmail.com

## Execution
Spawn subagents sequentially. Use model `minimax/MiniMax-M2.7` for all.
