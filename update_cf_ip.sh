#!/bin/bash
# Cloudflare 优选 IP 自动更新脚本

CFST_DIR="/root/.openclaw/workspace"
RESULT_FILE="$CFST_DIR/cf_best_ip.txt"
LOG_FILE="/var/log/cf_ip_update.log"

# 运行测速
cd $CFST_DIR
./cfst -n 200 -t 4 -dn 5 -tl 200 -o $RESULT_FILE

# 获取最优 IP
BEST_IP=$(head -1 $RESULT_FILE | awk '{print $1}')
BEST_DELAY=$(head -1 $RESULT_FILE | awk '{print $2}')
BEST_SPEED=$(head -1 $RESULT_FILE | awk '{print $3}')

if [ -n "$BEST_IP" ]; then
    echo "[$(date)] 优选IP: $BEST_IP 延迟: ${BEST_DELAY}ms 速度: ${BEST_SPEED}KB/s" >> $LOG_FILE
    
    # 可以在这里添加更新 hosts 或 DNS 的命令
    # 例如：更新 Cloudflare DNS 记录
    
    echo "✅ 优选完成: $BEST_IP"
else
    echo "[$(date)] 优选失败" >> $LOG_FILE
    echo "❌ 优选失败"
fi
