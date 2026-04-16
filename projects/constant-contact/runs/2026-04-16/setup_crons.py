#!/usr/bin/env python3
"""Add blog and research post crons + update LOCAL-SEO-PIPELINE.md"""
import json, subprocess, os

BLOG_MESSAGE = """You are running the weekly blog post workflow for Clinical Nutrition Center.

Run the blog post orchestrator: projects/blog-post/orchestrator.md

TOPIC: Pick a topic from projects/blog-post/LOCAL-SEO-PIPELINE.md — the highest priority post that hasn't been done yet this week.

Execute ALL steps in the orchestrator: Topic Generator (skip since selecting), Writer, SEO, Image, Editor, FAQ Schema, Media Upload, Article Upload, Notify, Log.

IMPORTANT REMINDERS:
- WordPress: https://www.clinicalnutritioncenter.com (with www)
- Post type: post (NOT research_update)
- Draft scheduled 7 days from today
- Email ethanlazarus@gmail.com when done
- Update master-log.json

Model: minimax/MiniMax-M2.7 for all steps except image (nano-banana).
"""

RESEARCH_MESSAGE = """You are running the weekly research post workflow for Clinical Nutrition Center.

Run the research post orchestrator: projects/research-post/orchestrator.md

Execute ALL steps in the orchestrator. Pick a trending clinical topic using the topic-selector and topic-researcher subagents.

IMPORTANT REMINDERS:
- WordPress: https://www.clinicalnutritioncenter.com (with www)  
- Post type: research_update (NOT post)
- Draft scheduled 7 days from today
- Email ethanlazarus@gmail.com when done
- Update topic_log.json

Model: minimax/MiniMax-M2.7 for all steps except writer (google/gemini-3.1-pro) and image (nano-banana).
"""

def add_cron(name, schedule_cron, message, model="minimax/MiniMax-M2.7"):
    cmd = [
        "openclaw", "cron", "add",
        "--name", name,
        "--cron", schedule_cron,
        "--tz", "America/Denver",
        "--session", "isolated",
        "--model", model,
        "--timeout-seconds", "600",
        "--message", message,
        "--no-deliver"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"✅ {name}: {result.stdout.strip()}")
    if result.stderr:
        print(f"   stderr: {result.stderr.strip()[:100]}")
    return result.stdout.strip()

# Add blog post cron (Monday 8 AM)
add_cron(
    "Weekly Blog Post (Local SEO)",
    "0 8 * * 1",
    BLOG_MESSAGE
)

# Add research post cron (Thursday 8 AM)
add_cron(
    "Weekly Research Post (Clinical)",
    "0 8 * * 4",
    RESEARCH_MESSAGE
)

print("\nDone setting up crons!")
