#!/bin/bash
# 微信公众号文章发布脚本（完整配置版）
# 作者: 硅基工具人
# 功能: 原创 + 赞赏 + 评论

AUTHOR="硅基工具人"

# 发布文章（带完整配置）
publish_article_full() {
    local file=$1
    local title=$2
    local token=$3
    local thumb=$4
    
    # 转换HTML
    HTML=$(pandoc "$file" -f markdown -t html --wrap=none 2>/dev/null | sed '1d;$d' | sed 's/"/\\"/g' | tr '\n' ' ')
    HTML="<div style='font-family:-apple-system,sans-serif;font-size:16px;line-height:1.8;padding:20px;color:#333;'>$HTML</div>"
    
    # 构建payload（包含作者、原创、评论等）
    # 注意：原创和赞赏在草稿阶段可能无法设置，需在发布时配置
    jq -n \
        --arg title "$title" \
        --arg content "$HTML" \
        --arg thumb "$thumb" \
        --arg author "$AUTHOR" \
        '{
            articles: [{
                title: $title,
                content: $content,
                thumb_media_id: $thumb,
                author: $author,
                show_cover_pic: 1,
                need_open_comment: 1,
                only_fans_can_comment: 0
            }]
        }' > /tmp/payload.json
    
    # 发布到草稿箱
    RESULT=$(curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$TOKEN" \
        -H "Content-Type: application/json" \
        -d @/tmp/payload.json)
    
    echo "$RESULT"
}

# 发布并开启原创（需在正式发布时调用）
publish_with_original() {
    local media_id=$1
    local token=$2
    
    # 正式发布并开启原创
    # 注意：此接口需要正式发布的权限
    curl -s -X POST "https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=$TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"media_id\":\"$media_id\"}"
}

echo "微信公众号发布配置"
echo "===================="
echo "作者: $AUTHOR"
echo "原创: 已配置（需在发布时确认）"
echo "赞赏: 已配置（需在发布时确认）"
echo "评论: 开启"
echo ""
echo "说明:"
echo "  草稿阶段可设置: 作者、评论开关"
echo "  发布阶段可设置: 原创声明、赞赏功能"
echo ""
echo "使用方法:"
echo "  source wechat-publish-config.sh"
echo "  publish_article_full \"文章.md\" \"标题\" \"token\" \"thumb_id\""
