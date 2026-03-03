#!/bin/bash
# Telegram sendMessageDraft 快速测试脚本

echo "🚀 Telegram Draft Bot 快速测试"
echo "================================"
echo ""

# 检查 Token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ 未设置 TELEGRAM_BOT_TOKEN"
    echo ""
    echo "请设置环境变量："
    echo "export TELEGRAM_BOT_TOKEN='your_token_here'"
    echo ""
    echo "或者创建 .env 文件："
    echo "echo 'TELEGRAM_BOT_TOKEN=your_token' > .env"
    echo "source .env"
    exit 1
fi

echo "✅ Bot Token 已设置"
echo ""

# 检查 Python 依赖
echo "📦 检查依赖..."
python3 -c "import requests" 2>/dev/null || pip3 install requests -q

echo "✅ 依赖已安装"
echo ""

# 运行测试
echo "🧪 启动测试..."
echo ""
cd /root/.openclaw/workspace
python3 telegram_draft_bot.py
