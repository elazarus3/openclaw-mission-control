# Image Generator Agent (image-generator.md)

## Goal
Generate a featured image for the research post using the **Nano Banana** model (`google/gemini-3.1-flash-image-preview`), Google's native multimodal image generation API.

## Model
`google/gemini-3.1-flash-image-preview` (alias: `nano-banana`)

## Primary Method: Gemini Nano Banana API

Use the following Python script. The `inline_data.data` field returns raw bytes — write directly, no base64 decoding required.

```python
#!/usr/bin/env python3
"""Generate research post featured image using Gemini Nano Banana (gemini-3.1-flash-image-preview)"""
import sys
from pathlib import Path
from google import genai
from google.genai import types

import os
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GEMINI_API_KEY:
    env_file = "/home/ethan/.openclaw/api_keys.env"
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("export GOOGLE_API_KEY="):
                GEMINI_API_KEY = line.split("=")[1].strip().strip('"')
                break
OUTPUT_PATH = "projects/research-post/posts/<seo-filename>.jpg"
PROMPT = "<your image prompt here>"

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"]
    )
)

saved = False
for part in response.candidates[0].content.parts:
    if hasattr(part, 'inline_data') and part.inline_data:
        raw = part.inline_data.data  # already bytes, write directly
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(raw)
        print(f"Image saved: {OUTPUT_PATH} ({len(raw):,} bytes)")
        saved = True
        break

if not saved:
    print("ERROR: No image in response", file=sys.stderr)
    sys.exit(1)
```

**Important:** The venv at `/home/ethan/.openclaw/workspace/venv` has `google-genai` installed. Always activate it first:
```bash
source /home/ethan/.openclaw/workspace/venv/bin/activate
python3 generate_image.py
```

## Fallback Method: Pollinations.ai

If the Gemini API fails (rate limit, error), fall back to Pollinations.ai:

```bash
PROMPT="<your prompt here>"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PROMPT'))")
curl -sL "https://image.pollinations.ai/prompt/${ENCODED}?width=1200&height=630&model=flux&nologo=true&seed=42" \
  -o "projects/research-post/posts/<seo-filename>.jpg"
```

## Image Prompt Guidelines
- Clean, professional, medical/health-focused aesthetic
- Natural lighting, empowering composition
- Colorado/altitude/lifestyle theme when clinically relevant
- **No needles or syringes visible** (ever)
- **No identifiable people** (avoid likeness issues)
- **NO text, words, letters, or signage** — zero text in images
- **Person-first visual language** — empowering, not stigmatizing
- Color palette: whites, soft blues, natural greens
- Blog header ratio: 16:9

## Input
- **Topic:** {{topic}}
- **SEO Title:** {{seo_title}}

## Output
- Full path to the saved `.jpg` file
- Confirmation of which method was used (Nano Banana vs. Pollinations fallback)
