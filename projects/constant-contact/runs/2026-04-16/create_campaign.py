#!/usr/bin/env python3
"""Create and schedule the CNC newsletter campaign in Constant Contact"""
import re, json, urllib.request, urllib.parse, urllib.error, os
from dotenv import load_dotenv

load_dotenv("/home/ethan/.openclaw/workspace/.env")

CLIENT_ID = "3753c661-13eb-4506-9658-eeea0ded4bca"
CLIENT_SECRET = "5owuCkm_-ZJmX7xA3QaO-A"
BASE_URL = "https://api.cc.email/v3"
ENV_PATH = "/home/ethan/.openclaw/workspace/.env"

def refresh_tokens():
    url = "https://authz.constantcontact.com/oauth2/default/v1/token"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": os.environ.get("CONSTANT_CONTACT_REFRESH_TOKEN")
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        new_access = res_data["access_token"]
        new_refresh = res_data["refresh_token"]
        # Update .env
        with open(ENV_PATH, "r") as f:
            content = f.read()
        content = re.sub(r'CONSTANT_CONTACT_ACCESS_TOKEN=.*', f'CONSTANT_CONTACT_ACCESS_TOKEN="{new_access}"', content)
        content = re.sub(r'CONSTANT_CONTACT_REFRESH_TOKEN=.*', f'CONSTANT_CONTACT_REFRESH_TOKEN="{new_refresh}"', content)
        with open(ENV_PATH, "w") as f:
            f.write(content)
        os.environ["CONSTANT_CONTACT_ACCESS_TOKEN"] = new_access
        os.environ["CONSTANT_CONTACT_REFRESH_TOKEN"] = new_refresh
        print(f"✅ Tokens refreshed. New access: {new_access[:25]}...")
        return new_access

def api_request(method, endpoint, data=None, retry=True):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {os.environ.get('CONSTANT_CONTACT_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read()
            if res_data:
                return json.loads(res_data.decode("utf-8"))
            return {}
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            refresh_tokens()
            return api_request(method, endpoint, data, retry=False)
        error_body = e.read().decode("utf-8")
        print(f"API Error {e.code} on {endpoint}: {error_body}")
        raise

# 1. Read HTML
html_file = "/home/ethan/.openclaw/workspace/projects/constant-contact/runs/2026-04-16/newsletter_v2.html"
with open(html_file, "r") as f:
    html_content = f.read()
print(f"📄 Read HTML ({len(html_content):,} bytes)")

# 2. Draft Campaign
payload = {
    "name": "CNC April 2026 — GLP-1 Reactivation",
    "email_campaign_activities": [{
        "format_type": 5,
        "from_name": "Dr. Ethan Lazarus | Clinical Nutrition Center",
        "from_email": "noreply@clinicalnutritioncenter.com",
        "reply_to_email": "noreply@clinicalnutritioncenter.com",
        "subject": "It's been a while — a note from Dr. Lazarus",
        "html_content": html_content
    }]
}
print("📤 Creating campaign...")
res = api_request("POST", "/emails", data=payload)
print(f"Raw response: {json.dumps(res, indent=2)[:500]}")

campaign_id = res.get("campaign_id")
activities = res.get("campaign_activities") or res.get("email_campaign_activities", [])
activity_id = activities[0].get("campaign_activity_id") if activities else None
print(f"✅ Campaign created! ID: {campaign_id}, Activity ID: {activity_id}")

# 3. Assign Contact Lists
print("📋 Assigning contact list...")
activity_data = api_request("GET", f"/emails/activities/{activity_id}")
activity_data["contact_list_ids"] = ["c2114ee0-fa84-11ea-82b3-d4ae527536d1"]
api_request("PUT", f"/emails/activities/{activity_id}", data=activity_data)
print("✅ List assigned")

# 4. Schedule
print("📅 Scheduling for April 23, 2026 at 10:30 AM MDT...")
schedule_payload = {"scheduled_date": "2026-04-23T16:30:00Z"}
api_request("POST", f"/emails/activities/{activity_id}/schedules", data=schedule_payload)
print("✅ Campaign scheduled!")

# Save result
result = {
    "campaign_id": campaign_id,
    "activity_id": activity_id,
    "scheduled_time": "2026-04-23T16:30:00Z (10:30 AM MDT)",
    "subject": "It's been a while — a note from Dr. Lazarus",
    "list_id": "c2114ee0-fa84-11ea-82b3-d4ae527536d1"
}
with open("/home/ethan/.openclaw/workspace/projects/constant-contact/runs/2026-04-16/schedule_result.json", "w") as f:
    json.dump(result, f, indent=2)
print(f"✅ Result saved: {result}")
