#!/bin/bash
# Upload featured image to WordPress media library
# Usage: ./upload-media.sh <image_path> <alt_text>

WP_URL="https://www.clinicalnutritioncenter.com"
WP_USER="drlazarus"
WP_PASS="1ggq 5syX 9ztB YhUs P2FH aEEh"
IMAGE_PATH="${1:-}"
ALT_TEXT="${2:-}"

if [ -z "$IMAGE_PATH" ] || [ ! -f "$IMAGE_PATH" ]; then
    echo "ERROR: Image file not found: $IMAGE_PATH"
    exit 1
fi

AUTH_HEADER="Authorization: Basic $(echo -n "${WP_USER}:${WP_PASS}" | base64)"

RESPONSE=$(curl -s -X POST "${WP_URL}/wp-json/wp/v2/media" \
  -H "${AUTH_HEADER}" \
  -H "Content-Disposition: attachment; filename=$(basename "$IMAGE_PATH")" \
  -H "Content-Type: image/jpeg" \
  --data-binary @"${IMAGE_PATH}" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

echo "$BODY" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print('media_id:', d.get('id'))
    print('media_url:', d.get('source_url'))
    print('alt_text:', d.get('alt_text'))
except:
    print('raw:', sys.stdin.read()[:200])
"
echo "HTTP: $HTTP_CODE"
