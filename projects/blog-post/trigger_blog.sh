#!/usr/bin/env python3
"""
Trigger script for the Blog Post Workflow.
Designed to run via cron every Monday at 12:00 PM.
"""
import subprocess
import datetime
import os

LOG_FILE = "/home/ethan/.openclaw/workspace/projects/blog-post/cron.log"
WORKSPACE_DIR = "/home/ethan/.openclaw/workspace"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def main():
    log("=== Starting Weekly Blog Post Workflow ===")
    
    # Run the orchestrator subagent using the openclaw CLI
    cmd = [
        "/home/linuxbrew/.linuxbrew/bin/openclaw",
        "agent",
        "--agent", "content-creator",
        "-m", "Execute the blog post workflow defined in projects/blog-post/orchestrator.md. This is an automated run. Use anthropic/claude-haiku-4-5 for all steps."
    ]
    
    log(f"Executing: {' '.join(cmd)}")
    
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
        result = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True, env=env)
        log(f"OpenClaw exit code: {result.returncode}")
        
        # Log tail of output
        if result.stdout:
            log("STDOUT (last 10 lines):\n" + "\n".join(result.stdout.strip().split("\n")[-10:]))
        
        if result.stderr:
            log("STDERR:\n" + result.stderr)
            
    except Exception as e:
        log(f"Error launching process: {str(e)}")
    
    log("=== Workflow Execution Triggered ===")

if __name__ == "__main__":
    main()
