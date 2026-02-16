# Workspace 文件结构说明

## 📁 目录结构

```
workspace/
├── 📁 trading/              # 交易与套利系统
│   └── polymarket_scanner.py    # Polymarket套利扫描器
│
├── 📁 content/              # 内容生产系统
│   ├── 📁 scripts/          # 内容生成脚本
│   │   ├── karpathy_digest.py   # Karpathy日报生成
│   │   ├── evolution_monitor.py # 进化监控系统
│   │   └── self_evolution.py    # 自我进化核心
│   └── 📁 daily/            # 日报归档
│       ├── 2026-02-13-daily.md
│       └── 2026-02-13-wechat.md
│
├── 📁 news/                 # 公众号文章
│   └── 📁 articles/         # 专业格式文章
│       ├── 20260213-01-deepseek-anniversary.md
│       ├── 20260213-02-zhipu-glm5.md
│       └── ... (共8篇)
│
├── 📁 memory/               # 记忆与日志
│   ├── 2026-02-12.md
│   ├── 2026-02-13.md
│   └── karpathy-digest-*.md
│
├── 📁 config/               # 配置文件
│   └── 📁 vpn/              # VPN配置
│       ├── clash-verge-config.yaml
│       └── vpn-config-backup.md
│
└── 📄 核心文件              # 保留在根目录
    ├── AGENTS.md            # 代理配置
    ├── SOUL.md              # 灵魂定义
    ├── IDENTITY.md          # 身份定义
    ├── USER.md              # 用户信息
    ├── TOOLS.md             # 工具配置
    ├── BOOTSTRAP.md         # 启动配置
    └── HEARTBEAT.md         # 心跳任务
```

## 🎯 使用指南

### 交易相关
- 所有交易脚本在 `trading/`
- 策略文件未来放在 `trading/strategies/`

### 内容生产
- 日报生成脚本在 `content/scripts/`
- 生成的日报归档在 `content/daily/`
- 公众号文章在 `news/articles/`

### 记忆与日志
- 每日记忆在 `memory/`
- 格式：YYYY-MM-DD.md

### 配置
- VPN配置在 `config/vpn/`
- 其他工具配置未来放 `config/`

## 🔄 自动化任务

- **早上8点**：自动生成日报 + 8篇公众号文章
- **持续运行**：Polymarket套利扫描器
- **每晚8点**：生成进化报告
