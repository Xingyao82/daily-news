#!/usr/bin/env python3
"""
Karpathy 精选 RSS 日报生成器（纯标准库版本）
完全复制 YouMind 技能功能
"""

import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta
import json
import os
import xml.etree.ElementTree as ET

# 配置
RSS_PACK_URL = "https://youmind.com/rss/pack/andrej-karpathy-curated-rss"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "393431723")
MEMORY_DIR = "/root/.openclaw/workspace/memory"


def send_telegram_report(title, message):
    """发送 Telegram 报告"""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[{title}]\n{message}")
        return
    
    import urllib.request
    import urllib.parse
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # 如果消息太长，分段发送
    max_length = 4000
    
    if len(message) <= max_length:
        data = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"*{title}*\n\n{message}",
            "parse_mode": "Markdown",
            "disable_web_page_preview": "True"
        }).encode()
        
        try:
            req = urllib.request.Request(url, data=data, method='POST')
            urllib.request.urlopen(req, timeout=30)
        except Exception as e:
            print(f"发送失败: {e}")
    else:
        # 分段发送
        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        for i, part in enumerate(parts):
            part_title = f"{title} (Part {i+1}/{len(parts)})" if i > 0 else title
            data = urllib.parse.urlencode({
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"*{part_title}*\n\n{part}",
                "parse_mode": "Markdown",
                "disable_web_page_preview": "True"
            }).encode()
            
            try:
                req = urllib.request.Request(url, data=data, method='POST')
                urllib.request.urlopen(req, timeout=30)
            except Exception as e:
                print(f"发送失败: {e}")


def fetch_url(url):
    """获取 URL 内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"获取失败 {url}: {e}")
        return None


def parse_rss(xml_content):
    """解析 RSS Feed"""
    try:
        root = ET.fromstring(xml_content)
        
        # 处理 RSS 2.0 和 Atom 格式
        entries = []
        
        # RSS 2.0
        for item in root.findall('.//item'):
            entry = {
                'title': item.findtext('title', '无标题').strip(),
                'link': item.findtext('link', ''),
                'description': item.findtext('description', ''),
                'pubDate': item.findtext('pubDate', ''),
            }
            entries.append(entry)
        
        # Atom
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title = entry.findtext('{http://www.w3.org/2005/Atom}title', '无标题')
            link = entry.find('{http://www.w3.org/2005/Atom}link')
            href = link.get('href', '') if link is not None else ''
            summary = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')
            published = entry.findtext('{http://www.w3.org/2005/Atom}published', '')
            
            entries.append({
                'title': title.strip() if title else '无标题',
                'link': href,
                'description': summary,
                'pubDate': published
            })
        
        return entries
    except Exception as e:
        print(f"解析 RSS 失败: {e}")
        return []


def fetch_article_content(url):
    """获取文章内容"""
    html = fetch_url(url)
    if not html:
        return {
            "title": "获取失败",
            "content": "无法访问页面",
            "url": url
        }
    
    try:
        # 提取标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "无标题"
        title = re.sub(r'<[^>]+>', '', title)  # 移除 HTML 标签
        
        # 移除 script 和 style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # 提取段落
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
        
        article_text = ""
        for p in paragraphs[:5]:
            text = re.sub(r'<[^>]+>', ' ', p)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 50:
                article_text += text + "\n\n"
                if len(article_text) > 1000:
                    break
        
        if not article_text:
            article_text = "无法提取正文"
        
        return {
            "title": title[:200],
            "content": article_text[:1500],
            "url": url
        }
    except Exception as e:
        return {
            "title": "解析失败",
            "content": f"错误: {str(e)[:100]}",
            "url": url
        }


def group_by_topic(articles):
    """按主题分组"""
    topics = {}
    
    for article in articles:
        title = article.get('title', '')
        title_lower = title.lower()
        
        # 关键词匹配
        if any(word in title_lower for word in ['ai', 'llm', 'gpt', 'openai', 'claude', 'model']):
            topic = 'AI'
        elif any(word in title_lower for word in ['code', 'programming', 'developer', 'software', 'python']):
            topic = '编程'
        elif any(word in title_lower for word in ['learning', 'neural', 'pytorch', 'tensorflow', 'training']):
            topic = '深度学习'
        elif any(word in title_lower for word in ['startup', 'founder', 'business', 'company']):
            topic = '创业'
        elif any(word in title_lower for word in ['chip', 'gpu', 'hardware', 'semiconductor', 'nvidia']):
            topic = '硬件'
        elif any(word in title_lower for word in ['paper', 'research', 'arxiv', 'study', 'university']):
            topic = '研究'
        else:
            topic = '其他'
        
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(article)
    
    return topics


def generate_digest():
    """生成日报"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"[{datetime.now()}] 开始生成 Karpathy 精选 RSS 日报...")
    
    # 获取 RSS
    xml_content = fetch_url(RSS_PACK_URL)
    if not xml_content:
        print("获取 RSS 失败")
        return
    
    entries = parse_rss(xml_content)
    print(f"解析到 {len(entries)} 条 RSS 条目")
    
    if not entries:
        print("没有 RSS 条目")
        return
    
    # 只处理最近15条
    entries = entries[:15]
    
    # 获取每篇文章内容
    articles = []
    for i, entry in enumerate(entries):
        print(f"正在处理 {i+1}/{len(entries)}: {entry.get('title', 'Unknown')[:50]}...")
        url = entry.get('link', '')
        if url:
            content = fetch_article_content(url)
            # 使用 RSS 的标题如果获取失败
            if content['title'] in ['获取失败', '解析失败']:
                content['title'] = entry.get('title', '无标题')
            articles.append(content)
    
    if not articles:
        print("没有获取到文章内容")
        return
    
    # 按主题分组
    topics = group_by_topic(articles)
    
    # 生成报告
    total_count = len(articles)
    topic_count = len(topics)
    
    report = f"""> Andrej Karpathy 精选的信源资讯汇总 | 共 {total_count} 条更新
---
"""
    
    topic_emojis = {
        'AI': '🤖',
        '编程': '💻',
        '深度学习': '🧠',
        '创业': '🚀',
        '硬件': '⚙️',
        '研究': '📚',
        '其他': '📝'
    }
    
    for topic, items in topics.items():
        emoji = topic_emojis.get(topic, '📝')
        report += f"\n## {emoji} {topic}\n\n"
        
        for item in items[:2]:  # 每个主题最多2条
            title = item['title'][:80] + "..." if len(item['title']) > 80 else item['title']
            report += f"**{title}**\n"
            summary = item['content'][:150].replace('\n', ' ')
            report += f"> {summary}...\n"
            report += f"🔗 {item['url']}\n\n"
    
    topic_names = '、'.join(topics.keys())
    report += f"""---
## 📊 今日数据
- **{total_count}** 条 RSS 更新
- **{len(articles)}** 篇精选深度阅读  
- **{topic_count}** 个核心主题：{topic_names}
## 💡 编者观察

---
*本日报由 AI 自动生成 | 数据源：Andrej Karpathy curated RSS*
"""
    
    # 保存到文件
    os.makedirs(MEMORY_DIR, exist_ok=True)
    filename = f"{MEMORY_DIR}/karpathy-digest-{today}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"日报已保存: {filename}")
    
    # 发送 Telegram
    send_telegram_report(f"📚 Karpathy 精选 RSS 日报 - {today}", report)
    
    print("日报发送完成")


if __name__ == "__main__":
    generate_digest()
