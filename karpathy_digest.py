#!/usr/bin/env python3
"""
Karpathy 精选 RSS 日报生成脚本
获取 Andrej Karpathy 的最新动态、博客和视频
"""

import requests
from datetime import datetime, timedelta
import re
import os
import json

def fetch_blog_posts():
    """通过直接请求获取 Karpathy 博客内容"""
    try:
        # Karpathy 博客主页
        url = "https://karpathy.ai/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text
        
        posts = []
        # 尝试从博客页面提取文章链接
        # Karpathy 的博客通常在主页列出文章
        article_pattern = r'href="([^"]*blog[^"]*)"[^>]*>([^<]+)</a>'
        matches = re.findall(article_pattern, html, re.IGNORECASE)
        
        seen = set()
        for link, title in matches[:5]:
            if link not in seen and title.strip():
                seen.add(link)
                # 确保完整URL
                if link.startswith('/'):
                    link = f"https://karpathy.ai{link}"
                elif not link.startswith('http'):
                    link = f"https://karpathy.ai/{link}"
                
                posts.append({
                    'title': title.strip(),
                    'link': link,
                    'summary': '',
                    'published': '',
                    'type': '博客'
                })
        
        return posts
    except Exception as e:
        return []

def fetch_github_activity():
    """获取 Karpathy GitHub 最近活动"""
    try:
        # Karpathy 的 GitHub 用户名是 karpathy
        url = "https://api.github.com/users/karpathy/events/public"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        events = response.json()
        
        activities = []
        yesterday = datetime.now() - timedelta(days=2)
        
        for event in events[:10]:
            event_time = event.get('created_at', '')
            if event_time:
                event_date = datetime.fromisoformat(event_time.replace('Z', '+00:00')).replace(tzinfo=None)
                if event_date > yesterday:
                    event_type = event.get('type', '')
                    repo = event.get('repo', {}).get('name', '')
                    
                    if event_type == 'PushEvent':
                        commits = event.get('payload', {}).get('commits', [])
                        if commits:
                            msg = commits[0].get('message', '')[:100]
                            activities.append({
                                'title': f"推送代码到 {repo}",
                                'link': f"https://github.com/{repo}",
                                'summary': f"最新提交: {msg}",
                                'published': event_date.strftime('%Y-%m-%d %H:%M'),
                                'type': 'GitHub'
                            })
                    elif event_type == 'CreateEvent':
                        ref_type = event.get('payload', {}).get('ref_type', '')
                        activities.append({
                            'title': f"创建{ref_type}: {repo}",
                            'link': f"https://github.com/{repo}",
                            'summary': '',
                            'published': event_date.strftime('%Y-%m-%d %H:%M'),
                            'type': 'GitHub'
                        })
        
        return activities[:5]
    except Exception as e:
        return []

def fetch_youtube_videos():
    """获取 Karpathy YouTube 视频 - 使用简单方法"""
    try:
        # YouTube 频道页面
        url = "https://www.youtube.com/@AndrejKarpathy/videos"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        videos = []
        html = response.text
        
        # 尝试提取视频信息 (YouTube 页面结构会变化，这里使用简单匹配)
        # 查找视频标题和ID
        video_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"([^"]+)"\}'
        matches = re.findall(video_pattern, html)
        
        seen = set()
        for video_id, title in matches[:3]:
            if video_id not in seen:
                seen.add(video_id)
                videos.append({
                    'title': title,
                    'link': f"https://youtube.com/watch?v={video_id}",
                    'summary': '',
                    'published': '近期',
                    'type': '视频'
                })
        
        return videos
    except Exception as e:
        return []

def get_karpathy_insights():
    """获取 Karpathy 的一些经典/重要内容推荐"""
    return [
        {
            'title': 'Let\'s build GPT: from scratch',
            'link': 'https://www.youtube.com/watch?v=kCc8FmEb1nY',
            'summary': '从头开始构建 GPT 模型的经典教程，深入浅出讲解 transformer 原理',
            'type': '精选视频'
        },
        {
            'title': 'Neural Networks: Zero to Hero',
            'link': 'https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ',
            'summary': '神经网络入门到精通系列，最受欢迎的教育课程之一',
            'type': '精选课程'
        },
        {
            'title': 'Tokenization - AI 背后的无声英雄',
            'link': 'https://www.youtube.com/watch?v=zduSFxRajkE',
            'summary': '深入讲解 Tokenization 原理，理解 GPT 如何处理文本',
            'type': '精选视频'
        },
        {
            'title': 'Karpathy 博客',
            'link': 'https://karpathy.ai/',
            'summary': 'Andrej Karpathy 的个人博客，包含大量深度技术文章',
            'type': '精选资源'
        }
    ]

def generate_digest():
    """生成日报"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # 获取各类内容
    blog_posts = fetch_blog_posts()
    github_activities = fetch_github_activity()
    youtube_videos = fetch_youtube_videos()
    insights = get_karpathy_insights()
    
    # 构建日报内容
    lines = []
    lines.append("=" * 60)
    lines.append(f"🧠 Karpathy 精选日报 - {today}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Andrej Karpathy - AI 研究员、教育家、前 Tesla AI 总监")
    lines.append("博客: https://karpathy.ai/ | GitHub: https://github.com/karpathy")
    lines.append("")
    
    # GitHub 动态
    if github_activities:
        lines.append("🔨 最新 GitHub 动态")
        lines.append("-" * 40)
        for activity in github_activities:
            lines.append(f"\n【{activity['type']}】{activity['title']}")
            if activity['published']:
                lines.append(f"📅 {activity['published']}")
            if activity['summary']:
                lines.append(f"📝 {activity['summary']}")
            if activity['link']:
                lines.append(f"🔗 {activity['link']}")
        lines.append("")
    
    # YouTube 视频
    if youtube_videos:
        lines.append("🎬 最新 YouTube 视频")
        lines.append("-" * 40)
        for video in youtube_videos:
            lines.append(f"\n【{video['type']}】{video['title']}")
            if video['published']:
                lines.append(f"📅 {video['published']}")
            if video['link']:
                lines.append(f"🔗 {video['link']}")
        lines.append("")
    
    # 博客文章
    if blog_posts:
        lines.append("📚 博客文章")
        lines.append("-" * 40)
        for post in blog_posts:
            lines.append(f"\n【{post['type']}】{post['title']}")
            if post['link']:
                lines.append(f"🔗 {post['link']}")
        lines.append("")
    
    # 精选内容（始终显示）
    lines.append("⭐ 精选推荐内容")
    lines.append("-" * 40)
    for item in insights:
        lines.append(f"\n【{item['type']}】{item['title']}")
        if item['summary']:
            lines.append(f"📝 {item['summary']}")
        if item['link']:
            lines.append(f"🔗 {item['link']}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("🦞 由三妹自动采集生成")
    lines.append("📅 每日更新，追踪 AI 大牛最新动态")
    lines.append("=" * 60)
    
    return "\n".join(lines)

if __name__ == "__main__":
    digest = generate_digest()
    print(digest)
    
    # 保存到文件
    output_dir = "/root/.openclaw/workspace/news"
    os.makedirs(output_dir, exist_ok=True)
    today_file = datetime.now().strftime('%Y%m%d')
    output_file = os.path.join(output_dir, f"{today_file}-karpathy-digest.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(digest)
    
    print(f"\n\n✅ 日报已保存到: {output_file}")
