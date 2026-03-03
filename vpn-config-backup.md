# Xray VLESS + WS + TLS 配置备份
# 域名: proxy.xingyao8206.xyz
# VPS IP: 192.3.104.20
# 创建时间: 2026-02-12

## 服务端配置 (/etc/xray.json)
```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{"id": "b0c49c97-e1c9-4f6e-8c23-f70e9f2e5f4a", "alterId": 0}],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": { "path": "/xrayws", "headers": { "Host": "proxy.xingyao8206.xyz" } },
      "security": "tls",
      "tlsSettings": {
        "certificates": [{
          "certificateFile": "/etc/XrayR/cert/proxy.xingyao8206.xyz.crt",
          "keyFile": "/etc/XrayR/cert/proxy.xingyao8206.xyz.key"
        }],
        "serverName": "proxy.xingyao8206.xyz"
      }
    }
  }],
  "outbounds": [{ "protocol": "freedom", "tag": "direct" }]
}
```

## 客户端配置

### 方案1: 走 Cloudflare (域名)
```
vless://b0c49c97-e1c9-4f6e-8c23-f70e9f2e5f4a@proxy.xingyao8206.xyz:443?encryption=none&security=tls&sni=proxy.xingyao8206.xyz&type=ws&host=proxy.xingyao8206.xyz&path=/xrayws&allowInsecure=1#proxy-CF
```

### 方案2: 优选 IP (更快)
```
vless://b0c49c97-e1c9-4f6e-8c23-f70e9f2e5f4a@172.64.17.74:443?encryption=none&security=tls&sni=proxy.xingyao8206.xyz&type=ws&host=proxy.xingyao8206.xyz&path=/xrayws&allowInsecure=1#proxy-优选IP
```

### 方案3: 直连 VPS (不走 CF)
```
vless://b0c49c97-e1c9-4f6e-8c23-f70e9f2e5f4a@192.3.104.20:443?encryption=none&security=tls&sni=proxy.xingyao8206.xyz&type=ws&host=proxy.xingyao8206.xyz&path=/xrayws&allowInsecure=1#proxy-直连
```

## 优选 IP Top 5
1. 172.64.17.74 (延迟 2.43ms)
2. 172.64.22.99 (延迟 2.57ms)
3. 172.64.19.135 (延迟 2.52ms)
4. 172.64.23.87 (延迟 2.52ms)
5. 172.64.42.77 (延迟 2.53ms)

## 重要提示
- 客户端必须开启 "允许不安全证书" (allowInsecure)
- 因为是自签名证书，不走 Cloudflare 证书链
- 如果走 Cloudflare，确保小黄云开启 + SSL 模式为 "完全"
