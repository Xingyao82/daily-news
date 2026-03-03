#!/usr/bin/env python3
"""
Finnhub 数据获取脚本
使用 Finnhub API 获取实时股价和财务数据
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Finnhub API Key
FINNHUB_API_KEY = "d6ij1o9r01qm7dc7mhrgd6ij1o9r01qm7dc7mhs0"
BASE_URL = "https://finnhub.io/api/v1"

class FinnhubClient:
    """Finnhub API 客户端"""
    
    def __init__(self, api_key: str = FINNHUB_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "X-Finnhub-Token": api_key
        })
    
    def _get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送GET请求"""
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取实时股价
        
        Args:
            symbol: 股票代码 (如 'AAPL', 'NVDA')
        
        Returns:
            股价数据字典
        """
        data = self._get("quote", {"symbol": symbol})
        if not data:
            return None
        
        return {
            "symbol": symbol,
            "current_price": data.get("c"),  # 当前价格
            "change": data.get("d"),  # 价格变化
            "change_percent": data.get("dp"),  # 变化百分比
            "high": data.get("h"),  # 今日最高
            "low": data.get("l"),  # 今日最低
            "open": data.get("o"),  # 开盘价
            "previous_close": data.get("pc"),  # 昨日收盘价
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """获取公司信息"""
        return self._get("stock/profile2", {"symbol": symbol})
    
    def get_financials(self, symbol: str, freq: str = "annual") -> Optional[Dict]:
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
            freq: 频率 ('annual'年报, 'quarterly'季报)
        """
        return self._get("stock/financials-reported", {
            "symbol": symbol,
            "freq": freq
        })
    
    def get_earnings(self, symbol: str) -> Optional[List]:
        """获取财报日历"""
        return self._get("stock/earnings", {"symbol": symbol})
    
    def get_news(self, symbol: str, from_date: str, to_date: str) -> Optional[List]:
        """
        获取公司新闻
        
        Args:
            symbol: 股票代码
            from_date: 开始日期 (YYYY-MM-DD)
            to_date: 结束日期 (YYYY-MM-DD)
        """
        return self._get("company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
    
    def get_recommendation(self, symbol: str) -> Optional[List]:
        """获取分析师推荐"""
        return self._get("stock/recommendation", {"symbol": symbol})
    
    def get_price_target(self, symbol: str) -> Optional[Dict]:
        """获取目标价"""
        return self._get("stock/price-target", {"symbol": symbol})
    
    def get_peers(self, symbol: str) -> Optional[List]:
        """获取同行公司"""
        return self._get("stock/peers", {"symbol": symbol})


def format_stock_data(data: Dict) -> str:
    """格式化股票数据为Markdown"""
    if not data:
        return "❌ 无法获取数据"
    
    change_emoji = "📈" if data.get("change", 0) >= 0 else "📉"
    
    return f"""### {data['symbol']} 实时行情 {change_emoji}

| 指标 | 数值 |
|------|------|
| **当前价格** | ${data.get('current_price', 'N/A')} |
| **涨跌** | {data.get('change', 'N/A')} ({data.get('change_percent', 'N/A')}%) |
| **今日最高** | ${data.get('high', 'N/A')} |
| **今日最低** | ${data.get('low', 'N/A')} |
| **开盘价** | ${data.get('open', 'N/A')} |
| **昨收** | ${data.get('previous_close', 'N/A')} |

*更新时间: {data.get('timestamp', 'N/A')}*
"""


def main():
    """主函数 - 示例用法"""
    print("=" * 60)
    print("📊 Finnhub 数据获取工具")
    print("=" * 60)
    print()
    
    client = FinnhubClient()
    
    # 示例1: 获取NVIDIA股价
    print("1. 获取 NVIDIA 实时股价...")
    nvda = client.get_quote("NVDA")
    print(format_stock_data(nvda))
    print()
    
    # 示例2: 获取Apple股价
    print("2. 获取 Apple 实时股价...")
    aapl = client.get_quote("AAPL")
    print(format_stock_data(aapl))
    print()
    
    # 示例3: 获取Tesla股价
    print("3. 获取 Tesla 实时股价...")
    tsla = client.get_quote("TSLA")
    print(format_stock_data(tsla))
    print()
    
    # 示例4: 获取分析师推荐
    print("4. 获取 NVIDIA 分析师推荐...")
    rec = client.get_recommendation("NVDA")
    if rec:
        latest = rec[0] if rec else None
        if latest:
            print(f"周期: {latest.get('period')}")
            print(f"买入: {latest.get('buy')} | 持有: {latest.get('hold')} | 卖出: {latest.get('sell')}")
    print()
    
    # 示例5: 批量获取
    print("5. 批量获取科技巨头股价...")
    tech_stocks = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    results = []
    
    for symbol in tech_stocks:
        data = client.get_quote(symbol)
        if data:
            results.append({
                "symbol": symbol,
                "price": data.get("current_price"),
                "change": data.get("change_percent")
            })
        time.sleep(0.5)  # 避免请求过快
    
    print("\n| 股票 | 价格 | 涨跌 |")
    print("|------|------|------|")
    for r in results:
        change_str = f"{r['change']:.2f}%" if r['change'] else "N/A"
        print(f"| {r['symbol']} | ${r['price']} | {change_str} |")
    
    print()
    print("=" * 60)
    print("✅ 数据获取完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
