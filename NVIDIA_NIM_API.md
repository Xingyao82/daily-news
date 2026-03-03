# NVIDIA NIM API 配置指南

## 🎉 NVIDIA提供免费API！

NVIDIA推出了 **NIM (NVIDIA Inference Microservices)** 平台，开发者可以免费使用！

---

## ✅ 免费额度

| 项目 | 额度 |
|------|------|
| **免费API调用** | 1,000次（个人邮箱） |
| **公司邮箱注册** | 10,000次 |
| **可下载的模型** | Llama 3.1、Mistral 7B等 |
| **GPU使用** | 最多2节点/16 GPU |

---

## 🔧 申请步骤

### 1. 注册NVIDIA开发者账号
**访问**: https://developer.nvidia.com/developer-program
- 点击 "Join Now"
- 填写邮箱、密码、公司信息
- 验证邮箱

### 2. 加入NVIDIA Developer Program
- 免费加入
- 获得500万+开发者资源

### 3. 获取API Key
**访问**: https://build.nvidia.com/explore/discover
- 登录后选择模型（如Llama 3.1）
- 点击 "Build with this NIM"
- 生成API Key

### 4. 支持的模型
- **Meta Llama 3.1** (8B, 70B, 405B)
- **Mistral 7B Instruct**
- **NVIDIA Nemotron**
- **Google Gemma**
- 等100+模型

---

## 💻 使用示例

```bash
# 调用API
curl https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role":"user","content":"Hello!"}]
  }'
```

---

## 🎯 优势

- ✅ **免费额度**: 1000-10000次调用
- ✅ **GPU加速**: TensorRT优化
- ✅ **标准API**: OpenAI API兼容
- ✅ **多种模型**: Llama、Mistral等
- ✅ **自托管可选**: 可下载Docker容器

---

## 📋 使用限制

- 免费版仅供开发/测试使用
- 生产环境需购买NVIDIA AI Enterprise许可
- 90天免费试用期后可续

---

## 🔗 相关链接

- **NVIDIA API Catalog**: https://build.nvidia.com/explore/discover
- **开发者注册**: https://developer.nvidia.com/developer-program
- **文档**: https://docs.nvidia.com/nim/
- **社区论坛**: https://forums.developer.nvidia.com/c/ai-data-science/nvidia-nim

---

**需要我帮你注册或配置NVIDIA NIM API吗？** 🚀
