#!/usr/bin/env python3
"""
SearXNG Search CLI

Usage:
  python searxng_search.py "search query" [--url http://localhost:8888] [--format json|markdown]
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import Dict, List, Any, Optional


def search(
    query: str,
    base_url: str = "http://localhost:8888",
    categories: Optional[str] = None,
    language: Optional[str] = None,
    time_range: Optional[str] = None,
    safesearch: int = 0,
    format: str = "json"
) -> Dict[str, Any]:
    """
    Perform a search via SearXNG API.
    
    Args:
        query: Search query string
        base_url: SearXNG instance URL
        categories: Comma-separated categories (general, images, videos, news, etc.)
        language: Language code (e.g., en-US, zh-CN)
        time_range: Time range filter (day, week, month, year)
        safesearch: Safe search level (0=off, 1=moderate, 2=strict)
        format: Response format (json or markdown)
    
    Returns:
        Search results as dict
    """
    params = {
        "q": query,
        "format": "json"
    }
    
    if categories:
        params["categories"] = categories
    if language:
        params["language"] = language
    if time_range:
        params["time_range"] = time_range
    if safesearch:
        params["safesearch"] = safesearch
    
    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "OpenClaw-SearXNG-Skill/1.0",
            "Accept": "application/json"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if format == "markdown":
                return format_as_markdown(data, query)
            return data
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {
            "error": f"HTTP {e.code}: {e.reason}",
            "details": error_body
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def format_as_markdown(data: Dict[str, Any], query: str) -> str:
    """Format search results as markdown."""
    if "error" in data:
        return f"# Search Error\n\n{data['error']}"
    
    results = data.get("results", [])
    if not results:
        return f"# No Results\n\nQuery: `{query}`"
    
    lines = [f"# Search Results: {query}\n"]
    
    for i, r in enumerate(results[:10], 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "").strip()
        engine = r.get("engine", "unknown")
        
        lines.append(f"### {i}. {title}")
        lines.append(f"**Source:** {engine}")
        lines.append(f"**URL:** {url}")
        if content:
            lines.append(f"\n{content}")
        lines.append("")
    
    # Add suggestions if available
    suggestions = data.get("suggestions", [])
    if suggestions:
        lines.append("---")
        lines.append("\n**Suggestions:** " + ", ".join([f"`{s}`" for s in suggestions[:5]]))
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SearXNG Search CLI")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--url", default="http://localhost:8888", help="SearXNG instance URL")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--categories", help="Categories (general, images, videos, news, etc.)")
    parser.add_argument("--language", help="Language code (e.g., en-US, zh-CN)")
    parser.add_argument("--time-range", choices=["day", "week", "month", "year"], help="Time range filter")
    parser.add_argument("--safesearch", type=int, choices=[0, 1, 2], default=0, help="Safe search level")
    
    args = parser.parse_args()
    
    result = search(
        query=args.query,
        base_url=args.url,
        categories=args.categories,
        language=args.language,
        time_range=args.time_range,
        safesearch=args.safesearch,
        format=args.format
    )
    
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result)


if __name__ == "__main__":
    main()
