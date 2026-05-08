#!/usr/bin/env python3
"""
StoryTeller Monitor — Route A: GitHub Actions + BigModel

不依赖 Claude CLI 或 Managed Agents，纯结构化 Python 脚本：
  - 搜索：Tavily API（直接 HTTP）
  - 相关性判断：BigModel GLM-4-Flash（单次 LLM 调用）
  - 通知：Slack Webhook（直接 HTTP）
  - 状态持久化：Git（由 GitHub Actions 在脚本后 commit）

运行方式：
  python3 scripts/monitor.py
  （在 vault repo 根目录执行，或 VAULT 环境变量指定路径）
"""

import os
import re
import json
import math
import datetime
import sys
from pathlib import Path

import requests
import yaml

# ── 路径 ─────────────────────────────────────────────────────────

VAULT = Path(os.environ.get("VAULT", Path(__file__).parent.parent))
EVENTS_DIR  = VAULT / "events"
FINDINGS_DIR = VAULT / "findings"
CONFIG_FILE  = VAULT / "config.md"

# ── 凭证 ─────────────────────────────────────────────────────────

TAVILY_API_KEY   = os.environ.get("TAVILY_API_KEY", "")
BIGMODEL_API_KEY = os.environ.get("BIGMODEL_API_KEY", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# ══════════════════════════════════════════════════════════════════
# Markdown frontmatter 解析 / 写入
# ══════════════════════════════════════════════════════════════════

def parse_md(path: Path) -> tuple[dict, str]:
    """读取 .md 文件，返回 (frontmatter_dict, body_str)。"""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                return fm, parts[2].strip()
            except yaml.YAMLError as e:
                print(f"  [WARN] YAML parse error in {path.name}: {e}")
    return {}, text


def write_md(path: Path, fm: dict, body: str):
    """将 frontmatter + body 写回文件。"""
    fm_str = yaml.dump(
        fm, allow_unicode=True, default_flow_style=False, sort_keys=False
    )
    path.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")


# ══════════════════════════════════════════════════════════════════
# 生命周期状态机
# ══════════════════════════════════════════════════════════════════

# (consecutive_empty 上限, 新状态, interval_hours)
LIFECYCLE = [
    (3,  "HOT",      3),
    (11, "ACTIVE",   6),
    (17, "TRACKING", 24),
    (23, "WATCHING", 72),
    (29, "COOLING",  168),
    (37, "DORMANT",  336),
]


def compute_next_state(consecutive_empty: int) -> tuple[str, int]:
    for threshold, status, hours in LIFECYCLE:
        if consecutive_empty <= threshold:
            return status, hours
    return "CLOSED", 0


def add_hours(dt: datetime.datetime, hours: int) -> str:
    return (dt + datetime.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M")


# ══════════════════════════════════════════════════════════════════
# Tavily 搜索
# ══════════════════════════════════════════════════════════════════

def search_tavily(query: str, days: int) -> list[dict]:
    if not TAVILY_API_KEY:
        return []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {TAVILY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
                "days": days,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"    [WARN] Tavily error: {e}")
        return []


def filter_new(results: list[dict], last_check: str, seen_urls: set) -> list[dict]:
    """去掉 last_check 之前的结果，以及已出现过的 URL。"""
    out = []
    for r in results:
        url = r.get("url", "")
        if url in seen_urls:
            continue
        pub = r.get("published_date") or ""
        # published_date 格式各异，做简单字符串前缀比较（都是 ISO 格式）
        if pub and len(pub) >= 10 and pub[:10] < last_check[:10]:
            continue
        out.append(r)
    return out


# ══════════════════════════════════════════════════════════════════
# BigModel 相关性判断
# ══════════════════════════════════════════════════════════════════

def judge_relevance(
    candidates: list[dict],
    event_title: str,
    criteria: str,
) -> list[dict]:
    """
    调用 BigModel GLM-4-Flash 判断相关性，返回 RELEVANT 的结果（含 _summary 字段）。
    """
    if not candidates or not BIGMODEL_API_KEY:
        if not BIGMODEL_API_KEY:
            print("  [WARN] BIGMODEL_API_KEY not set, skipping relevance judgment")
        return []

    items_text = "\n\n".join(
        f"[{i}] 标题: {r.get('title', '(no title)')}\n"
        f"    URL: {r.get('url', '')}\n"
        f"    摘要: {(r.get('content') or '')[:400]}"
        for i, r in enumerate(candidates)
    )

    prompt = f"""你是新闻相关性判断专家。判断以下搜索结果是否与正在追踪的事件相关。

## 追踪事件
{event_title}

## 相关性标准
{criteria}

## 待判断结果
{items_text}

## 输出要求
只输出 JSON 数组，每个元素格式如下（RELEVANT 时填写 summary，NOISE 时 summary 为空字符串）：
[{{"index": 0, "relevance": "RELEVANT", "summary": "一句话：核心新事实是什么"}}, ...]

直接输出 JSON，不要有任何其他文字或 markdown 代码块。"""

    try:
        resp = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {BIGMODEL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "glm-4-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1000,
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()

        # 兼容模型把 JSON 包在 ```json ... ``` 里的情况
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not json_match:
            print(f"  [WARN] BigModel non-JSON response: {raw[:200]}")
            return []

        judgments = json.loads(json_match.group())
        relevant = []
        for j in judgments:
            if j.get("relevance") == "RELEVANT":
                idx = int(j.get("index", -1))
                if 0 <= idx < len(candidates):
                    r = dict(candidates[idx])
                    r["_summary"] = j.get("summary", "")
                    relevant.append(r)
        return relevant

    except json.JSONDecodeError as e:
        print(f"  [WARN] BigModel JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"  [WARN] BigModel API error: {e}")
        return []


# ══════════════════════════════════════════════════════════════════
# Slack 通知
# ══════════════════════════════════════════════════════════════════

def post_slack(
    event_title: str,
    findings: list[dict],
    old_status: str,
    new_status: str,
    next_check: str,
):
    if not SLACK_WEBHOOK_URL or not findings:
        return
    items = "\n".join(
        f"• <{f['url']}|{f.get('title', f['url'])}>"
        + (f" — {f['_summary']}" if f.get("_summary") else "")
        for f in findings[:5]
    )
    text = (
        f"🔔 *{event_title}*\n\n"
        f"*本次发现（{len(findings)} 条）:*\n{items}\n\n"
        f"*状态*: {old_status} → {new_status}  |  *下次检查*: {next_check}"
    )
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Slack post failed: {e}")


# ══════════════════════════════════════════════════════════════════
# Finding 文件
# ══════════════════════════════════════════════════════════════════

def create_finding_file(event_id: str, finding: dict, date_str: str, seq: int):
    FINDINGS_DIR.mkdir(exist_ok=True)
    date_compact = date_str.replace("-", "")
    filename = f"{date_compact}-{event_id}-{seq:03d}.md"
    path = FINDINGS_DIR / filename
    title = finding.get("title") or finding["url"]
    summary = finding.get("_summary") or (finding.get("content") or "")[:300]
    content = (
        f"---\n"
        f'event: "[[{event_id}]]"\n'
        f"date: {date_str}\n"
        f'url: "{finding["url"]}"\n'
        f'source_title: "{title.replace(chr(34), chr(39))}"\n'
        f"relevance: RELEVANT\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"**来源**: [{title}]({finding['url']})\n"
        f"**发现时间**: {date_str}\n"
        f"**所属事件**: [[{event_id}]]\n\n"
        f"## 摘要\n\n{summary}\n"
    )
    path.write_text(content, encoding="utf-8")
    return filename


# ══════════════════════════════════════════════════════════════════
# 读取相关性标准
# ══════════════════════════════════════════════════════════════════

def load_criteria() -> str:
    """从 config.md 提取相关性判断标准章节。"""
    if not CONFIG_FILE.exists():
        return "判断内容是否与追踪事件直接相关，忽略泛泛提及和转载。"
    text = CONFIG_FILE.read_text(encoding="utf-8")
    match = re.search(r"(## 相关性判断标准.*?)(?=\n## |\Z)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "判断内容是否与追踪事件直接相关，忽略泛泛提及和转载。"


# ══════════════════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════════════════

def run():
    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0, tzinfo=None)
    now_str  = now.strftime("%Y-%m-%dT%H:%M")
    date_str = now.strftime("%Y-%m-%d")

    print(f"=== StoryTeller (BigModel) ===")
    print(f"Time : {now_str} UTC")
    print(f"Vault: {VAULT}")

    # 检查必要凭证
    missing = [k for k, v in {
        "TAVILY_API_KEY": TAVILY_API_KEY,
        "BIGMODEL_API_KEY": BIGMODEL_API_KEY,
        "SLACK_WEBHOOK_URL": SLACK_WEBHOOK_URL,
    }.items() if not v]
    if missing:
        print(f"[WARN] Missing env vars: {', '.join(missing)}")

    FINDINGS_DIR.mkdir(exist_ok=True)
    criteria = load_criteria()

    event_files = sorted(EVENTS_DIR.glob("*.md"))
    if not event_files:
        print("No event files found in events/")
        return

    checked = 0
    skipped_not_due = 0
    skipped_closed = 0
    events_with_findings = []

    for event_path in event_files:
        fm, body = parse_md(event_path)
        event_id = str(fm.get("id") or event_path.stem)
        title     = str(fm.get("title", event_id))
        status    = str(fm.get("status", "HOT"))

        # ── Skip 判断 ─────────────────────────────────────────────
        if status == "CLOSED":
            skipped_closed += 1
            continue

        next_check_str = str(fm.get("next_check", ""))
        if next_check_str and next_check_str > now_str:
            skipped_not_due += 1
            continue

        checked += 1
        print(f"\n── {event_id} ──")
        print(f"   status={status}  next_check={next_check_str or '(none)'}")

        # ── 搜索参数 ──────────────────────────────────────────────
        interval_hours  = int(fm.get("interval_hours", 6))
        days_back       = max(1, math.ceil(interval_hours / 24) + 1)
        last_check_str  = str(fm.get("last_check", "2000-01-01T00:00"))
        search_queries  = fm.get("search_queries") or []

        # 已见 URL（从 body 正文中提取，用于去重）
        seen_urls: set[str] = set(re.findall(r"https?://[^\s\)\"']+", body))

        # ── 逐条搜索 ──────────────────────────────────────────────
        all_candidates: list[dict] = []
        for query in search_queries[:5]:
            print(f"   Search: {query[:70]}")
            results = search_tavily(str(query), days_back)
            fresh   = filter_new(results, last_check_str, seen_urls)
            for r in fresh:
                seen_urls.add(r.get("url", ""))
            all_candidates.extend(fresh)

        # URL 去重
        deduped: list[dict] = []
        _seen_dedup: set[str] = set()
        for r in all_candidates:
            u = r.get("url", "")
            if u not in _seen_dedup:
                _seen_dedup.add(u)
                deduped.append(r)

        print(f"   Candidates after dedup: {len(deduped)}")

        # ── 相关性判断 ────────────────────────────────────────────
        relevant = judge_relevance(deduped, title, criteria) if deduped else []
        print(f"   Relevant: {len(relevant)}")

        # ── 状态更新 ──────────────────────────────────────────────
        old_status       = status
        consecutive_empty = int(fm.get("consecutive_empty", 0))

        if relevant:
            consecutive_empty = 0
            new_status, new_interval = "HOT", 3
        else:
            consecutive_empty += 1
            new_status, new_interval = compute_next_state(consecutive_empty)

        next_check_new = (
            add_hours(now, new_interval) if new_status != "CLOSED" else "CLOSED"
        )
        findings_count = int(fm.get("findings_count", 0)) + len(relevant)

        fm.update({
            "last_check"       : now_str,
            "status"           : new_status,
            "interval_hours"   : new_interval,
            "consecutive_empty": consecutive_empty,
            "next_check"       : next_check_new,
            "findings_count"   : findings_count,
            "tags"             : ["tracker", new_status],
        })
        if relevant:
            fm["last_activity"] = date_str

        # ── 追加发现到 body ───────────────────────────────────────
        if relevant:
            links = "\n".join(
                f"- [{r.get('title', r['url'])}]({r['url']})"
                + (f" — {r['_summary']}" if r.get("_summary") else "")
                for r in relevant
            )
            if "## 后续发现" not in body:
                body += "\n\n## 后续发现\n"
            body += f"\n### {date_str}\n{links}\n"

        # ── 写回事件文件 ──────────────────────────────────────────
        write_md(event_path, fm, body)

        # ── 创建 finding 文件 ─────────────────────────────────────
        for i, f in enumerate(relevant, 1):
            fname = create_finding_file(event_id, f, date_str, i)
            print(f"   Finding: {fname}")

        # ── Slack 通知 ────────────────────────────────────────────
        if relevant:
            post_slack(title, relevant, old_status, new_status, next_check_new)
            events_with_findings.append(event_id)

        print(f"   {old_status} → {new_status} | empty={consecutive_empty} | next={next_check_new}")

    # ── 汇总报告 ──────────────────────────────────────────────────
    print(f"\n{'═' * 50}")
    print(f"Checked : {checked}")
    print(f"Findings: {len(events_with_findings)} event(s) — {', '.join(events_with_findings) or 'none'}")
    print(f"Skipped : {skipped_not_due} not-due + {skipped_closed} CLOSED")
    print("Done.")


if __name__ == "__main__":
    run()
