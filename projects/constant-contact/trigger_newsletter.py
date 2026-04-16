#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime

WORKSPACE = "/home/ethan/.openclaw/workspace"
PROJECT_DIR = f"{WORKSPACE}/projects/constant-contact"
LOG_FILE = f"{PROJECT_DIR}/cron.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def main():
    log("=" * 60)
    log("Starting Monthly Constant Contact Newsletter Workflow")
    log("=" * 60)
    
    cmd = [
        "/home/linuxbrew/.linuxbrew/bin/openclaw",
        "agent",
        "--agent", "content-creator",
        "--message",
        f"Please execute the newsletter workflow precisely as defined in {PROJECT_DIR}/orchestrator.md. This is an automated run."
    ]
    
    # Build clean cron-safe environment
    env = os.environ.copy()
    # Canonical PATH: includes opt/node/bin for openclaw, linuxbrew/bin for node
    env["PATH"] = f"/home/linuxbrew/.linuxbrew/opt/node/bin:/home/linuxbrew/.linuxbrew/bin:/usr/local/bin:/usr/bin:{env.get('PATH', '')}"
    # Explicitly load API keys (api_keys.env may not be in cron environment)
    api_keys_file = "/home/ethan/.openclaw/api_keys.env"
    if os.path.exists(api_keys_file):
        with open(api_keys_file) as kf:
            for line in kf:
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip('"')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        log("OpenClaw command finished.")
        if result.stdout:
            log(f"STDOUT:\n{result.stdout[:1000]}")
        if result.stderr:
            log(f"STDERR:\n{result.stderr[:1000]}")
    except Exception as e:
        log(f"Error executing OpenClaw: {str(e)}")
    
    log("Workflow Completed")
    log("=" * 60)

if __name__ == "__main__":
    main()