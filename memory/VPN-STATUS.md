# VPN 状态记录（2026-02-21）

## 🔴 当前问题
Cloudflare Tunnel 边缘 IP `198.54.117.242` 被墙，所有端口 Connection Refused。

## 🟢 可用方案

### 1. Reality 直连（当前可用，但暴露 VPS IP）
```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@192.3.104.20:12144?type=tcp&security=reality&flow=xtls-rprx-vision&sni=www.cloudflare.com&pbk=cHTvQVPZhgqkdQ-l2LQWqqHHqr1_KypPXG-QhJgv3BE&sid=&spx=/#Reality-直连
```
- ✅ 现在就能用
- ⚠️ 暴露 VPS IP，有被封风险

### 2. 优选 IP 方案（推荐，待测试）
修改 hosts 文件，绕过被墙 IP：
```
104.16.80.182 proxy.xingyao8206.xyz
```
备选 IP：
- 104.18.1.242
- 104.20.0.1
- 172.65.80.1

然后使用原链接：
```
vless://83da297c-7d81-4548-bfa6-5cf7e9e94431@proxy.xingyao8206.xyz:443?type=ws&security=tls&sni=proxy.xingyao8206.xyz&host=proxy.xingyao8206.xyz&path=/ws#CF-优选IP
```

### 3. Workers 中转（备用方案）
需要手动在 Cloudflare Dashboard 创建 Worker，代码：
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    url.hostname = "vps-proxy-new.xingyao8206.xyz";
    return fetch(url, request);
  }
};
```

## 📋 服务器配置
- Xray 监听：443, 8443, 2053, 12144
- Tunnel：vps-proxy-new（4 条线正常，但入口 IP 被墙）
- 自动监控：每 2 分钟检查，自动重启

## 📝 TODO
- [ ] 测试优选 IP 是否可用
- [ ] 如优选 IP 不行，尝试 Workers 中转
- [ ] 或等待 Cloudflare 自动更换边缘 IP
