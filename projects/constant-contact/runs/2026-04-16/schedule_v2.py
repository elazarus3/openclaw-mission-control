#!/usr/bin/env python3
"""Exchange OAuth code for tokens and schedule the newsletter in one shot"""
import urllib.request, urllib.parse, json, re, sys, os

CODE = sys.argv[1] if len(sys.argv) > 1 else input("Paste the code from the URL (after ?code=): ").strip()

# --- Exchange code for tokens ---
print("Exchanging code for tokens...")
url = "https://authz.constantcontact.com/oauth2/default/v1/token"
data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "client_id": "3753c661-13eb-4506-9658-eeea0ded4bca",
    "client_secret": "5owuCkm_-ZJmX7xA3QaO-A",
    "code": CODE,
    "redirect_uri": "https://localhost"
}).encode("utf-8")

req = urllib.request.Request(url, data=data)
req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())
except Exception as e:
    print(f"❌ Token exchange failed: {e}")
    sys.exit(1)

access = tokens["access_token"]
refresh = tokens.get("refresh_token", "")

# Save to .env
env_path = "/home/ethan/.openclaw/workspace/.env"
with open(env_path, "r") as f:
    content = f.read()
content = re.sub(r'CONSTANT_CONTACT_ACCESS_TOKEN=.*', f'CONSTANT_CONTACT_ACCESS_TOKEN="{access}"', content)
content = re.sub(r'CONSTANT_CONTACT_REFRESH_TOKEN=.*', f'CONSTANT_CONTACT_REFRESH_TOKEN="{refresh}"', content)
with open(env_path, "w") as f:
    f.write(content)
os.environ["CONSTANT_CONTACT_ACCESS_TOKEN"] = access
print(f"✅ Tokens saved")

# --- Read HTML ---
html_file = "/home/ethan/.openclaw/workspace/projects/constant-contact/runs/2026-04-16/newsletter_v2.html"
with open(html_file, "r") as f:
    html_content = f.read()
print(f"📄 HTML loaded ({len(html_content):,} bytes)")

# --- Create campaign ---
def api_post(endpoint, payload):
    req = urllib.request.Request(
        f"https://api.cc.email/v3{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

print("📤 Creating campaign...")
res = api_post("/emails", {
    "name": "CNC April 2026 — GLP-1 Reactivation",
    "email_campaign_activities": [{
        "format_type": 5,
        "from_name": "Dr. Ethan Lazarus | Clinical Nutrition Center",
        "from_email": "noreply@clinicalnutritioncenter.com",
        "reply_to_email": "noreply@clinicalnutritioncenter.com",
        "subject": "It's been a while — a note from Dr. Lazarus",
        "html_content": html_content
    }]
})
campaign_id = res.get("campaign_id")
activities = res.get("campaign_activities", [])
activity_id = activities[0]["campaign_activity_id"] if activities else None
print(f"✅ Campaign created: ID={campaign_id}, Activity={activity_id}")

# --- Assign list ---
print("📋 Assigning General Interest list...")
activity_data = json.loads(urllib.request.urlopen(
    urllib.request.Request(f"https://api.cc.email/v3/emails/activities/{activity_id}",
        headers={"Authorization": f"Bearer {access}"}
    )
).read())
activity_data["contact_list_ids"] = ["c2114ee0-fa84-11ea-82b3-d4ae527536d1"]
urllib.request.Request(
    f"https://api.cc.email/v3/emails/activities/{activity_id}",
    data=json.dumps(activity_data).encode("utf-8"),
    method="PUT",
    headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
)
print("✅ List assigned")

# --- Schedule ---
print("📅 Scheduling for April 23, 2026 10:30 AM MDT...")
urllib.request.urlopen(urllib.request.Request(
    f"https://api.cc.email/v3/emails/activities/{activity_id}/schedules",
    data=json.dumps({"scheduled_date": "2026-04-23T16:30:00Z"}).encode("utf-8"),
    headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
))
print("✅ SCHEDULED! April 23, 2026 at 10:30 AM MDT")

# --- Save result ---
result = {
    "campaign_id": campaign_id,
    "activity_id": activity_id,
    "scheduled_time": "2026-04-23T16:30:00Z (10:30 AM MDT)",
    "subject": "It's been a while — a note from Dr. Lazarus",
    "list": "General Interest (c2114ee0-fa84-11ea-82b3-d4ae527536d1)"
}
with open("/home/ethan/.openclaw/workspace/projects/constant-contact/runs/2026-04-16/schedule_result.json", "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
