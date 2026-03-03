# 微信公众号发布标准流程

## 1. 封面图片
- **来源**: Pexels API (免费)
- **API Key**: GvWstmlt41CdVTFzOPrBZCIo6DHAazMycf6cAcTVZNHEl48ke0w4z8NV
- **搜索关键词**: 根据文章主题匹配
- **上传**: 上传到微信素材库获取thumb_media_id

## 2. 文章格式 (Markdown → HTML)
- **标题**: h1/h2/h3 标签
- **段落**: p 标签，line-height: 1.8
- **粗体**: strong 标签
- **表格**: 
  - width: 100%
  - border-collapse: collapse
  - 表头: 绿色背景 (#07c160)
  - 单元格: padding 10-12px
  - 边框: 1px solid #ddd
- **引用**: blockquote，左边框绿色

## 3. 字数要求
- **每篇文章**: 3000-5000字
- **结构**: 核心动态、深度解读、数据洞察、产业影响、投资建议、风险提示

## 4. 中文编码
- **关键**: 使用 `json.dumps(payload, ensure_ascii=False)`
- **编码**: UTF-8
- **避免**: Unicode转义 (\uXXXX)

## 5. 作者信息
- **作者**: 硅基工具人
- **底部**: 硅基工具人 + 蓝色渐变背景

## 6. 定时任务
- **时间**: 每天 8:00 (Asia/Shanghai)
- **任务**: 生成5篇AI财经日报
- **审核**: 每天 8:10

## 7. 内容来源
- Reuters、CNBC、Bloomberg
- Microsoft Blog、Google Blog
- 官方公告、财报

## 8. 脚本位置
- 封面获取: `/root/.openclaw/pexels-image.sh`
- 发布脚本: `/root/.openclaw/wechat-format.sh`
- API配置: `/root/.openclaw/pexels-config.env`
