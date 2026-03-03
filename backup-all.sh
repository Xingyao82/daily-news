#!/bin/bash
# OpenClaw 完整备份脚本
# 备份所有配置，方便迁移到新 VPS

BACKUP_DIR="/root/openclaw-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "🚀 开始备份 OpenClaw 配置..."
echo "备份目录: $BACKUP_DIR"
echo ""

# 1. 备份 OpenClaw 配置
echo "[1/6] 备份 OpenClaw 配置..."
cp -r ~/.openclaw "$BACKUP_DIR/" 2>/dev/null || echo "⚠️ .openclaw 目录不存在"

# 2. 备份 Xray 配置
echo "[2/6] 备份 Xray 配置..."
cp /usr/local/etc/xray/config.json "$BACKUP_DIR/xray-config.json" 2>/dev/null

# 3. 备份 Cloudflare Tunnel
echo "[3/6] 备份 Cloudflare Tunnel..."
cp -r ~/.cloudflared "$BACKUP_DIR/" 2>/dev/null || echo "⚠️ cloudflared 未配置"

# 4. 备份定时任务
echo "[4/6] 备份定时任务..."
crontab -l > "$BACKUP_DIR/crontab.txt" 2>/dev/null || echo "⚠️ 无定时任务"

# 5. 备份系统服务
echo "[5/6] 备份系统服务..."
cp /etc/systemd/system/xray.service "$BACKUP_DIR/" 2>/dev/null
cp /etc/systemd/system/cloudflared.service "$BACKUP_DIR/" 2>/dev/null || true

# 6. 备份自定义脚本
echo "[6/6] 备份自定义脚本..."
mkdir -p "$BACKUP_DIR/workspace"
cp -r ~/.openclaw/workspace/*.sh "$BACKUP_DIR/workspace/" 2>/dev/null || true
cp ~/.openclaw/workspace/*.md "$BACKUP_DIR/workspace/" 2>/dev/null || true

# 打包
echo ""
echo "📦 打包备份..."
cd /root
tar -czvf "openclaw-backup-$(date +%Y%m%d).tar.gz" "$(basename $BACKUP_DIR)"

# 生成迁移指南
cat > "$BACKUP_DIR/迁移说明.txt" <> 'EOF'
=====================================
OpenClaw 迁移说明
=====================================

1. 在新 VPS 上安装 OpenClaw:
   npm install -g openclaw

2. 解压备份:
   tar -xzvf openclaw-backup-YYYYMMDD.tar.gz
   cd openclaw-backup-YYYYMMDD

3. 恢复配置:
   cp -r .openclaw ~/
   cp xray-config.json /usr/local/etc/xray/
   cp -r .cloudflared ~/

4. 安装 Xray:
   # 参考原安装步骤

5. 恢复定时任务:
   crontab crontab.txt

6. 恢复系统服务:
   cp xray.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable xray
   systemctl start xray

7. 更新 IP 地址:
   # 修改所有配置中的旧 IP (192.3.104.20) 为新 IP
   # 使用 sed 批量替换:
   sed -i 's/192.3.104.20/新IP/g' ~/.openclaw/workspace/*.md

8. 重启服务:
   systemctl restart xray
   openclaw gateway restart

=====================================
EOF

echo ""
echo "✅ 备份完成!"
echo "备份文件: /root/openclaw-backup-$(date +%Y%m%d).tar.gz"
echo ""
echo "📋 下一步:"
echo "1. 下载备份文件到本地"
echo "2. 联系 RackNerd 更换 IP，或购买新 VPS"
echo "3. 在新机器上运行迁移脚本"
