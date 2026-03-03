#!/bin/bash
# OpenClaw 双机同步脚本
# 支持 VPS ↔ Mac mini 双向同步

set -e

# 配置
VPS_HOST="192.3.104.20"  # 当前VPS IP
VPS_USER="root"
MAC_HOST=""  # 需要填入Mac mini的IP
MAC_USER=""  # Mac用户名

# 同步目录
SYNC_DIRS=(
    ".openclaw/config"
    ".openclaw/workspace"
    ".openclaw/memory"
    ".openclaw/wechat-config.json"
    ".openclaw/pexels-config.env"
    ".cloudflared/"
)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} $1"
}

# 检查配置
check_config() {
    if [ -z "$MAC_HOST" ] || [ -z "$MAC_USER" ]; then
        error "请先编辑脚本，设置 MAC_HOST 和 MAC_USER"
        exit 1
    fi
}

# VPS → Mac 同步 (VPS为主)
sync_to_mac() {
    log "开始同步: VPS → Mac mini"
    
    for dir in "${SYNC_DIRS[@]}"; do
        local src="$HOME/$dir"
        if [ -e "$src" ]; then
            log "同步: $dir"
            rsync -avz --delete \
                -e "ssh -o StrictHostKeyChecking=no" \
                "$src" \
                "${MAC_USER}@${MAC_HOST}:~/$dir" 2>/dev/null || \
            warn "同步失败: $dir"
        fi
    done
    
    log "VPS → Mac 同步完成"
}

# Mac → VPS 同步 (Mac为主)
sync_from_mac() {
    log "开始同步: Mac mini → VPS"
    
    for dir in "${SYNC_DIRS[@]}"; do
        local dest="$HOME/$dir"
        log "同步: $dir"
        rsync -avz --delete \
            -e "ssh -o StrictHostKeyChecking=no" \
            "${MAC_USER}@${MAC_HOST}:~/$dir" \
            "$dest" 2>/dev/null || \
        warn "同步失败: $dir"
    done
    
    log "Mac → VPS 同步完成"
}

# 双向同步 (合并，有冲突时VPS优先)
sync_bidirectional() {
    log "开始双向同步..."
    
    # 先 VPS → Mac
    sync_to_mac
    
    # 再 Mac → VPS（只同步 Mac 有而 VPS 没有的文件）
    log "合并 Mac 独有文件..."
    for dir in "${SYNC_DIRS[@]}"; do
        rsync -avz \
            -e "ssh -o StrictHostKeyChecking=no" \
            "${MAC_USER}@${MAC_HOST}:~/$dir/" \
            "$HOME/$dir/" 2>/dev/null || true
    done
    
    log "双向同步完成"
}

# 显示帮助
show_help() {
    cat << EOF
OpenClaw 双机同步工具

用法:
  ./sync-openclaw.sh to-mac     # VPS → Mac mini
  ./sync-openclaw.sh from-mac   # Mac mini → VPS
  ./sync-openclaw.sh bidirectional  # 双向同步
  ./sync-openclaw.sh setup      # 首次设置

配置:
  编辑脚本设置 MAC_HOST 和 MAC_USER

示例:
  MAC_HOST="192.168.1.100"
  MAC_USER="xingyao"

定时同步:
  crontab -e
  # 每2小时同步一次
  0 */2 * * * /path/to/sync-openclaw.sh to-mac

EOF
}

# 首次设置
setup() {
    log "首次设置..."
    
    echo ""
    read -p "Mac mini IP 地址: " mac_ip
    read -p "Mac 用户名: " mac_user
    
    # 更新脚本
    sed -i "s/MAC_HOST=\"\"/MAC_HOST=\"$mac_ip\"/" "$0"
    sed -i "s/MAC_USER=\"\"/MAC_USER=\"$mac_user\"/" "$0"
    
    log "配置已保存"
    
    # 生成SSH密钥
    if [ ! -f ~/.ssh/id_rsa ]; then
        log "生成SSH密钥..."
        ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
    fi
    
    log "请将以下公钥添加到 Mac mini 的 ~/.ssh/authorized_keys:"
    cat ~/.ssh/id_rsa.pub
    echo ""
    log "在 Mac mini 上运行:"
    log "  mkdir -p ~/.ssh && echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys"
}

# 主程序
case "${1:-help}" in
    to-mac)
        check_config
        sync_to_mac
        ;;
    from-mac)
        check_config
        sync_from_mac
        ;;
    bidirectional|both)
        check_config
        sync_bidirectional
        ;;
    setup)
        setup
        ;;
    *)
        show_help
        ;;
esac
