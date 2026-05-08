---
deployment: "deepdive"
vault_path: "/vault"
slack_channel: "event-update"
tracker_version: "2.0-cloud"
cron: "0 * * * *"
mode: "managed-agents"
---

# DeepDive 部署配置（Cloud 版）

## 说明

DeepDive 是 StoryTeller 的第一个部署实例，运行在 Anthropic Managed Agents 云容器中。
每篇 DeepDive 文章对应一个事件，发布后注册进追踪系统。

## 路径（Cloud 容器内）

- **Vault**: `/vault`（由 agent 从 GitHub repo 克隆）
- **Events**: `/vault/events/`
- **Findings**: `/vault/findings/`

## 运行方式

GitHub Actions 每小时触发 `scripts/trigger.py`，它创建一个 Managed Agent session。
Agent 克隆此 repo → 执行监控工作流 → 推送更新回 GitHub。

## 相关性判断标准（DeepDive 专属）

**算作发现（推送 Slack）：**
- 新公司正式命名或官方启动公告
- 首批客户/案例公告
- 新融资、估值、股权结构变动
- 核心高管对该项目的公开表态
- 竞争对手针对性反应
- 招聘公告（新实体的专项岗位）
- Claude Partner Network 新成员加入

**忽略（不推送）：**
- 泛泛 AI 行业新闻仅顺带提及
- 对原公告的转载或摘编
- 无新事实的观点类文章
