#!/usr/bin/env python3
"""
Tavily Search — Production Implementation
Uses Tavily AI Search API for comprehensive, research-grade web searches.
"""
import sys
import json
import os
from datetime import datetime, timedelta

try:
    from tavily import TavilyClient
except ImportError:
    print("ERROR: tavily-python not installed. Run: pip install tavily-python", file=sys.stderr)
    sys.exit(1)

# API key from openclaw.json skills config
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "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")

def search(query, freshness=None, depth="basic", max_results=10):
    """
    Run a Tavily search and return structured results.

    Args:
        query: Search query string
        freshness: None, "day", "week", "month", or "year" (prompts.py-style)
        depth: "basic" or "comprehensive" — comprehensive uses deeper retrieval
        max_results: Number of results (1-20)
    """
    client = TavilyClient(api_key=TAVILY_API_KEY)

    # Map freshness string to days
    freshness_days = {
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
    }

    search_kwargs = {
        "query": query,
        "depth": depth,
        "max_results": max_results,
    }

    if freshness in freshness_days:
        search_kwargs["days"] = freshness_days[freshness]

    try:
        response = client.search(**search_kwargs)
        return response
    except Exception as e:
        return {"error": str(e), "results": []}


def format_results(results, max_results=5):
    """Format Tavily results for readable output."""
    if "error" in results:
        return f"Error: {results['error']}"

    output = []
    for i, r in enumerate(results.get("results", [])[:max_results], 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "")
        score = r.get("score", "")

        output.append(f"[{i}] {title}")
        output.append(f"    URL: {url}")
        if content:
            # Truncate long snippets
            snippet = content[:300] + "..." if len(content) > 300 else content
            output.append(f"    Snippet: {snippet}")
        if score:
            output.append(f"    Relevance: {score:.3f}")
        output.append("")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: tavily_search.py '<query>' [--freshness day|week|month|year] [--depth basic|comprehensive] [--max-results N]", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]

    freshness = None
    depth = "basic"
    max_results = 10

    # Parse optional flags
    for arg in sys.argv[2:]:
        if arg == "--freshness" and len(sys.argv) > 2:
            freshness = sys.argv[sys.argv.index(arg) + 1]
        elif arg == "--depth" and len(sys.argv) > 2:
            depth = sys.argv[sys.argv.index(arg) + 1]
        elif arg == "--max-results" and len(sys.argv) > 2:
            max_results = int(sys.argv[sys.argv.index(arg) + 1])

    results = search(query, freshness=freshness, depth=depth, max_results=max_results)

    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results, max_results=max_results))


if __name__ == "__main__":
    main()
