# WordPress Media Uploader Agent (wp-media-uploader.md)

## Task
Upload the generated image to the WordPress media library and set alt text.

## CRITICAL: Alt Text Is Required
**Every image MUST have descriptive alt text.** This is a accessibility requirement and impacts SEO. Generate it from the topic/SEO data.

Good alt text examples:
- "GLP-1 weight loss medication pens on a clinical countertop in a Denver medical clinic"
- "Research materials and medical data in a clinical research setting"
- "Modern medical clinic interior with natural lighting"

Bad alt text (too vague):
- "image" / "photo" / "research image" / "featured image"

## Upload Command
Use `curl --data-binary` — Python requests gets 403 on this WordPress host:
```bash
IMAGE_PATH="/path/to/image.jpg"
ALT_TEXT="Your descriptive alt text here"
WP_USER="drlazarus"
WP_PASS="1ggq 5syX 9ztB YhUs P2FH aEEh"
AUTH_HEADER="Authorization: Basic $(echo -n "${WP_USER}:${WP_PASS}" | base64)"

curl -s -X POST "https://www.clinicalnutritioncenter.com/wp-json/wp/v2/media" \
  -H "${AUTH_HEADER}" \
  -H "Content-Disposition: attachment; filename=$(basename "$IMAGE_PATH")" \
  -H "Content-Type: image/jpeg" \
  --data-binary @"${IMAGE_PATH}"
```

Then set alt text on the uploaded media:
```bash
MEDIA_ID="<id from upload response>"
curl -s -X POST "https://www.clinicalnutritioncenter.com/wp-json/wp/v2/media/${MEDIA_ID}" \
  -H "${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  -d "{\"alt_text\": \"$ALT_TEXT\"}"
```

## Input
- Image Path: `{{image_path}}`
- Topic / SEO Title: Use the research topic to generate descriptive alt text

## Output
- Media ID: {{media_id}}
- Media URL: {{media_url}}
- Alt Text: {{alt_text_used}}
