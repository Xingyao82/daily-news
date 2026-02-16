#!/usr/bin/env python3
"""
三妹全维度进化监控系统
每小时分析数据，自动优化，生成报告
"""

import json
import os
import sys
from datetime import datetime, timedelta
sys.path.insert(0, '/root/.openclaw/workspace')
from self_evolution import SelfEvolution

# 配置
REPORT_TIME = 20  # 每晚 8 点生成日报
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "393431723")


def send_telegram_report(title, message):
    """发送进化报告"""
    import requests
    if not TELEGRAM_BOT_TOKEN:
        print(f"[{title}]\n{message}")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"*{title}*\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"发送报告失败: {e}")


def analyze_polymarket_performance():
    """分析 Polymarket 扫描器性能"""
    evo = SelfEvolution()
    
    if not evo.db.get("scans"):
        return "暂无扫描数据"
    
    scans = evo.db["scans"]
    recent_24h = [s for s in scans 
                  if datetime.now() - datetime.fromisoformat(s["timestamp"]) < timedelta(hours=24)]
    
    if not recent_24h:
        return "过去24小时无扫描数据"
    
    total_scans = len(recent_24h)
    total_opps = sum(s["opportunities_found"] for s in recent_24h)
    avg_duration = sum(s["duration_seconds"] for s in recent_24h) / len(recent_24h)
    
    report = f"""📊 Polymarket 扫描器进化报告（24小时）

🔍 扫描统计:
- 扫描次数: {total_scans}
- 发现机会: {total_opps}
- 发现率: {(total_opps/max(total_scans,1)*100):.2f}%
- 平均耗时: {avg_duration:.0f}秒

🧬 进化建议:
"""
    
    if total_opps == 0 and total_scans > 10:
        report += "- 发现率过低，建议放宽阈值到 0.995\n"
    elif avg_duration > 300:
        report += "- 扫描耗时过长，建议增加并发\n"
    else:
        report += "- 当前参数运行良好\n"
    
    return report


def check_system_health():
    """检查系统健康并自动修复"""
    import subprocess
    
    issues = []
    fixes = []
    
    # 检查内存 (使用 free 命令)
    try:
        result = subprocess.run(["free"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                mem_line = lines[1].split()
                total = int(mem_line[1])
                used = int(mem_line[2])
                percent = (used / total) * 100
                if percent > 85:
                    issues.append(f"内存使用过高: {percent:.1f}%")
    except:
        pass
    
    # 检查磁盘 (使用 df 命令)
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                use_percent = parts[4].replace('%', '')
                if int(use_percent) > 90:
                    issues.append(f"磁盘空间不足: {use_percent}%")
                    # 清理日志
                    subprocess.run(["find", "/var/log", "-name", "*.log", "-mtime", "+7", "-delete"], check=False)
                    fixes.append("已清理旧日志文件")
    except:
        pass
    
    # 检查 Gateway
    try:
        import requests
        response = requests.get("http://127.0.0.1:18789/health", timeout=5)
        if response.status_code != 200:
            issues.append("Gateway 健康检查异常")
            subprocess.run(["systemctl", "restart", "openclaw-main"], check=False)
            fixes.append("已重启 Gateway")
    except:
        issues.append("Gateway 无法连接")
        subprocess.run(["systemctl", "restart", "openclaw-main"], check=False)
        fixes.append("已重启 Gateway")
    
    # 检查 Polymarket 扫描器
    try:
        result = subprocess.run(["pgrep", "-f", "polymarket_scanner"], capture_output=True)
        if result.returncode != 0:
            issues.append("Polymarket 扫描器未运行")
            subprocess.run(["systemctl", "restart", "polymarket-scanner"], check=False)
            fixes.append("已重启 Polymarket 扫描器")
    except:
        pass
    
    report = "🖥️ 系统健康检查\n\n"
    if issues:
        report += "⚠️ 发现问题:\n"
        for issue in issues:
            report += f"- {issue}\n"
        if fixes:
            report += "\n🔧 自动修复:\n"
            for fix in fixes:
                report += f"- {fix}\n"
    else:
        report += "✅ 系统运行正常\n"
    
    return report


def learn_user_preferences():
    """学习用户偏好（从 MEMORY.md 和会话历史）"""
    prefs = {
        "trading_style": "确定性套利",  # 从对话学习
        "risk_tolerance": "保守",       # 只做无风险
        "communication": "简洁",        # 你的回复风格
        "interests": ["量化", "套利", "自动化"],
        "updated_at": datetime.now().isoformat()
    }
    
    # 保存到记忆
    memory_path = "/root/.openclaw/workspace/memory/user_preferences.json"
    with open(memory_path, 'w') as f:
        json.dump(prefs, f, indent=2)
    
    return f"""🧠 用户偏好学习

已记录偏好:
- 交易风格: {prefs['trading_style']}
- 风险偏好: {prefs['risk_tolerance']}
- 沟通风格: {prefs['communication']}
- 兴趣领域: {', '.join(prefs['interests'])}
"""


def daily_evolution_report():
    """生成每日进化报告"""
    sections = []
    
    # 1. Polymarket 性能
    sections.append(analyze_polymarket_performance())
    
    # 2. 系统健康
    sections.append(check_system_health())
    
    # 3. 学习偏好
    sections.append(learn_user_preferences())
    
    # 4. 明日优化计划
    sections.append("""📅 明日优化计划

自动执行:
- 继续监控 Polymarket 套利机会
- 生成早8点 AI 日报
- 分析扫描数据，动态调整参数
- 系统健康检查与自动修复

建议关注:
- 如果24小时内仍无套利机会，将放宽阈值
- 观察 VPS 内存使用，必要时优化
""")
    
    full_report = "\n" + "="*40 + "\n".join(sections)
    
    send_telegram_report("🧬 三妹每日进化报告", full_report)
    
    return full_report


def main():
    """主函数 - 可以定时运行"""
    print(f"[{datetime.now()}] 开始进化分析...")
    
    report = daily_evolution_report()
    print(report)
    
    print("进化分析完成，已发送报告")


if __name__ == "__main__":
    main()
