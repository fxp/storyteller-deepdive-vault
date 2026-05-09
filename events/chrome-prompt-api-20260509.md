---
id: chrome-prompt-api-20260509
title: Google Chrome 推出 Prompt API（浏览器内置 Gemini Nano）
seed_url: https://developer.chrome.com/docs/ai/prompt-api
published_date: 2024-11-12
status: HOT
last_check: 2026-05-09T19:30
last_activity: '2026-05-09'
next_check: 2026-05-09T22:30
interval_hours: 3
consecutive_empty: 0
findings_count: 16
tags:
- tracker
- HOT
entities:
  orgs:
  - Google
  - Chrome 团队
  - Mozilla
  - Apple
  - Microsoft
  people:
  - Thomas Steiner
  - Alexandra Klepper
  products:
  - Chrome Prompt API
  - Gemini Nano
  - Chrome AI APIs
  - Built-in AI
  topics:
  - 浏览器内置 AI
  - 端侧推理
  - Web AI
  - Origin Trial
  - 开发者生态
search_queries:
- Chrome Prompt API developer adoption origin trial 2025 2026
- Gemini Nano on-device Chrome performance benchmark developer experience
- Chrome built-in AI API Firefox Safari Edge competitive response
- Chrome Prompt API enterprise developer use cases production deployment
- Chrome AI APIs stable release graduation origin trial update
---

# Google Chrome 推出 Prompt API（浏览器内置 Gemini Nano）

> 追踪卡片 · 状态: HOT · 下次检查: 2026-05-09T12:18

## 种子事件

**日期**: 2024-11-12（Chrome Extensions Origin Trial 开放）
**来源**: [Prompt API - Chrome for Developers](https://developer.chrome.com/docs/ai/prompt-api)

**摘要**: Google Chrome 推出 Prompt API，允许开发者直接在浏览器中向本地运行的 Gemini Nano 模型发送自然语言请求，无需调用远程服务器。该 API 最初作为 Chrome Extensions 的 Origin Trial（Chrome 131 起），后扩展到普通网页（Chrome 138+）。Chrome 148 进一步加入采样参数控制（temperature、topK）的 Origin Trial。典型应用场景包括：AI 搜索增强、内容过滤、从邮件中提取日历事件/联系人、个性化信息流等。

## 关键实体

- **组织**: Google（Chrome 团队）；潜在竞争方：Mozilla、Apple、Microsoft
- **人物**: Thomas Steiner、Alexandra Klepper（Chrome 开发者关系）
- **产品**: Chrome Prompt API、Gemini Nano、Chrome Built-in AI APIs
- **赛道**: 浏览器端侧 AI / Web AI / 本地推理 / 隐私优先 AI

## 预期后续方向

1. Prompt API 从 Origin Trial 毕业，进入 Chrome 稳定版（正式 GA）
2. 开发者生态采用情况：真实应用案例、性能反馈
3. Gemini Nano 模型版本迭代，能力边界扩展
4. 竞争对手跟进：Firefox、Safari、Edge 是否推出类似本地推理能力
5. W3C/WICG 标准化进程（Prompt API 是否纳入 Web 标准）
6. 企业/隐私合规场景：数据不出设备如何赢得企业用户

## 后续发现

<!-- 监控代理自动追加 -->

## 相关文章

- [Prompt API - Chrome for Developers](https://developer.chrome.com/docs/ai/prompt-api)
- [Chrome Extensions Prompt API Origin Trial](https://developer.chrome.com/docs/extensions/ai/prompt-api)
### 2026-05-09
- [Join the Prompt API origin trial  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/prompt-multimodal-origin-trial) — Google Chrome 推出 Prompt API，允许开发者在其网站上使用该 API。
- [Mozilla pushes back against Google's Prompt API](https://www.theregister.com/software/2026/04/30/mozilla-pushes-back-against-googles-prompt-api/5223409) — Mozilla 对 Google 的 Prompt API 决策表示反对。
- [Prompt API - Chrome Platform Status](https://chromestatus.com/feature/5134603979063296?gate=5123192519393280) — Prompt API 提供了对设备上 AI 语言模型的直接访问。
- [Expanding built-in AI to more devices with Chrome  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/gemini-nano-cpu-support) — Chrome 中的 Gemini Nano 更新，旨在将强大的客户端 AI 功能带给更广泛的用户和设备。
- [Chrome's Built-In AI: Gemini Nano and Prompt API Complete Guide](https://flaming.codes/posts/chrome-gemini-nano-built-in-ai) — Google Chrome 通过 Prompt API 直接在浏览器中添加了 Gemini Nano。
- [Prompt API - Chrome Platform Status](https://chromestatus.com/feature/5134603979063296) — Prompt API 支持各种用例，从生成图像标题和执行视觉搜索到转录音频，分类声音。
- [AI APIs are in stable and origin trials, with new Early Preview Program APIs  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/ai-api-updates-io25) — 从 Chrome 138 开始，Summarizer API、Language Detector API 和 Translator API 可用。
### 2026-05-09
- [If Chrome has the *#optimization-guide-on-device-model* and *#prompt-api-for-gem... | Hacker News](https://news.ycombinator.com/item?id=48019542) — Chrome 148版本将发布，支持Prompt API的新下载功能。
- [Discover the Power of Gemini Nano: The On-Device AI Model running in Chrome 127+ - DEV Community](https://dev.to/codewithahsan/discover-the-power-of-gemini-nano-the-on-device-ai-model-running-in-chrome-127-e7g) — 介绍Gemini Nano在Chrome 127+版本中的运行情况。
- [Google is building its Gemini Nano AI model into Chrome on the desktop | TechCrunch](https://techcrunch.com/2024/05/14/google-is-building-its-gemini-nano-ai-model-into-chrome-on-the-desktop/) — Google宣布将Gemini Nano AI模型直接集成到Chrome桌面客户端中。
### 2026-05-09
- [Any release timeline for LanguageModel? - Google Groups](https://groups.google.com/a/chromium.org/g/chrome-ai-dev-preview-discuss/c/lTfc3susp8g/m/ODo9ndWnAwAJ) — Google Groups 中讨论了 Prompt API 的当前 origin trial 包括多模态支持，提供了新事实。
- [# Gemini Nano: Google's Most Powerful On-Device AI Model ...](https://www.facebook.com/groups/AIUGM/posts/3799327687014865/) — Facebook 群组中提到 Gemini Nano 目前在 Chrome Canary 中可用，提供了新事实。
- [Google launches Gemini Nano for Chrome desktop client | Okoone](https://www.okoone.com/spark/technology-innovation/google-launches-gemini-nano-for-chrome-desktop-client/) — Okoone 文章探讨了 Gemini Nano 如何增强 Chrome，提供了新事实。
- [Practical built-in AI with Gemini Nano in Chrome - YouTube](https://www.youtube.com/watch?v=CjpZCWYrSxM) — YouTube 视频介绍了 Chrome 内置 AI 和 Prompt API，提供了新事实。
- [Is Google’s New Chrome AI API a Security Risk?](https://twit.tv/posts/tech/googles-new-chrome-ai-api-security-risk) — Twit.tv 上讨论了 Google 新的 Chrome AI API 的安全问题，提供了新事实。
- [Exploring Built-in AI for Chrome: The Prompt API | tyingshoelaces](https://tyingshoelaces.com/blog/chrome-ai-prompt-api) — tyingshoelaces 博客介绍了如何获取浏览器中的生成式 AI 结果，提供了新事实。

