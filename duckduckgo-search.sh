#!/bin/bash
# DuckDuckGo 搜索脚本 - 绕过 Brave API 限制
# 用法: ./duckduckgo-search.sh "搜索关键词"

QUERY="$1"
if [ -z "$QUERY" ]; then
    echo "用法: $0 \"搜索关键词\""
    exit 1
fi

echo "🔍 DuckDuckGo 搜索: $QUERY"
echo ""

# 使用 duckduckgo 的 html 版本（无需 API Key）
curl -s "https://html.duckduckgo.com/html/?q=$(echo $QUERY | sed 's/ /+/g')" \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    | grep -oP '(?<=<a rel="nofollow" class="result__a" href=")[^"]*' \
    | head -10

# 或者用文本模式
echo ""
echo "📄 搜索结果摘要:"
curl -s "https://html.duckduckgo.com/html/?q=$(echo $QUERY | sed 's/ /+/g')" \
    -A "Mozilla/5.0" \
    | grep -oP '(?<=<a class="result__snippet">)[^<]+' \
    | head -5
