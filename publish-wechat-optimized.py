#!/usr/bin/env python3
"""
微信公众号文章发布脚本 - 优化排版版
"""
import json
import urllib.request
import subprocess
import sys

# 微信公众号配置
APPID = "wx6a31a87c6438a8ea"
APPSECRET = "e80f56dcf5210443031d25a6f3e46356"
THUMB_ID = "bp5Z0WUrA0JL_mie2cUkSnZc9RBP88N1Hw8H5z_Yzh4KG1Z4toavxmgS0eCqkAP8"

def get_access_token():
    """获取微信 Access Token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
        return data.get('access_token')

def delete_all_drafts(token):
    """删除所有草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    payload = json.dumps({"offset": 0, "count": 20, "no_content": 1}).encode()
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        items = data.get('item', [])
        
    for item in items:
        media_id = item.get('media_id')
        if media_id:
            del_url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
            del_payload = json.dumps({"media_id": media_id}).encode()
            del_req = urllib.request.Request(del_url, data=del_payload, headers={'Content-Type': 'application/json'})
            try:
                urllib.request.urlopen(del_req)
                print(f"已删除草稿: {media_id[:20]}...")
            except:
                pass

def markdown_to_html(file_path):
    """Markdown 转 HTML，并优化微信排版"""
    # 使用 pandoc 转换
    result = subprocess.run(
        ['pandoc', file_path, '-f', 'markdown', '-t', 'html', '--wrap=none'],
        capture_output=True, text=True
    )
    html = result.stdout
    
    # 微信优化样式
    container_style = """
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 16px;
        line-height: 1.8;
        color: #333;
        max-width: 100%;
        padding: 0 10px;
    """
    
    h1_style = """
        font-size: 22px;
        font-weight: bold;
        color: #1a1a1a;
        margin: 28px 0 18px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #07c160;
    """
    
    h2_style = """
        font-size: 18px;
        font-weight: bold;
        color: #2c2c2c;
        margin: 24px 0 14px 0;
        padding-left: 14px;
        border-left: 4px solid #07c160;
    """
    
    h3_style = """
        font-size: 16px;
        font-weight: bold;
        color: #444;
        margin: 18px 0 10px 0;
    """
    
    p_style = """
        margin: 14px 0;
        text-align: justify;
        text-indent: 0;
    """
    
    strong_style = """
        color: #07c160;
        font-weight: bold;
    """
    
    blockquote_style = """
        margin: 18px 0;
        padding: 14px 18px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #07c160;
        color: #555;
        border-radius: 0 8px 8px 0;
    """
    
    table_style = """
        width: 100%;
        border-collapse: collapse;
        margin: 18px 0;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    """
    
    th_style = """
        background: linear-gradient(135deg, #07c160 0%, #05a050 100%);
        color: white;
        padding: 12px 14px;
        text-align: left;
        font-weight: bold;
        border: 1px solid #06b050;
    """
    
    td_style = """
        padding: 10px 14px;
        border: 1px solid #e0e0e0;
        background: #fff;
    """
    
    li_style = """
        margin: 8px 0;
        line-height: 1.8;
    """
    
    # 添加容器
    html = f'<div style="{container_style}">{html}</div>'
    
    # 替换样式
    html = html.replace('<h1', f'<h1 style="{h1_style}"')
    html = html.replace('<h2', f'<h2 style="{h2_style}"')
    html = html.replace('<h3', f'<h3 style="{h3_style}"')
    html = html.replace('<p>', f'<p style="{p_style}">')
    html = html.replace('<strong>', f'<strong style="{strong_style}">')
    html = html.replace('<blockquote>', f'<blockquote style="{blockquote_style}">')
    html = html.replace('<table>', f'<table style="{table_style}">')
    html = html.replace('<th>', f'<th style="{th_style}">')
    html = html.replace('<td>', f'<td style="{td_style}">')
    html = html.replace('<li>', f'<li style="{li_style}">')
    
    # 优化分隔线
    html = html.replace('<hr />', '<div style="margin: 24px 0; height: 1px; background: linear-gradient(90deg, transparent, #ddd, transparent);"></div>')
    
    return html

def publish_article(token, file_path, title, index, total):
    """发布单篇文章"""
    print(f"\n[{index}/{total}] 正在发布: {title}")
    
    # 转换 HTML
    content = markdown_to_html(file_path)
    
    # 构建 payload
    payload = {
        "articles": [{
            "title": title,
            "content": content,
            "author": "硅基工具人",
            "thumb_media_id": THUMB_ID,
            "show_cover_pic": 1,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    
    # 发布
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get('errcode') == 0:
                print(f"✅ 发布成功! Media ID: {result.get('media_id', '')[:30]}...")
                return True
            else:
                print(f"❌ 发布失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    # 文章列表
    articles = [
        ("20260224-01-openai-hardware.md", "OpenAI硬件战略深度解析：200人团队打造AI设备生态"),
        ("20260224-03-lecun-world-model.md", "LeCun离职创业：世界模型实验室估值50亿美元"),
        ("20260224-04-sanders-ai-warning.md", "Bernie Sanders警告：AI革命速度超乎想象"),
        ("20260224-05-weill-cornell-aim.md", "AI医疗新突破：Weill Cornell启动2亿美元AIM项目"),
        ("20260224-07-ai-investment-rationality.md", "AI投资去泡沫化：从炒作走向务实"),
        ("20260224-08-ai-election-2026.md", "AI与2026年中期选举：深度伪造与个性化宣传"),
    ]
    
    print("=" * 50)
    print("微信公众号文章发布 - 优化排版版")
    print("=" * 50)
    
    # 获取 Token
    print("\n1. 获取 Access Token...")
    token = get_access_token()
    if not token:
        print("❌ 获取 Token 失败")
        sys.exit(1)
    print("✅ Token 获取成功")
    
    # 删除旧草稿
    print("\n2. 清理旧草稿...")
    delete_all_drafts(token)
    print("✅ 草稿清理完成")
    
    # 发布文章
    print("\n3. 发布文章（优化排版）...")
    success_count = 0
    for i, (file, title) in enumerate(articles, 1):
        if publish_article(token, file, title, i, len(articles)):
            success_count += 1
    
    # 总结
    print("\n" + "=" * 50)
    print(f"发布完成: {success_count}/{len(articles)} 篇成功")
    print("请登录公众号后台查看草稿箱")
    print("=" * 50)

if __name__ == "__main__":
    main()
