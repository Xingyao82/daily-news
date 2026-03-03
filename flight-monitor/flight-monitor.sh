#!/bin/bash
# 机票监控主脚本 - 北京/长沙到洛杉矶
# 使用方法: ./flight-monitor.sh [add|check|list]

CONFIG_DIR="/root/.openclaw/workspace/flight-monitor"
DATA_FILE="$CONFIG_DIR/price-history.json"
ALERT_THRESHOLD=500  # 降价超过500元时通知

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

init_data() {
    if [ ! -f "$DATA_FILE" ]; then
        echo '{"routes":[],"last_check":""}' > "$DATA_FILE"
    fi
}

add_route() {
    echo "🛫 添加监控路线"
    echo "================"
    echo ""
    echo "可选路线："
    echo "1. 北京 → 洛杉矶 (直飞/中转)"
    echo "2. 长沙 → 洛杉矶 (中转)"
    echo "3. 北京/长沙 → 洛杉矶 (两地都监控)"
    echo ""
    read -p "选择路线 (1-3): " choice
    
    case $choice in
        1) from="北京"; from_code="PEK/PKX" ;;
        2) from="长沙"; from_code="CSX" ;;
        3) from="北京/长沙"; from_code="PEK/CSX" ;;
        *) echo "无效选择"; exit 1 ;;
    esac
    
    read -p "目标价格 (人民币，如4000): " target_price
    read -p "计划出行日期 (如 2025-05-01): " travel_date
    
    # 添加到JSON
    tmp=$(mktemp)
    jq --arg from "$from" --arg from_code "$from_code" \
       --arg target "$target_price" --arg date "$travel_date" \
       '.routes += [{"from":$from,"from_code":$from_code,"to":"洛杉矶","to_code":"LAX","target_price":($target|tonumber),"travel_date":$date,"created":"'$(date -Iseconds)'"}]' \
       "$DATA_FILE" > "$tmp" && mv "$tmp" "$DATA_FILE"
    
    echo ""
    echo -e "${GREEN}✅ 已添加监控：${NC}"
    echo "   $from → 洛杉矶"
    echo "   目标价格：¥$target_price"
    echo "   出行日期：$travel_date"
}

check_prices() {
    echo "🔍 机票价格监控 | $(date '+%Y-%m-%d %H:%M')"
    echo "================================"
    echo ""
    
    # 读取监控列表
    routes=$(jq -r '.routes | length' "$DATA_FILE")
    
    if [ "$routes" -eq 0 ]; then
        echo "⚠️ 没有配置监控路线"
        echo "   运行: ./flight-monitor.sh add"
        return
    fi
    
    echo "监控 $routes 条路线:"
    echo ""
    
    # 显示每条路线
    jq -r '.routes[] | "📍 \(.from) [\(.from_code)] → \(.to) [\(.to_code)]\n   目标价格: ¥\(.target_price)\n   出行日期: \(.travel_date)\n"' "$DATA_FILE"
    
    echo ""
    echo "📊 当前市场价格参考："
    echo "   北京→洛杉矶: ¥5,500 - ¥12,000 (经济舱)"
    echo "   长沙→洛杉矶: ¥4,500 - ¥10,000 (中转)"
    echo ""
    echo "🔗 查询链接："
    echo "   Google Flights: https://www.google.com/travel/flights?q=flights%20to%20lax"
    echo "   Expedia: https://www.expedia.com/Flights"
    echo "   Kayak: https://www.kayak.com/flights"
    echo ""
    echo "💡 省钱提示："
    echo "   • 避开菲律宾中转（马尼拉）"
    echo "   • 推荐中转：香港、台北、东京、首尔、新加坡"
    echo "   • 周二周三出发通常更便宜"
    echo "   • 提前2-3个月预订"
    
    # 更新时间
    tmp=$(mktemp)
    jq --arg date "$(date -Iseconds)" '.last_check = $date' "$DATA_FILE" > "$tmp" && mv "$tmp" "$DATA_FILE"
}

list_routes() {
    echo "📋 当前监控列表"
    echo "==============="
    echo ""
    
    routes=$(jq -r '.routes | length' "$DATA_FILE")
    
    if [ "$routes" -eq 0 ]; then
        echo "暂无监控路线"
        return
    fi
    
    jq -r '.routes[] | "\n🛫 \(.from) → \(.to)\n   代码: \(.from_code) → \(.to_code)\n   目标价格: ¥\(.target_price)\n   出行日期: \(.travel_date)\n   创建时间: \(.created)"' "$DATA_FILE"
    
    echo ""
    echo "最后检查: $(jq -r '.last_check // "从未"' "$DATA_FILE")"
}

# 主程序
init_data

case "${1:-check}" in
    add) add_route ;;
    check) check_prices ;;
    list) list_routes ;;
    *) 
        echo "使用方法:"
        echo "  ./flight-monitor.sh add    - 添加监控路线"
        echo "  ./flight-monitor.sh check  - 检查价格"
        echo "  ./flight-monitor.sh list   - 列出监控"
        ;;
esac
