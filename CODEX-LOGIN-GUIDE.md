# OpenClaw Codex 登录指南（VPS命令行版）

## 🎯 登录方式

不需要图形浏览器，用命令行 OAuth 设备码流程即可。

---

## 📋 登录步骤

### 1. 启动登录流程
```bash
openclaw models auth login --provider openai-codex
```

### 2. 复制设备码
终端会显示类似：
```
🦞 OpenAI Codex Login

1. 访问: https://auth.openai.com/device
2. 输入设备码: ABCD-EFGH
3. 登录你的 OpenAI 账号
4. 授权 OpenClaw 访问

Waiting for authorization...
```

### 3. 手机/电脑浏览器完成授权
- 用你的**手机**或**本地电脑**打开 https://auth.openai.com/device
- 输入设备码
- 登录 OpenAI 账号
- 点击"授权"

### 4. VPS自动获取Token
授权完成后，VPS终端会自动：
```
✅ Authorization successful
✅ Token saved to ~/.openclaw/auth/openai-codex.json
```

---

## ⚠️ 注意事项

### 关于 "Team 拼车"
- 如果账号是共享的，**多人同时登录可能会触发风控**
- OpenAI 可能会要求重新验证
- 建议错峰使用

### 网络要求
- VPS 需要能访问 OpenAI 域名
- 如果VPS在国内，可能需要代理

### Token有效期
- OAuth Token 通常有有效期（30-90天）
- 过期后需要重新登录

---

## 🔧 配置为默认模型

登录成功后，设置 Codex 为默认：
```bash
openclaw config set models.default "openai/codex"
# 或特定版本
openclaw config set models.default "openai/codex:latest"
```

---

## 🆘 故障排除

### 问题1: "Device flow not supported"
```bash
# 使用 paste-token 方式
openclaw models auth paste-token --provider openai-codex
# 然后粘贴你的 API Key
```

### 问题2: 网络超时
```bash
# 检查网络
ping auth.openai.com

# 如果无法访问，需要配置代理
export HTTPS_PROXY=http://your-proxy:port
openclaw models auth login --provider openai-codex
```

### 问题3: 账号被封
- Team 拼车账号风险较高
- 建议换个人账号或官方 API

---

## 💡 建议

如果只是为了省钱，还有这些选择：

| 方案 | 费用 | 稳定性 |
|------|------|--------|
| OpenAI Codex Official | $20/月 | ⭐⭐⭐⭐⭐ |
| GitHub Copilot Chat | $10/月 | ⭐⭐⭐⭐⭐ |
| Kimi K2.5 | ¥0-20/月 | ⭐⭐⭐⭐ |
| Claude API | $20/月 | ⭐⭐⭐⭐⭐ |
| Team 拼车 | ¥10/月 | ⭐⭐ |

对于 VPS 长期使用，**GitHub Copilot Chat** ($10/月) 性价比最高，且 OpenClaw 原生支持：
```bash
openclaw models auth login-github-copilot
```
