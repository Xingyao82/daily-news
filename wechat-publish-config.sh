#!/bin/bash
# 微信公众号文章发布脚本（带作者配置）
# 作者: 硅基工具人

AUTHOR="硅基工具人"

publish_article() {
    local file=$1
    local title=$2
    local token=$3
    local thumb=$4
    
    # 转换HTML
    HTML=$(pandoc "$file" -f markdown -t html --wrap=none 2>/dev/null | sed '1d;$d' | sed 's/"/\\"/g' | tr '\n' ' ')
    HTML="<div style='font-family:-apple-system,sans-serif;font-size:16px;line-height:1.8;padding:20px;color:#333;'>$HTML</div>"
    
    # 构建payload（包含作者）
    jq -n \
        --arg title "$title" \
        --arg content "$HTML" \
        --arg thumb "$thumb" \
        --arg author "$AUTHOR" \
        '{articles:[{title:$title,content:$content,thumb_media_id:$thumb,author:$author,show_cover_pic:1}]}' > /tmp/payload.json
    
    # 发布
    curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$TOKEN" \
        -H "Content-Type: application/json" \
        -d @/tmp/payload.json
}

echo "微信公众号发布配置"
echo "===================="
echo "作者: $AUTHOR"
echo ""
echo "使用方式:"
echo "  source wechat-publish-config.sh"
echo "  publish_article \"文章.md\" \"标题\" \"token\" \"thumb_id\""
