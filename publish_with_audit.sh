#!/bin/bash
# OpenClaw 文章发布脚本（带强制审核）
# 使用: ./publish_with_audit.sh 文章路径.md

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <文章路径.md>"
    echo "示例: $0 /root/.openclaw/workspace/news/articles/20260226-测试.md"
    exit 1
fi

ARTICLE_PATH="$1"

# 检查文件是否存在
if [ ! -f "$ARTICLE_PATH" ]; then
    echo -e "${RED}❌ 错误: 文件不存在: $ARTICLE_PATH${NC}"
    exit 1
fi

echo "=========================================="
echo "📋 OpenClaw 文章发布流程"
echo "=========================================="
echo ""

# 步骤1: 审核检查
echo "🤖 步骤1: 启动审核机器人..."
echo "----------------------------------------"

if python3 /root/.openclaw/workspace/audit_bot.py "$ARTICLE_PATH"; then
    echo ""
    echo -e "${GREEN}✅ 审核通过！${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 审核未通过！${NC}"
    echo ""
    echo "请根据审核报告修复问题后重新提交。"
    echo "审核报告已保存。"
    exit 1
fi

# 步骤2: 人工确认
echo "----------------------------------------"
echo "👤 步骤2: 人工确认"
echo "----------------------------------------"
echo ""
echo "即将发布文章: $(basename "$ARTICLE_PATH")"
echo ""
echo "请确认以下检查已完成:"
echo "  [ ] 数据准确性已核实"
echo "  [ ] 格式规范已检查"
echo "  [ ] 敏感内容已排除"
echo ""

# 步骤3: 发布到公众号
echo "----------------------------------------"
echo "📤 步骤3: 发布到微信公众号"
echo "----------------------------------------"

# 获取配置
APPID="wx6a31a87c6438a8ea"
APPSECRET="e80f56dcf5210443031d25a6f3e46356"
THUMB_ID="bp5Z0WUrA0JL_mie2cUkSnZc9RBP88N1Hw8H5z_Yzh4KG1Z4toavxmgS0eCqkAP8"

# 获取标题（从文件名或文章内）
TITLE=$(grep "^# " "$ARTICLE_PATH" | head -1 | sed 's/^# //')
if [ -z "$TITLE" ]; then
    TITLE=$(basename "$ARTICLE_PATH" .md)
fi

echo "标题: $TITLE"
echo ""

# 转换HTML
HTML=$(pandoc "$ARTICLE_PATH" -f markdown -t html --wrap=none 2>/dev/null)

# 发布（使用Python）
python3 << EOF
import json
import urllib.request
import sys

APPID = "$APPID"
APPSECRET = "$APPSECRET"
THUMB_ID = "$THUMB_ID"

# 获取Token
token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
with urllib.request.urlopen(token_url) as resp:
    token_data = json.loads(resp.read().decode())
    token = token_data.get('access_token')

if not token:
    print("❌ 获取Token失败")
    sys.exit(1)

print("✅ Token获取成功")

# 构建payload
title = """$TITLE"""
content = """$HTML"""

payload = {
    "articles": [{
        "title": title,
        "content": f"<div style='font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;font-size:16px;line-height:1.8;color:#333;padding:0 10px;'>{content}</div>",
        "author": "硅基工具人",
        "thumb_media_id": THUMB_ID,
        "show_cover_pic": 1,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]
}

# 发布
draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(draft_url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        if result.get('media_id'):
            print(f"✅ 发布成功!")
            print(f"   Media ID: {result.get('media_id')[:30]}...")
        else:
            print(f"❌ 发布失败: {result}")
            sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 发布成功！${NC}"
    echo "=========================================="
    echo ""
    echo "文章已发布到微信公众号草稿箱"
    echo "请在公众号后台查看并正式发布"
    echo ""
else
    echo ""
    echo "=========================================="
    echo -e "${RED}❌ 发布失败${NC}"
    echo "=========================================="
    exit 1
fi
