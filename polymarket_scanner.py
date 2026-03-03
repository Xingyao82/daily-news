#!/usr/bin/env python3
"""
Polymarket Complete Set 套利扫描器
监控所有市场，找所有选项价格总和 < $0.99 的套利机会
"""

import requests
import json
import time
from datetime import datetime
import os
import sys
sys.path.insert(0, '/root/.openclaw/workspace')
from self_evolution import SelfEvolution

# 配置
POLYMARKET_API = "https://clob.polymarket.com"
THRESHOLD = 0.99  # 价格总和阈值（留1%安全边际）
MIN_VOLUME = 1000  # 最小交易量（确保能成交）
CHECK_INTERVAL = 300  # 检查间隔（秒）

# Telegram 配置（从环境变量读取）
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "393431723")


def send_telegram_alert(message):
    """发送 Telegram 提醒"""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[ALERT] {message}")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"发送 Telegram 失败: {e}")


def get_markets():
    """获取所有活跃市场"""
    markets = []
    next_cursor = None
    
    while True:
        url = f"{POLYMARKET_API}/markets"
        params = {"active": True, "limit": 100}
        if next_cursor:
            params["next_cursor"] = next_cursor
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            markets.extend(data.get("data", []))
            next_cursor = data.get("next_cursor")
            
            if not next_cursor:
                break
                
        except Exception as e:
            print(f"获取市场失败: {e}")
            break
    
    return markets


def get_orderbook(market_id):
    """获取市场订单簿，计算最佳买价"""
    url = f"{POLYMARKET_API}/book"
    params = {"market": market_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 买单最高价 = 你能卖出的价格
        # 卖单最低价 = 你能买入的价格
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        if not asks:
            return None
        
        # 最佳买价（最低卖单价）
        best_ask = float(asks[0]["price"])
        return best_ask
        
    except Exception as e:
        return None


def check_arbitrage_opportunity(market):
    """检查单个市场是否有套利机会"""
    market_id = market.get("market_slug") or market.get("condition_id")
    title = market.get("question", "Unknown")
    volume = float(market.get("volume", 0))
    
    # 交易量太小，跳过
    if volume < MIN_VOLUME:
        return None
    
    # 获取所有 outcomes
    outcomes = market.get("outcomes", [])
    if len(outcomes) < 2:
        return None
    
    # 获取每个选项的最佳买价
    total_price = 0
    outcome_prices = []
    
    for outcome in outcomes:
        outcome_id = outcome.get("id")
        outcome_name = outcome.get("name", "Unknown")
        
        # 构建市场 ID（outcome 格式）
        token_id = outcome.get("token_id")
        if not token_id:
            continue
        
        price = get_orderbook(token_id)
        if price is None:
            return None  # 无法获取价格，跳过
        
        total_price += price
        outcome_prices.append({
            "name": outcome_name,
            "price": price
        })
    
    # 检查是否满足套利条件
    if total_price < THRESHOLD:
        profit = 1 - total_price
        profit_pct = (profit / total_price) * 100
        
        return {
            "market_id": market_id,
            "title": title,
            "total_price": total_price,
            "profit": profit,
            "profit_pct": profit_pct,
            "volume": volume,
            "outcomes": outcome_prices,
            "url": f"https://polymarket.com/event/{market.get('market_slug', '')}"
        }
    
    return None


def format_alert(opportunity):
    """格式化套利提醒"""
    msg = f"""
🎯 *Complete Set 套利机会！*

📌 *{opportunity['title']}*

💰 *价格总和:* ${opportunity['total_price']:.4f}
📈 *利润:* ${opportunity['profit']:.4f} ({opportunity['profit_pct']:.2f}%)
📊 *交易量:* ${opportunity['volume']:,.0f}

📝 *各选项价格:*
"""
    for outcome in opportunity['outcomes']:
        msg += f"• {outcome['name']}: ${outcome['price']:.4f}\n"
    
    msg += f"\n🔗 [打开 Polymarket]({opportunity['url']})"
    
    return msg


def scan_for_arbitrage():
    """主扫描函数"""
    import time
    start_time = time.time()
    
    print(f"[{datetime.now()}] 开始扫描套利机会...")
    
    markets = get_markets()
    print(f"获取到 {len(markets)} 个活跃市场")
    
    opportunities = []
    
    for i, market in enumerate(markets):
        if i % 10 == 0:
            print(f"已检查 {i}/{len(markets)} 个市场...")
        
        # 限制 API 频率
        time.sleep(0.5)
        
        opp = check_arbitrage_opportunity(market)
        if opp:
            opportunities.append(opp)
            print(f"发现套利机会: {opp['title']} (利润: {opp['profit_pct']:.2f}%)")
    
    # 发送提醒
    if opportunities:
        for opp in opportunities:
            alert_msg = format_alert(opp)
            send_telegram_alert(alert_msg)
        print(f"发送了 {len(opportunities)} 个套利提醒")
    else:
        print("未发现套利机会")
    
    # 记录到进化系统
    duration = time.time() - start_time
    try:
        evo = SelfEvolution()
        evo.record_scan_result(len(markets), len(opportunities), duration)
    except Exception as e:
        print(f"进化系统记录失败: {e}")
    
    return opportunities


def main():
    """主循环"""
    print("=" * 50)
    print("Polymarket Complete Set 套利扫描器")
    print(f"阈值: < ${THRESHOLD}")
    print(f"最小交易量: ${MIN_VOLUME}")
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("=" * 50)
    
    while True:
        try:
            scan_for_arbitrage()
            print(f"等待 {CHECK_INTERVAL} 秒后下次扫描...\n")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n用户停止扫描")
            break
        except Exception as e:
            print(f"扫描出错: {e}")
            time.sleep(60)  # 出错后等待1分钟重试


if __name__ == "__main__":
    main()
