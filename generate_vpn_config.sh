#!/bin/bash
# 生成小火箭配置和优选 IP 脚本

VPS_DOMAIN="proxy.xingyao8206.xyz"
UUID="b0c49c97-e1c9-4f6e-8c23-f70e9f2e5f4a"
PATH="/xrayws"

# 生成小火箭配置链接
generate_shadowrocket_link() {
    local cf_ip=$1
    
    # VLESS 格式：vless://uuid@host:port?params#remark
    # 使用 Cloudflare IP 作为连接地址，SNI 保持域名
    echo "vless://${UUID}@${cf_ip}:443?security=tls&sni=${VPS_DOMAIN}&type=ws&host=${VPS_DOMAIN}&path=${PATH}#CF-优选-${cf_ip}"
}

# 生成订阅内容
generate_subscription() {
    local output_file="/root/.openclaw/workspace/sing-box/subscription.txt"
    mkdir -p /root/.openclaw/workspace/sing-box
    
    echo "# 小火箭订阅配置" > $output_file
    echo "# 生成时间: $(date)" >> $output_file
    echo "" >> $output_file
    
    # 检查是否有优选 IP
    if [ -f "/root/.openclaw/workspace/cf_best_ip.txt" ]; then
        echo "# 基于 Cloudflare 优选 IP 生成" >> $output_file
        echo "" >> $output_file
        
        # 读取前3个优选 IP
        head -3 /root/.openclaw/workspace/cf_best_ip.txt | while read line; do
            ip=$(echo $line | awk '{print $1}')
            delay=$(echo $line | awk '{print $2}')
            
            if [ -n "$ip" ]; then
                link=$(generate_shadowrocket_link "$ip")
                echo "$link" >> $output_file
                echo "# IP: $ip 延迟: ${delay}ms" >> $output_file
                echo "" >> $output_file
            fi
        done
    else
        echo "# 暂无优选 IP，使用默认域名配置" >> $output_file
        echo "" >> $output_file
        # 使用域名（通过 Cloudflare CDN）
        link=$(generate_shadowrocket_link "$VPS_DOMAIN")
        echo "$link" >> $output_file
    fi
    
    echo $output_file
}

# 生成 Clash 配置
generate_clash_config() {
    local output_file="/root/.openclaw/workspace/sing-box/clash.yaml"
    
    cat > $output_file << EOF
# Clash Meta 配置
# 配合 Cloudflare 优选 IP 使用

mixed-port: 7890
allow-lan: false
mode: rule
log-level: info

dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query

proxies:
  - name: "CF-优选-自动"
    type: vless
    server: ${VPS_DOMAIN}
    port: 443
    uuid: ${UUID}
    tls: true
    servername: ${VPS_DOMAIN}
    network: ws
    ws-opts:
      path: ${PATH}
      headers:
        Host: ${VPS_DOMAIN}

proxy-groups:
  - name: "Proxy"
    type: select
    proxies:
      - "CF-优选-自动"

rules:
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
EOF

    echo $output_file
}

# 主函数
main() {
    echo "生成订阅配置..."
    
    sub_file=$(generate_subscription)
    clash_file=$(generate_clash_config)
    
    echo ""
    echo "✅ 配置已生成："
    echo "  小火箭订阅: $sub_file"
    echo "  Clash配置: $clash_file"
    echo ""
    echo "订阅链接："
    echo "  http://$(curl -s ifconfig.me):18789/sing-box/subscription.txt"
}

main
