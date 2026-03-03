# OpenClaw 双机同步方案

## 🔄 同步脚本位置
`/root/.openclaw/workspace/sync-openclaw.sh`

## 📋 使用步骤

### 1. 首次设置
```bash
cd /root/.openclaw/workspace
./sync-openclaw.sh setup

# 按提示输入：
# - Mac mini IP 地址
# - Mac 用户名
```

### 2. 配置 SSH 免密登录
```bash
# 在 VPS 上查看公钥
cat ~/.ssh/id_rsa.pub

# 复制输出的内容，在 Mac mini 上执行：
mkdir -p ~/.ssh
echo '复制的公钥内容' >> ~/.ssh/authorized_keys
```

### 3. 测试同步
```bash
# VPS → Mac mini
./sync-openclaw.sh to-mac

# Mac mini → VPS
./sync-openclaw.sh from-mac

# 双向同步
./sync-openclaw.sh bidirectional
```

## 📦 同步内容

| 目录 | 说明 |
|------|------|
| `.openclaw/config` | 配置文件 |
| `.openclaw/workspace` | 工作区（代码、脚本） |
| `.openclaw/memory` | 记忆文件 |
| `.openclaw/wechat-config.json` | 微信配置 |
| `.openclaw/pexels-config.env` | Pexels API Key |
| `.cloudflared/` | VPN隧道配置 |

## ⏰ 自动同步（推荐）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每2小时同步一次）
0 */2 * * * /root/.openclaw/workspace/sync-openclaw.sh to-mac >> /var/log/openclaw-sync.log 2>&1
```

## 🏠 双机热备架构

```
┌─────────────┐         每2小时同步         ┌─────────────┐
│             │  ─────────────────────────►  │             │
│   VPS       │                              │   Mac mini  │
│  (主力)     │  ◄─────────────────────────  │  (备份)     │
│             │         手动回滚              │             │
└─────────────┘                              └─────────────┘
     │                                            │
     │ 24/7在线                                   │ 本地开发
     │ 定时任务                                   │ 测试环境
     │ 对外服务                                   │ 备用切换
```

## 💡 使用场景

### 场景1：日常同步（VPS → Mac）
```bash
# 每天自动同步，Mac作为备份
./sync-openclaw.sh to-mac
```

### 场景2：Mac开发后同步回VPS
```bash
# 在Mac上改完代码，同步到VPS
./sync-openclaw.sh from-mac
```

### 场景3：VPS故障，切换到Mac
```bash
# 1. 在Mac上启动 Gateway
openclaw gateway start

# 2. 所有设备重新配对到Mac IP
openclaw pair http://mac-mini-ip:18789
```

## ⚠️ 注意事项

1. **IP变化**：Mac mini 建议使用静态IP
2. **防火墙**：Mac 系统设置 → 安全性 → 允许 SSH
3. **冲突解决**：双向同步时，VPS文件优先
4. **大文件**：首次同步可能较慢，后续增量很快

## 🆘 故障恢复

如果 VPS 彻底挂了：
```bash
# 在 Mac mini 上
openclaw gateway start
# 所有配置都已同步，直接可用！
```
