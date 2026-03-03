#!/usr/bin/env python3
"""
Telegram Bot - sendMessageDraft 功能部署
支持流式消息发送，提升用户体验
"""

import requests
import json
import time
import sys
from typing import Optional, Dict, Any

# Telegram Bot Token (需要从用户获取)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

class TelegramDraftBot:
    """支持 sendMessageDraft 的 Telegram Bot"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def _post(self, method: str, data: Dict) -> Optional[Dict]:
        """发送 POST 请求到 Telegram API"""
        try:
            url = f"{self.base_url}/{method}"
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API 请求失败: {e}")
            return None
    
    def send_message_draft(self, chat_id: int, text: str, 
                          parse_mode: str = "Markdown",
                          disable_web_page_preview: bool = True) -> Optional[Dict]:
        """
        发送消息草稿（流式发送）
        
        Args:
            chat_id: 聊天ID
            text: 消息文本
            parse_mode: 解析模式 (Markdown/HTML)
            disable_web_page_preview: 禁用网页预览
        
        Returns:
            API 响应
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        return self._post("sendMessageDraft", data)
    
    def send_message(self, chat_id: int, text: str,
                    parse_mode: str = "Markdown") -> Optional[Dict]:
        """发送普通消息（对比用）"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        return self._post("sendMessage", data)
    
    def send_streaming_content(self, chat_id: int, content_generator):
        """
        流式发送长内容
        模拟 AI 生成内容的流式输出
        
        Args:
            chat_id: 聊天ID
            content_generator: 内容生成器（生成器函数）
        """
        print(f"🚀 开始流式发送内容到 chat_id: {chat_id}")
        
        buffer = ""
        chunk_size = 100  # 每100字符发送一次
        
        for chunk in content_generator():
            buffer += chunk
            
            # 当缓冲区达到阈值时发送
            if len(buffer) >= chunk_size:
                result = self.send_message_draft(chat_id, buffer)
                if result and result.get("ok"):
                    print(f"✅ 已发送 {len(buffer)} 字符")
                buffer = ""
                time.sleep(0.5)  # 避免请求过快
        
        # 发送剩余内容
        if buffer:
            result = self.send_message_draft(chat_id, buffer)
            if result and result.get("ok"):
                print(f"✅ 已发送最后 {len(buffer)} 字符")
        
        print("✅ 流式发送完成")
    
    def demo_streaming_article(self, chat_id: int):
        """
        演示：流式发送一篇AI生成的文章
        """
        def article_generator():
            """文章生成器，模拟AI逐步生成内容"""
            paragraphs = [
                "🔥 **今日头条：AI行业重大突破**\n\n",
                "据最新消息，人工智能领域迎来重大进展。",
                "多家科技巨头同时发布新一代大模型，",
                "在推理能力和多模态理解方面取得显著突破。\n\n",
                "📊 **关键数据：**\n",
                "• 推理速度提升 40%\n",
                "• 能耗降低 35%\n",
                "• 支持 200+ 种语言\n\n",
                "💡 **专家观点：**\n",
                "业界专家认为，这次突破将加速AI在各行业的落地应用，",
                "特别是在医疗诊断、自动驾驶和科学研究领域。",
                "预计2026年AI市场规模将达到5000亿美元。\n\n",
                "---\n",
                "*本文由AI自动生成，仅供参考*"
            ]
            
            for paragraph in paragraphs:
                for char in paragraph:
                    yield char
                    time.sleep(0.02)  # 模拟打字效果
        
        self.send_streaming_content(chat_id, article_generator)


def setup_webhook(bot_token: str, webhook_url: str) -> bool:
    """设置 Webhook"""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        if result.get("ok"):
            print(f"✅ Webhook 设置成功: {webhook_url}")
            return True
        else:
            print(f"❌ Webhook 设置失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def get_updates(bot_token: str, offset: int = 0) -> Optional[list]:
    """获取消息更新（polling 模式）"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {
        "offset": offset,
        "limit": 100,
        "timeout": 30
    }
    
    try:
        response = requests.get(url, params=params, timeout=35)
        result = response.json()
        if result.get("ok"):
            return result.get("result", [])
        return []
    except Exception as e:
        print(f"❌ 获取更新失败: {e}")
        return []


def main():
    """主函数 - 演示使用"""
    print("=" * 60)
    print("🤖 Telegram sendMessageDraft 部署工具")
    print("=" * 60)
    print()
    
    # 检查 Bot Token
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  请先设置 BOT_TOKEN!")
        print("步骤：")
        print("1. 在 Telegram 搜索 @BotFather")
        print("2. 创建新 Bot 或选择现有 Bot")
        print("3. 复制 Token 到脚本中的 BOT_TOKEN 变量")
        print()
        print("或者通过环境变量设置：")
        print("export TELEGRAM_BOT_TOKEN='your_token_here'")
        return
    
    bot = TelegramDraftBot(BOT_TOKEN)
    
    print("✅ Bot 初始化成功")
    print()
    
    # 演示模式选择
    print("选择模式：")
    print("1. 测试 sendMessageDraft (需要 chat_id)")
    print("2. 流式发送演示文章 (需要 chat_id)")
    print("3. Polling 模式运行 Bot")
    print()
    
    choice = input("输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        chat_id = input("输入 chat_id: ").strip()
        text = input("输入要发送的消息: ").strip()
        
        result = bot.send_message_draft(int(chat_id), text)
        if result:
            print(f"✅ 发送成功: {result}")
        else:
            print("❌ 发送失败")
    
    elif choice == "2":
        chat_id = input("输入 chat_id: ").strip()
        print("🚀 开始流式发送演示文章...")
        bot.demo_streaming_article(int(chat_id))
    
    elif choice == "3":
        print("🔄 启动 Polling 模式...")
        print("按 Ctrl+C 停止")
        print()
        
        offset = 0
        try:
            while True:
                updates = get_updates(BOT_TOKEN, offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        print(f"📩 收到消息: {text[:50]}...")
                        
                        # 回复流式内容
                        if text.startswith("/article"):
                            bot.demo_streaming_article(chat_id)
                        elif text.startswith("/draft"):
                            bot.send_message_draft(
                                chat_id, 
                                "📝 **Draft Message**\n\n这是一条测试草稿消息！"
                            )
                        else:
                            bot.send_message(
                                chat_id,
                                f"收到: {text}\n\n使用 /article 查看流式文章演示"
                            )
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n👋 Bot 已停止")
    
    else:
        print("❌ 无效选项")


if __name__ == "__main__":
    # 尝试从环境变量获取 Token
    import os
    env_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if env_token:
        BOT_TOKEN = env_token
    
    main()
