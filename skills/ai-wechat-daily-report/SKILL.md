---
name: ai-wechat-daily-report
description: Write Chinese AI/tech/finance daily reports and prepare polished WeChat Official Account draft versions. Use when asked to: collect news, write a 日报, produce a 科技财经日报, create a公众号文章/草稿, optimize title/digest/layout for WeChat, publish to 微信公众号草稿箱, or follow the user's fixed daily-report house style.
---

# AI WeChat Daily Report

Write and publish the user's preferred daily report format.

## Follow this house style

Always apply these defaults unless the user overrides them:

- Write in Chinese.
- Write in a 科技/AI/财经日报 style.
- Prefer medium-to-long length; do not make it too short.
- Focus on facts, synthesis, and market interpretation.
- Author name: `硅基工具人`.
- Do **not** include persona sections like `三妹点评`.
- Do **not** include source links in the article body.
- Default destination for publication is **微信公众号草稿箱**.
- When preparing the WeChat version, generate:
  - a stronger, more clickable title
  - a digest / cover summary
  - WeChat-friendly HTML styling

## Standard workflow

1. Collect the day's relevant AI / tech / market signals.
2. Draft a Markdown daily report in the workspace.
3. Use this structure by default:
   - 标题
   - 作者 / 时间
   - 今日要闻
   - AI与科技热点
   - 市场数据
   - 市场解读
   - 今日关键信号
   - 数据说明
   - 免责声明
4. Remove raw source URLs from the final body unless the user explicitly asks to keep them.
5. If asked for GitHub delivery, save the Markdown in the repo and commit only the relevant report change.
6. If asked for WeChat draft delivery, convert the Markdown to polished WeChat HTML and send it to the Official Account draft box.

## Title rules for WeChat draft

Prefer titles that feel like public-account headlines rather than plain archive titles.

Use patterns like:
- `OpenAI冲刺IPO，Mistral上新：AI行业正在从狂热走向兑现`
- `AI没有大爆点的一天，真正重要的信号却越来越清楚`
- `从OpenAI到英伟达，AI市场开始进入“拼兑现”阶段`

Keep titles specific, readable, and not too tabloid.

## Digest rules

Write a 1-2 sentence digest that:
- summarizes the most important signal of the day
- explains why it matters
- reads naturally in a WeChat cover preview

## Publishing rules

When publishing to WeChat:
- publish to **drafts**, not final publish, unless the user explicitly asks otherwise
- keep author as `硅基工具人`
- prefer clean typography, strong section hierarchy, and readable tables
- do not mass-delete old drafts unless the user explicitly asks

## Operational notes

- Reuse existing local scripts/configs for WeChat publishing when available.
- If credentials fail, stop and ask the user for the updated secret/config.
- Prefer a single polished draft over many variants unless the user asks for options.
- If there are unrelated dirty git changes, isolate the report commit/push so other local work is not disturbed.
