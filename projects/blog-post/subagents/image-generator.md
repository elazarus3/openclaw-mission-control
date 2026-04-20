# Image Generator Agent (image-generator.md)

## Goal
Generate a **photorealistic** featured image for the blog post using the **Nano Banana** model (`google/gemini-3.1-flash-image-preview`).

## Model
`google/gemini-3.1-flash-image-preview` (alias: `nano-banana`)

## Python Script Template
```python
#!/usr/bin/env python3
"""Generate blog post featured image — photorealistic"""
import sys
from pathlib import Path
from google import genai
from google.genai import types

import os
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GEMINI_API_KEY:
    # Fallback: load from api_keys.env
    env_file = "/home/ethan/.openclaw/api_keys.env"
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("export GOOGLE_API_KEY="):
                GEMINI_API_KEY = line.split("=")[1].strip().strip('"')
                break
OUTPUT_PATH = "projects/blog-post/posts/YYYY-MM-DD/image.jpg"
PROMPT = "YOUR PHOTOREALISTIC PROMPT HERE"

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"]
    )
)

for part in response.candidates[0].content.parts:
    if hasattr(part, 'inline_data') and part.inline_data:
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(part.inline_data.data)
        print(f"Saved: {OUTPUT_PATH} ({len(part.inline_data.data):,} bytes)")
        break
```

## PROMPT WRITING RULES — PHOTOREALISTIC ONLY

**What to write in your prompt:**
- Start with: `Photorealistic photograph of...`
- Describe a real-world scene with specific physical details
- Use: natural light, soft shadows, real textures, shallow depth of field
- Include: actual objects in real settings (not abstract or symbolic)
- Colorado context: real Denver/Colorado settings when relevant — actual mountains in background, real clinic interiors, real food photography
- Medical context: real clinical settings — examination rooms, consultation settings, real food portions on real plates

**What NEVER to write:**
- ❌ "digital illustration," "3D render," "isometric," "clean graphic"
- ❌ "modern flat design," "minimalist icon," "stylized"
- ❌ Anything that makes it look like AI clip art
- ❌ Overly perfect skin, impossible lighting, surreal elements
- ❌ Text, logos, faces, identifiable people

**Style reference for photorealistic prompts:**
```
Photorealistic photograph of a dietitian in a modern clinic in Greenwood Village, Colorado, consulting with a patient at a table. Natural window light, soft shadows, shallow depth of field, Canon EOS R5, 85mm lens. Real clinical environment with natural textures.
```
vs.
```
A modern clinic with a dietitian and patient, clean white walls, blue accents, minimal design, professional medical aesthetic
```
**→ The first one produces a real-looking photo. The second produces AI clip art.**

## Input
- **Topic:** {{topic}}
- **SEO Title:** {{seo_title}}

## Output
- Full path to saved `.jpg`
- Confirm photorealistic method used

## Fallback
If Gemini fails, do NOT fall back to Pollinations.ai (it produces illustration-style images, not photorealistic). Report the failure and let the orchestrator decide whether to retry or skip the image.
