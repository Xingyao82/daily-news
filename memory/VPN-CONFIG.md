# VPN 配置备份

> UUID: `83da297c-7d81-4548-bfa6-5cf7e9e94431`
> 域名: `proxy.xingyao8206.xyz`

---

## 🟢 当前可用：Reality 直连

```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@192.3.104.20:12144?type=tcp&security=reality&flow=xtls-rprx-vision&sni=www.cloudflare.com&pbk=cHTvQVPZhgqkdQ-l2LQWqqHHqr1_KypPXG-QhJgv3BE&sid=&spx=/#Reality-直连
```

**特点：**
- ✅ **当前可用** 🎉
- ✅ 直连 VPS，不经过 Cloudflare
- ✅ Reality 协议，伪装 Cloudflare SNI
- ⚠️ 有被封 IP 风险（不要用大流量）

**PublicKey:** `cHTvQVPZhgqkdQ-l2LQWqqHHqr1_KypPXG-QhJgv3BE`

---

## 🔴 暂时不可用：Cloudflare Tunnel

**问题：** 边缘 IP `198.54.117.242` 被墙，所有端口 Connection Refused

### Plan A：WebSocket 443
```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@proxy.xingyao8206.xyz:443?type=ws&security=tls&sni=proxy.xingyao8206.xyz&host=proxy.xingyao8206.xyz&path=/ws#CF-WS-443
```

### Plan B：WebSocket 8443
```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@proxy.xingyao8206.xyz:8443?type=ws&security=tls&sni=proxy.xingyao8206.xyz&host=proxy.xingyao8206.xyz&path=/ws#CF-WS-8443
```

### Plan C：gRPC 2053
```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@proxy.xingyao8206.xyz:2053?type=grpc&security=tls&sni=proxy.xingyao8206.xyz&serviceName=grpc#CF-gRPC-2053
```

---

## 📋 使用建议

| 优先级 | 配置 | 状态 | 用途 |
|--------|------|------|------|
| 1 | Reality 直连 | 🟢 可用 | 现在用 |
| 2 | CF Tunnel | 🔴 被墙 | 等恢复 |

**警告：**
- Reality 直连**不要用大流量**（看视频、下载），容易触发封 IP
- 轻度使用（浏览网页、查资料）相对安全
- Tunnel 恢复后立即切回

---

## 🔧 修复记录

- 2026-02-20：发现 Cloudflare 边缘 IP 198.54.117.242 被墙
- 2026-02-20：创建新 Tunnel (vps-proxy-new)，仍分配到被墙 IP
- 状态：等待 Cloudflare 更换边缘 IP 或寻找其他解决方案
