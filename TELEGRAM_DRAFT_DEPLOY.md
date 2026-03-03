# Telegram sendMessageDraft 部署指南

## 🎯 功能概述

`sendMessageDraft` 是 Telegram Bot API 9.5 版本新增的功能，允许 bot **流式发送消息**。

### 核心特性
- ✅ **流式传输**：消息生成过程中逐步发送
- ✅ **实时反馈**：用户无需等待完整内容生成
- ✅ **打字机效果**：模拟 AI 实时生成内容
- ✅ **长内容优化**：适合发送长文章、报告

---

## 🚀 快速部署

### 步骤 1：获取 Bot Token

1. 在 Telegram 搜索 **@BotFather**
2. 发送 `/newbot` 创建新 bot
3. 按提示设置名称和用户名
4. 复制获得的 **Token**（格式：`123456:ABC-DEF...`）

### 步骤 2：配置环境

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN='your_bot_token_here'

# 或者编辑配置文件
nano /root/.openclaw/workspace/.env
telegram_bot_token=your_bot_token_here
```

### 步骤 3：运行 Bot

```bash
# 方式1：交互式测试
cd /root/.openclaw/workspace
python3 telegram_draft_bot.py

# 方式2：后台运行（Polling 模式）
nohup python3 telegram_draft_bot.py > /var/log/telegram_bot.log 2>&1 &
tail -f /var/log/telegram_bot.log
```

---

## 🔧 与 OpenClaw 集成

### 场景 1：自动发送日报

将日报自动发送到 Telegram：

```python
# 在 auto_publish.py 中添加
from telegram_draft_bot import TelegramDraftBot

bot = TelegramDraftBot(BOT_TOKEN)

# 发送日报到指定频道/群组
bot.send_streaming_content(
    chat_id=-1001234567890,  # 频道 ID
    content_generator=daily_report_generator
)
```

### 场景 2：AI 内容流式输出

用户提问 → AI 实时生成 → 流式发送：

```python
def ai_response_generator(user_query):
    """AI 逐步生成回复"""
    # 调用 AI API（如 OpenAI、Claude）
    # 使用流式响应
    for chunk in openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_query}],
        stream=True
    ):
        content = chunk.choices[0].delta.get("content", "")
        if content:
            yield content
```

### 场景 3：Webhook 模式（推荐生产环境）

```python
from flask import Flask, request

app = Flask(__name__)
bot = TelegramDraftBot(BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        
        # 流式发送 AI 回复
        bot.send_streaming_content(
            chat_id,
            lambda: ai_generate(text)
        )
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 📋 配置选项

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TELEGRAM_BOT_TOKEN` | Bot Token | ✅ |
| `TELEGRAM_WEBHOOK_URL` | Webhook URL（生产环境） | ❌ |
| `TELEGRAM_CHAT_ID` | 默认发送的聊天 ID | ❌ |
| `DRAFT_CHUNK_SIZE` | 流式分块大小（默认100字符） | ❌ |
| `DRAFT_DELAY` | 发送间隔（默认0.5秒） | ❌ |

### config.json 配置

```json
{
  "telegram": {
    "bot_token": "your_token_here",
    "webhook_url": "https://your-domain.com/webhook",
    "default_chat_id": -1001234567890,
    "draft_settings": {
      "chunk_size": 100,
      "delay": 0.5,
      "parse_mode": "Markdown"
    }
  }
}
```

---

## 🛡️ 安全建议

1. **保护 Token**
   - 不要硬编码在代码中
   - 使用环境变量或密钥管理服务
   - 定期轮换 Token

2. **Webhook 安全**
   - 使用 HTTPS
   - 设置 Secret Token
   - 验证请求来源

3. **Rate Limiting**
   - 遵守 Telegram API 限制（每秒30条消息）
   - 实现请求队列
   - 添加重试机制

---

## 🔍 故障排查

### 问题 1：无法发送消息
```
错误：Forbidden: bot was blocked by the user
解决：用户需要先向 bot 发送 /start
```

### 问题 2：API 调用失败
```
错误：429 Too Many Requests
解决：降低发送频率，添加延时
```

### 问题 3：Webhook 不工作
```
检查：
1. 服务器是否可从公网访问
2. 防火墙是否开放端口
3. URL 是否正确（需要 HTTPS）
```

---

## 📚 相关文档

- [Telegram Bot API 官方文档](https://core.telegram.org/bots/api#sendmessagedraft)
- [Webhook 设置指南](https://core.telegram.org/bots/webhooks)
- [Flask 部署文档](https://flask.palletsprojects.com/)

---

## ✅ 部署检查清单

- [ ] 获取 Bot Token
- [ ] 配置环境变量
- [ ] 测试 Polling 模式
- [ ] 测试 Webhook 模式（生产环境）
- [ ] 与 OpenClaw 集成
- [ ] 设置日志监控
- [ ] 配置告警机制

---

**部署完成！** 🎉

有问题随时联系 🦞 虾总
