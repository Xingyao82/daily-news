#!/bin/bash
# OpenClaw 自动备份脚本

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE" || exit 1

# 忽略敏感/大文件
cat > .gitignore <<'IGNORE'
*.log
*.tmp
node_modules/
.vpn/
media/inbound/*
media/outbound/*
IGNORE

# 检查是否有变更
if git status --porcelain | grep -q '^'; then
    DATE=$(date '+%Y-%m-%d %H:%M:%S')
    git add -A
    git commit -m "Auto backup: $DATE" --quiet
    # 如果有 remote，推送
    git push origin main --quiet 2>/dev/null || true
    echo "[$(date '+%H:%M:%S')] Backup committed"
else
    echo "[$(date '+%H:%M:%S')] No changes"
fi
