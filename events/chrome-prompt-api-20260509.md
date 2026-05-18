---
id: chrome-prompt-api-20260509
title: Google Chrome 推出 Prompt API（浏览器内置 Gemini Nano）
seed_url: https://developer.chrome.com/docs/ai/prompt-api
published_date: 2024-11-12
status: HOT
last_check: 2026-05-18T22:28
last_activity: '2026-05-18'
next_check: 2026-05-19T01:28
interval_hours: 3
consecutive_empty: 0
findings_count: 65
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
### 2026-05-09
- [Enhancing Gemini Nano: delivering higher quality summaries with LoRA  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/improved-summaries-gemini-nano) — Chrome 与 Google Cloud 合作改进 Gemini Nano 的输出，提供更高质量的摘要。
- [Browser AI with Chrome Prompt API | by Roman Fedytskyi - Medium](https://medium.com/@roman_fedyskyi/browser-ai-with-chrome-prompt-api-7954b46d113c) — 使用 Chrome 的 Prompt API 调用 AI 模型，构建交互式助手。
### 2026-05-10
- [Any release timeline for LanguageModel? - Google Groups](https://groups.google.com/a/chromium.org/g/chrome-ai-dev-preview-discuss/c/lTfc3susp8g) — Google Chrome 的 Prompt API 现在支持多模态支持，这是新事实。
- [Join the Prompt API for Chrome Extensions origin trial | Blog](https://developer.chrome.com/blog/prompt-api-origin-trial) — Prompt API 现在可用于 Chrome 扩展程序的 origin trial，这是新事实。
- [Build a local and offline-capable chatbot with the Prompt API  |  web.dev](https://web.dev/articles/ai-chatbot-promptapi) — 文章介绍了如何使用 Prompt API 构建本地和离线聊天机器人，这是新事实。
### 2026-05-10
- [Devpost](https://googlechromeai2025.devpost.com/resources) — Google Chrome Built-in AI Challenge 2025，邀请开发者使用内置AI API构建新应用或扩展。
- [Build a helpful, powerful web in the Google Chrome Built-in AI Challenge 2025  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/ai-challenge-2025) — Google Chrome Built-in AI Challenge 2025，邀请开发者使用内置AI API构建新应用或扩展。
### 2026-05-10
- [Prompt API on Chrome AI in 2025 - YouTube](https://www.youtube.com/watch?v=b-5WjGqsVz0) — 视频展示了 Chrome Prompt API 的几个功能，包括 zero-shot prompting、system prompts 和 n-shot prompting。
### 2026-05-10
- [When Chrome's Prompt API goes public — what are the ...](https://www.reddit.com/r/microsaas/comments/1r853yx/when_chromes_prompt_api_goes_public_what_are_the/) — 讨论了 Chrome Prompt API 公开后可能出现的第一个实际用例。
- [Chrome Built-in AI Guide](https://chromeai.oslook.com/guide) — Chrome 内置 AI 指南，包括设置和使用 Chrome 内置 AI API 的完整指南。
### 2026-05-10
- [Chrome's Gemini Nano Local AI Model: Eligibility and Performance](https://www.linkedin.com/posts/thenextgentechinsider_tech-news-activity-7421157310749843457-OSyN) — Chrome 的 Gemini Nano 本地 AI 模型具有 41% 的合格率，6 倍的运行速度，生产中的 0 成本。
- [Lionel Péramo's Post - Prompt API - LinkedIn](https://www.linkedin.com/posts/lionel-p%C3%A9ramo-web-development_prompt-api-ai-is-now-in-your-browser-the-activity-7423289014641790976-BzSh) — Prompt API 的常见用例包括自动化重复性工作流程、测试基于浏览器的流程、跨多个标签运行研究任务等。
### 2026-05-11
- [Explainer for the Prompt API - GitHub](https://github.com/webmachinelearning/prompt-api) — 解释了 Prompt API 的使用情况，包括下载进度监控。
### 2026-05-11
- ["Try Chrome's free, local AI with Prompt API" | Addy Osmani posted on the topic | LinkedIn](https://www.linkedin.com/posts/addyosmani_ai-softwareengineering-programming-activity-7360916715783770113-WtOb) — 介绍了 Chrome 的 Prompt API 和其他 API 的使用情况，包括 Writer API 和 Rewriter API，提供了新事实。
- [When Chrome's Prompt API goes public — what are the first real use ...](https://www.reddit.com/r/chrome_extensions/comments/1r78n49/when_chromes_prompt_api_goes_public_what_are_the/) — 讨论了 Chrome Prompt API 的潜在用途，提供了新事实。
### 2026-05-11
- [Built-in AI Web APIs: Chrome's On-Device Revolution - LinkedIn](https://www.linkedin.com/pulse/built-in-ai-web-apis-chromes-on-device-revolution-rahulkumar-gaddam-dzume) — LinkedIn 博客介绍了 Chrome 内置 AI Web API 的革命性，包括实验性 API 的测试。
### 2026-05-11
- [Google's Gemini Nano in Chrome Raises Privacy and Performance Concerns | Welcome.AI](https://welcome.ai/content/googles-gemini-nano-in-chrome-raises-privacy-and-performance-concerns) — Google 的 Gemini Nano 引起隐私和性能担忧，用户可以通过切换功能禁用它。
- [Google Tests Gemini Nano AI Inside Chrome - LinkedIn](https://www.linkedin.com/posts/acceleratorxorg_gemini-chrome-google-activity-7396089105584955392-qhYS) — Google 在 Chrome 浏览器中测试 Gemini Nano AI，这是一个新事实。
### 2026-05-11
- [Mozilla's opposition to Chrome's Prompt API | Hacker News](https://news.ycombinator.com/item?id=47959463) — Mozilla 对 Chrome 的 Prompt API 表示反对，提供了新的事实和观点。
- [Inside Chrome's / Edge's silent 4GB AI install: a complete hands-on ...](https://dev.to/jacquesgariepy/inside-chromes-edges-silent-4gb-ai-install-a-complete-hands-on-investigation-54g2) — Chrome 和 Edge 的 4GB AI 安装调查，提供了新的事实。
- [Chrome's Local AI Model in production (Gemini Nano) 41 ... - Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1qkph45/chromes_local_ai_model_in_production_gemini_nano/) — Reddit 上关于 Chrome 本地 AI 模型 Gemini Nano 的性能讨论，提供了新的事实。
### 2026-05-12
- [A Browser AI API? - End of Bug Bounties? - YouTube](https://www.youtube.com/watch?v=EWJbJgHFLcg) — Google 在 Chrome 中秘密集成了一个 4.7GB 的大规模 AI 模型，Mozilla 正在反击，这预示着浏览器未来的 AI 转变。
- [New AI powered APIs added to Chrome 138+ versions - Reddit](https://www.reddit.com/r/chrome/comments/1lgrv0i/new_ai_powered_apis_added_to_chrome_138_versions/) — Chrome 138 及更高版本内置了 3 个新的基于 AI 的网络 API，包括语言检测 API 和摘要 API。
### 2026-05-12
- [Your Chrome Browser Just Became an AI Assistant](https://ai.plainenglish.io/your-chrome-browser-just-became-an-ai-assistant-heres-what-that-means-209b3acc6299) — Google Gemini 现已内置 Chrome，使浏览器成为 AI 助手，这是新事实。
- [Mozilla opposes the implementation of Chrome's Prompt API in the ...](https://www.reddit.com/r/firefox/comments/1ta8uz0/mozilla_opposes_the_implementation_of_chromes/) — Mozilla 反对 Chrome 的 Prompt API 实施，提供了新的事实和观点。
- [Get started with built-in AI  |  AI on Chrome  |  Chrome for Developers](https://developer.chrome.com/docs/ai/get-started) — Chrome 内置 AI API，允许 Web 应用执行 AI 任务，这是新事实。
### 2026-05-12
- [Next-Level Web Applications with On-Device Generative AI: A Look at Google Chrome's Built-In Gemini Nano LLM - DEV Community](https://dev.to/ptvty/next-level-web-applications-with-on-device-generative-ai-a-look-at-google-chromes-built-in-gemini-nano-llm-4bng) — 介绍了 Chrome 内置的 Gemini Nano LLM 和 `window.ai` API，为网站提供设备端生成式 AI 功能。
- [Chrome for Developers: Gemini Nano supports CPU inference for wider AI access | Sunil Kumar Nayak posted on the topic | LinkedIn](https://www.linkedin.com/posts/sunil-kumar-nayak_expanding-built-in-ai-to-more-devices-with-activity-7379530207247986688-mMix) — Gemini Nano 支持在 CPU 上进行推理，以实现更广泛的 AI 访问，对开发者友好。
### 2026-05-12
- [Prompt API - Chrome Platform Status](https://cr-status.appspot.com/feature/5134603979063296?gate=5165720748687360) — Prompt API 支持多种用例，包括生成图像标题、执行视觉搜索、转录音频和分类声音。
### 2026-05-12
- [Google's Gemini Nano in Chrome Raises Privacy and Performance Concerns | Welcome.AI](https://www.welcome.ai/content/googles-gemini-nano-in-chrome-raises-privacy-and-performance-concerns) — Google 的 Gemini Nano 在 Chrome 中的集成引发了用户隐私和性能的担忧，用户现在可以通过 Google 引入的切换功能禁用它。
- [Chrome's Built-in AI in 3 min - The Prompt API - YouTube](https://www.youtube.com/watch?v=YkUcxX49Rqw) — 视频介绍了 Chrome 内置的 Prompt API 和 Gemini Nano，提供了新事实。
### 2026-05-13
- [Gemini Nano in Chrome: On-Device AI Is Here (No Cloud Required)](https://medium.com/@hamzamfarooqi/gemini-nano-in-chrome-on-device-ai-is-here-no-cloud-required-bba874f60697) — Gemini Nano 现已嵌入 Chrome 138，支持本地摘要、翻译和语言检测，提供了新事实。
- [Why is Mozilla opposing the 'Prompt API,' an AI feature planned for Google Chrome? - GIGAZINE](https://gigazine.net/gsc_news/en/20260501-google-chrome-prompt-api/) — Mozilla 对 Prompt API 表示反对，提供了新的观点和事实。
### 2026-05-13
- [AI Right in the Browser With Chrome’s Built-in AI APIs by Thomas Steiner](https://gitnation.com/contents/chrome-built-in-ai-apis) — Thomas Steiner 讨论了 Chrome 内置 AI API 的探索性 Prompt API 和 Gemini Nano 模型，提供了新信息。
### 2026-05-13
- [Chrome's Built in AI model (Gemini Nano) is 6x slower, only 41% of ...](https://www.reddit.com/r/ArtificialInteligence/comments/1qjxnw8/chromes_built_in_ai_model_gemini_nano_is_6x/) — Chrome 内置 AI 模型 Gemini Nano 的性能数据，包括速度和可用性，提供了新事实。
### 2026-05-13
- [Chrome is about to break the web... AGAIN! - YouTube](https://www.youtube.com/watch?v=seKv8ZyTiOU) — 视频讨论了 Chrome 内置 AI 模型和 Prompt API 的限制，以及 Mozilla 的立场，提供了新事实。
### 2026-05-14
- [Google Brings Gemini Nano to Chrome to Enable On-Device ... - InfoQ](https://www.infoq.com/news/2024/05/chrome-gemini-nano/) — Google Chrome 推出 Prompt API，支持语言相关用例，如摘要、改写或分类。
### 2026-05-14
- [Join the Prompt API for Chrome Extensions origin trial  |  Blog  |  Chrome for Developers](https://developer.chrome.com/blog/prompt-api-origin-trial?hl=en) — 文章标题表明 Prompt API 正在 Chrome 扩展中进行原产地试验，这是新事实。
### 2026-05-14
- [3 things about Prompt API: Local deployment, Gemini Nano, and ...](https://www.linkedin.com/posts/chrome-for-developers_3-things-you-didnt-know-about-the-prompt-activity-7445105966796369920-ieMT) — 介绍 Prompt API 的本地部署和 Gemini Nano，提供了新事实。
### 2026-05-15
- [The Prompt API | Hacker News](https://news.ycombinator.com/item?id=47917026) — Hacker News 上关于 Prompt API 的讨论，可能包含对 Gemini Nano 的新观点或事实。
### 2026-05-15
- [Google responds to Chrome's silent Gemini Nano install, stops short of addressing consent - Digital Trends](https://www.digitaltrends.com/computing/google-responds-to-chromes-silent-gemini-nano-install-stops-short-of-addressing-consent/) — Google 对 Chrome 的静默 Gemini Nano 安装做出回应，强调设备上 AI 对浏览器安全策略的重要性，但未解释为何删除它会导致自动重新下载。
### 2026-05-15
- [An experimental polyfill for the Prompt API  |  AI on Chrome  |  Chrome for Developers](https://developer.chrome.com/docs/ai/prompt-api-polyfill?hl=en) — 介绍了 Prompt API 的实验性 polyfill，提供了关于本地和云端后端提供者的新信息。
### 2026-05-16
- [Mozilla's opposition to Chrome's Prompt API (which only supports ...](https://www.reddit.com/r/linux/comments/1t01wpv/mozillas_opposition_to_chromes_prompt_api_which/) — Mozilla 对 Chrome 的 Prompt API 表示反对，提供了新的观点和事实。
### 2026-05-16
- [Chrome is quietly installing a 4GB AI model on your device - Reddit](https://www.reddit.com/r/cybersecurity/comments/1t57mk5/chrome_is_quietly_installing_a_4gb_ai_model_on/) — Reddit 上讨论了 Chrome 安装 4GB AI 模型的事实，这是新事实。
### 2026-05-16
- [How to use Chrome's Prompt API in Extensions - YouTube](https://www.youtube.com/watch?v=HjPQ3hyeXQI) — 视频介绍如何在 Chrome 扩展中使用 Prompt API，提供了新事实。
### 2026-05-18
- [Google Ships Chrome Prompt API Over Objections From Mozilla, Apple, W3C, and Microsoft](https://www.techtimes.com/articles/316729/20260516/google-ships-chrome-prompt-api-over-objections-mozilla-apple-w3c-microsoft.htm) — Google 在 Chrome 148 中发布了 Prompt API，尽管 Mozilla、Apple、W3C、Microsoft 和一位 Chrome 工程师都提出了正式反对。
### 2026-05-18
- [Prompt API - Microsoft Edge Origin Trials](https://developer.microsoft.com/microsoft-edge/origin-trials/trials/b7d35247-b855-4b08-b237-89e7a5056117) — Microsoft Edge Origin Trials 中介绍了 Prompt API 的使用，这是新事实。
- [On-device GenAI in Chrome, Chromebook Plus, and Pixel Watch with LiteRT-LM
            
            
            - Google Developers Blog](https://developers.googleblog.com/on-device-genai-in-chrome-chromebook-plus-and-pixel-watch-with-litert-lm/) — Google Developers Blog 中介绍了 LiteRT-LM 引擎，这是新事实。
- [Gemini Nano  |  AI  |  Android Developers](https://developer.android.com/ai/gemini-nano) — Android Developers 中介绍了 Gemini Nano 在 Android 上的使用，这是新事实。

