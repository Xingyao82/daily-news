#!/usr/bin/env python3
"""
Yahoo Finance 数据获取脚本
用于获取准确的股价和财务数据，确保文章数据准确性
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

def get_stock_data(ticker, period="1d"):
    """
    获取股票数据
    
    Args:
        ticker: 股票代码 (如 'NVDA', 'AAPL', 'MSFT')
        period: 时间周期 ('1d', '5d', '1mo', '3mo', '1y')
    
    Returns:
        dict: 股票数据字典
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 获取历史价格
        hist = stock.history(period=period)
        
        # 获取基本信息
        info = stock.info
        
        # 获取财务报表
        try:
            quarterly_financials = stock.quarterly_financials
            quarterly_earnings = stock.quarterly_earnings
        except:
            quarterly_financials = None
            quarterly_earnings = None
        
        data = {
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
            'previous_close': info.get('previousClose'),
            'open_price': info.get('open'),
            'day_high': info.get('dayHigh'),
            'day_low': info.get('dayLow'),
            '52_week_high': info.get('fiftyTwoWeekHigh'),
            '52_week_low': info.get('fiftyTwoWeekLow'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'peg_ratio': info.get('pegRatio'),
            'dividend_yield': info.get('dividendYield'),
            'ex_dividend_date': info.get('exDividendDate'),
            'target_high_price': info.get('targetHighPrice'),
            'target_low_price': info.get('targetLowPrice'),
            'target_mean_price': info.get('targetMeanPrice'),
            'recommendation': info.get('recommendationKey'),
            'number_of_analysts': info.get('numberOfAnalystOpinions'),
            'profit_margins': info.get('profitMargins'),
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'return_on_equity': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'current_ratio': info.get('currentRatio'),
            'quick_ratio': info.get('quickRatio'),
            'beta': info.get('beta'),
            'volume': info.get('volume'),
            'average_volume': info.get('averageVolume'),
            'shares_outstanding': info.get('sharesOutstanding'),
            'float_shares': info.get('floatShares'),
            'short_ratio': info.get('shortRatio'),
            'history': hist.to_dict() if not hist.empty else None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return data
    
    except Exception as e:
        return {'error': str(e), 'ticker': ticker}


def get_earnings_data(ticker):
    """
    获取 earnings 数据（准确财务数据）
    
    Args:
        ticker: 股票代码
    
    Returns:
        dict: 最新季度财务数据
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 获取季度收益
        earnings = stock.quarterly_earnings
        if earnings is not None and not earnings.empty:
            latest_quarter = earnings.index[0]
            latest_data = earnings.iloc[0]
            
            return {
                'ticker': ticker,
                'quarter': str(latest_quarter),
                'revenue': latest_data.get('Revenue') if 'Revenue' in latest_data else None,
                'earnings': latest_data.get('Earnings') if 'Earnings' in latest_data else None,
                'eps': latest_data.get('Earnings') / stock.info.get('sharesOutstanding') if 'Earnings' in latest_data and stock.info.get('sharesOutstanding') else None,
                'all_quarters': earnings.to_dict(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {'error': 'No earnings data available', 'ticker': ticker}
    
    except Exception as e:
        return {'error': str(e), 'ticker': ticker}


def get_multiple_stocks(tickers):
    """
    批量获取多只股票数据
    
    Args:
        tickers: 股票代码列表 (如 ['NVDA', 'AAPL', 'MSFT'])
    
    Returns:
        dict: 多只股票数据
    """
    results = {}
    for ticker in tickers:
        print(f"获取 {ticker} 数据...")
        results[ticker] = get_stock_data(ticker)
    return results


def format_for_article(data):
    """
    将数据格式化为文章可用的格式
    
    Args:
        data: 股票数据字典
    
    Returns:
        str: 格式化后的Markdown文本
    """
    if 'error' in data:
        return f"**数据获取错误**: {data['error']}"
    
    ticker = data.get('ticker', 'N/A')
    name = data.get('company_name', ticker)
    price = data.get('current_price', 'N/A')
    prev_close = data.get('previous_close', 'N/A')
    
    # 计算涨跌幅
    if price != 'N/A' and prev_close != 'N/A' and prev_close != 0:
        change = price - prev_close
        change_pct = (change / prev_close) * 100
        change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
    else:
        change_str = "N/A"
    
    market_cap = data.get('market_cap')
    if market_cap:
        if market_cap >= 1e12:
            market_cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            market_cap_str = f"${market_cap/1e9:.2f}B"
        else:
            market_cap_str = f"${market_cap:,.0f}"
    else:
        market_cap_str = "N/A"
    
    result = f"""### {name} ({ticker})

| 指标 | 数据 |
|------|------|
| **当前股价** | ${price:.2f} |
| **涨跌** | {change_str} |
| **市值** | {market_cap_str} |
| **市盈率(TTM)** | {data.get('pe_ratio', 'N/A')} |
| **远期市盈率** | {data.get('forward_pe', 'N/A')} |
| **52周最高** | ${data.get('52_week_high', 'N/A')} |
| **52周最低** | ${data.get('52_week_low', 'N/A')} |
| **分析师目标价** | ${data.get('target_mean_price', 'N/A')} |
| **推荐评级** | {data.get('recommendation', 'N/A')} |

*数据更新时间: {data.get('last_updated', 'N/A')}*
"""
    return result


def main():
    """主函数 - 示例用法"""
    print("=" * 60)
    print("Yahoo Finance 数据获取工具")
    print("=" * 60)
    print()
    
    # 示例1: 获取单只股票数据
    print("示例1: 获取 NVIDIA 数据")
    print("-" * 60)
    nvda_data = get_stock_data('NVDA')
    print(format_for_article(nvda_data))
    print()
    
    # 示例2: 批量获取多只股票
    print("示例2: 批量获取科技巨头数据")
    print("-" * 60)
    tech_stocks = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    results = get_multiple_stocks(tech_stocks)
    
    for ticker, data in results.items():
        if 'error' not in data:
            price = data.get('current_price', 'N/A')
            print(f"{ticker}: ${price}")
    print()
    
    # 示例3: 获取 earnings 数据
    print("示例3: 获取 NVIDIA Earnings 数据")
    print("-" * 60)
    earnings = get_earnings_data('NVDA')
    print(json.dumps(earnings, indent=2, default=str))


if __name__ == "__main__":
    main()
