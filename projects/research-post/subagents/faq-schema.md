# FAQ Schema Subagent (Research Post)

## Goal
Generate 3-5 FAQ items + proper FAQ schema JSON-LD markup for the research post. This is critical for AI search citation — FAQ schema is the single biggest on-page SEO quick win.

## Input
Read from the run folder:
- `draft.md` — the article draft
- `topic-research.json` — the topic context
- `seo.json` — the SEO metadata

## FAQ Generation Rules
- Generate FAQs that a **patient** would actually ask (not clinical jargon)
- Questions should come directly from the article content — don't invent questions the article doesn't answer
- Keep answers brief: 2-4 sentences, 8th-grade reading level
- FAQ questions should complement the article, not repeat it verbatim
- Example FAQ sources: side effects patients ask about, dosing questions, lifestyle questions, insurance/cost questions

## Output Format
Save to `projects/research-post/posts/YYYY-MM-DD/faq-schema.json`:

```json
{
  "faqs": [
    {
      "question": "Patient-friendly question 1?",
      "answer": "Brief plain-language answer, 2-4 sentences."
    },
    {
      "question": "Patient-friendly question 2?",
      "answer": "Brief plain-language answer, 2-4 sentences."
    }
  ],
  "json_ld": "<!-- COPY THIS EXACTLY INTO THE HTML HEAD -->\n<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"FAQPage\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"Patient-friendly question 1?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"Brief plain-language answer.\"\n      }\n    }\n  ]\n}\n</script>"
}
```

## Schema Requirements
- `@type`: `FAQPage`
- `@context`: `https://schema.org`
- Each question: `@type: Question`, `name`
- Each answer: `@type: Answer`, `text`
- Inject the JSON-LD into the HTML `<head>` section (or immediately after `<body>` if no head)

## Model
`minimax/MiniMax-M2.7`
