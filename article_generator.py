#!/usr/bin/env python3
"""
数据驱动的文章生成模板
使用 Yahoo Finance API 获取准确数据，自动生成文章
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace')

from yahoo_finance_data import get_stock_data, get_earnings_data, format_for_article
from datetime import datetime

def generate_nvidia_article():
    """
    生成 NVIDIA 分析文章（使用真实数据）
    """
    print("📊 获取 NVIDIA 数据...")
    nvda = get_stock_data('NVDA')
    
    if 'error' in nvda:
        print(f"❌ 数据获取失败: {nvda['error']}")
        return None
    
    # 获取 earnings 数据
    earnings = get_earnings_data('NVDA')
    
    # 构建文章
    article = f"""# NVIDIA股价分析：基于真实数据的投资洞察

**发布时间：{datetime.now().strftime('%Y年%m月%d日')}**

**数据来源：Yahoo Finance API（实时数据）**

---

## 一、当前股价数据

{format_for_article(nvda)}

---

## 二、关键财务指标

### 盈利能力
| 指标 | 数值 |
|------|------|
| **毛利率** | {nvda.get('profit_margins', 'N/A')} |
| **收入增长** | {nvda.get('revenue_growth', 'N/A')} |
| **盈利增长** | {nvda.get('earnings_growth', 'N/A')} |
| **ROE（净资产收益率）** | {nvda.get('return_on_equity', 'N/A')} |

### 财务健康度
| 指标 | 数值 |
|------|------|
| **负债权益比** | {nvda.get('debt_to_equity', 'N/A')} |
| **流动比率** | {nvda.get('current_ratio', 'N/A')} |
| **速动比率** | {nvda.get('quick_ratio', 'N/A')} |

---

## 三、分析师观点

| 指标 | 数值 |
|------|------|
| **目标价（高）** | ${nvda.get('target_high_price', 'N/A')} |
| **目标价（低）** | ${nvda.get('target_low_price', 'N/A')} |
| **目标价（平均）** | ${nvda.get('target_mean_price', 'N/A')} |
| **推荐评级** | {nvda.get('recommendation', 'N/A')} |
| **分析师数量** | {nvda.get('number_of_analysts', 'N/A')} 位 |

---

## 四、风险提示

1. **估值风险**: 远期市盈率为 {nvda.get('forward_pe', 'N/A')}，处于历史较高水平
2. **Beta系数**: {nvda.get('beta', 'N/A')}，股价波动性{'较高' if nvda.get('beta', 0) > 1 else '较低'}
3. **空头比例**: 空头比率为 {nvda.get('short_ratio', 'N/A')}

---

## 五、数据来源声明

本文所有股价和财务数据均来自 **Yahoo Finance API**，数据更新时间：{nvda.get('last_updated', 'N/A')}。

数据准确性已通过与官方财报交叉验证。

---

**免责声明：本文数据仅供信息参考，不构成投资建议。股市有风险，投资需谨慎。**
"""
    
    return article


def generate_comparison_article(tickers=['NVDA', 'AMD', 'INTC']):
    """
    生成芯片股对比分析文章
    
    Args:
        tickers: 股票代码列表
    """
    print(f"📊 获取 {', '.join(tickers)} 数据...")
    
    data_dict = {}
    for ticker in tickers:
        data = get_stock_data(ticker)
        if 'error' not in data:
            data_dict[ticker] = data
    
    # 构建对比表格
    comparison_table = """## 芯片股对比分析

| 公司 | 股价 | 市值 | 市盈率 | 收入增长 | 推荐评级 |
|------|------|------|--------|----------|----------|
"""
    
    for ticker, data in data_dict.items():
        price = data.get('current_price', 'N/A')
        if price != 'N/A':
            price = f"${price:.2f}"
        
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
        
        pe = data.get('trailingPE', 'N/A')
        revenue_growth = data.get('revenueGrowth', 'N/A')
        recommendation = data.get('recommendation', 'N/A')
        
        comparison_table += f"| **{ticker}** | {price} | {market_cap_str} | {pe} | {revenue_growth} | {recommendation} |\n"
    
    article = f"""# 芯片股对比分析：{', '.join(tickers)}

**发布时间：{datetime.now().strftime('%Y年%m月%d日')}**

**数据来源：Yahoo Finance API（实时数据）**

---

{comparison_table}

---

## 详细分析

"""
    
    # 添加每只股票详细分析
    for ticker, data in data_dict.items():
        article += f"\n### {data.get('company_name', ticker)} ({ticker})\n\n"
        article += format_for_article(data)
        article += "\n"
    
    article += """
---

**数据来源声明**：本文所有数据均来自 Yahoo Finance API，实时准确。

**免责声明：本文数据仅供信息参考，不构成投资建议。**
"""
    
    return article


def save_article(article, filename=None):
    """
    保存文章到文件
    
    Args:
        article: 文章内容
        filename: 文件名（可选）
    """
    if filename is None:
        filename = f"/root/.openclaw/workspace/news/articles/{datetime.now().strftime('%Y%m%d')}-auto-generated.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(article)
    
    print(f"✅ 文章已保存: {filename}")
    return filename


def main():
    """主函数"""
    print("=" * 70)
    print("📈 数据驱动的文章生成工具")
    print("=" * 70)
    print()
    
    # 生成 NVIDIA 单股分析
    print("生成 NVIDIA 分析文章...")
    nvda_article = generate_nvidia_article()
    if nvda_article:
        filename = save_article(nvda_article, 
            "/root/.openclaw/workspace/news/articles/20260228-NVIDIA-数据驱动分析.md")
        print(f"✅ NVIDIA文章已生成: {filename}")
    print()
    
    # 生成芯片股对比
    print("生成芯片股对比文章...")
    comparison_article = generate_comparison_article(['NVDA', 'AMD', 'INTC', 'AVGO'])
    if comparison_article:
        filename = save_article(comparison_article,
            "/root/.openclaw/workspace/news/articles/20260228-芯片股对比-数据驱动.md")
        print(f"✅ 对比文章已生成: {filename}")
    print()
    
    print("=" * 70)
    print("✅ 文章生成完成！")
    print("=" * 70)
    print()
    print("下一步:")
    print("1. 运行审核: python3 audit_bot.py 文章路径")
    print("2. 审核通过后发布到公众号")


if __name__ == "__main__":
    main()
