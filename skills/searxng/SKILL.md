---
name: searxng
description: Search the web using a self-hosted SearXNG instance. Use when the user wants to search the web without relying on third-party APIs like Brave. Supports general search, images, videos, news, and more. Requires a running SearXNG instance accessible via HTTP.
---

# SearXNG Web Search

This skill provides web search capabilities via a self-hosted SearXNG instance.

## Prerequisites

1. A running SearXNG instance (deployed via Docker or other methods)
2. The instance must be accessible from the OpenClaw host
3. Default URL: `http://localhost:8888` (configurable)

## Quick Start

### Deploy SearXNG (Docker)

```bash
docker run -d --name searxng \
  -p 8888:8080 \
  -v searxng-data:/etc/searxng \
  --restart=always \
  searxng/searxng
```

### Search

Use the provided script:

```bash
python3 scripts/searxng_search.py "your search query"
```

## Usage Examples

### Basic Search
```bash
python3 scripts/searxng_search.py "OpenAI GPT-4"
```

### Custom Instance URL
```bash
python3 scripts/searxng_search.py "query" --url http://searxng.example.com
```

### Search Images
```bash
python3 scripts/searxng_search.py "cat pictures" --categories images
```

### Search News (Recent)
```bash
python3 scripts/searxng_search.py "tech news" --categories news --time-range week
```

### Chinese Language Results
```bash
python3 scripts/searxng_search.py "搜索关键词" --language zh-CN
```

### Markdown Output
```bash
python3 scripts/searxng_search.py "query" --format markdown
```

## API Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query | "hello world" |
| `categories` | Search categories | general, images, videos, news, music, it, science |
| `language` | Language code | en-US, zh-CN, ja-JP |
| `time_range` | Time filter | day, week, month, year |
| `safesearch` | Safe search | 0 (off), 1 (moderate), 2 (strict) |

## Response Format

JSON response includes:
- `results`: List of search results with title, url, content, engine
- `suggestions`: Query suggestions
- `answers`: Direct answers if available
- `infoboxes`: Information boxes

## Integration with OpenClaw

When using via OpenClaw's `exec` tool, prefer JSON output for programmatic handling:

```python
# Example: Using exec to search
exec command="python3 skills/searxng/scripts/searxng_search.py 'query' --format json"
```

## Troubleshooting

### Connection Refused
- Check if SearXNG is running: `docker ps | grep searxng`
- Verify the URL is correct
- Check if port 8888 is accessible

### No Results
- Try different search terms
- Check if search engines are configured in SearXNG
- Verify network connectivity from SearXNG container

### Rate Limiting
- SearXNG aggregates multiple engines; some may rate-limit
- Consider enabling more engines in SearXNG config
- Add delays between requests if needed

## Advanced Configuration

### Custom SearXNG Config

Edit `/etc/searxng/settings.yml` in the container to:
- Enable/disable search engines
- Set default language
- Configure privacy settings
- Add custom engines

### Multiple Instances

You can run multiple SearXNG instances for redundancy:
```bash
# Instance 1
docker run -d --name searxng-1 -p 8888:8080 searxng/searxng

# Instance 2  
docker run -d --name searxng-2 -p 8889:8080 searxng/searxng
```

Then specify which to use: `--url http://localhost:8888` or `--url http://localhost:8889`
