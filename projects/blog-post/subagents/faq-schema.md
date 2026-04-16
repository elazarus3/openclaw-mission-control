# FAQ Schema Subagent (Blog Post)

## Goal
Generate 3-5 FAQ items + proper FAQ schema JSON-LD markup for the blog post. FAQ schema is critical for AI search citation and rich snippets in Google.

## Input
Read from the run folder:
- `draft.md` — the article draft
- `seo.json` — the SEO metadata (for keyword context)
- `topic` — the post topic

## FAQ Generation Rules
- Generate FAQs that a **patient** would actually ask — common questions before a first visit, GLP-1 questions, nutrition questions, etc.
- Questions must be grounded in the article content — don't invent questions the article doesn't answer
- Answers: 2-4 sentences, 8th-grade reading level, plain language
- Prioritize questions that match high-volume search queries (e.g., "how much does Wegovy cost", "what to eat on GLP-1")
- Colorado/Denver local angle should appear in at least one answer if relevant

## Output Format
Save to `projects/blog-post/posts/YYYY-MM-DD/faq-schema.json`:

```json
{
  "faqs": [
    {
      "question": "Patient-friendly question 1?",
      "answer": "Brief plain-language answer, 2-4 sentences."
    }
  ],
  "json_ld": "<!-- COPY THIS EXACTLY INTO THE HTML -->\n<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"FAQPage\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"Patient-friendly question 1?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"Brief plain-language answer.\"\n      }\n    }\n  ]\n}\n</script>"
}
```

## Injection Instructions for Article Uploader
The article uploader must inject the JSON-LD:
- Place the `<script type="application/ld+json">...</script>` in the HTML `<head>` section
- If the HTML has no `<head>`, place it immediately after `<body>`
- The FAQ section should also be added as visible HTML at the bottom of the article content (rendered FAQs, not just schema)

## Model
`minimax/MiniMax-M2.7`
