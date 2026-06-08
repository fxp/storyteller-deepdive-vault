#!/usr/bin/env python3
"""
StoryTeller Dashboard Generator  v2
- 只展示 RELEVANT 新发现
- 用 BigModel GLM 将近期发现合成叙述性进展摘要（而非 brief 列表）
- 每次监控跑完自动调用
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
import yaml

VAULT        = Path(os.environ.get("VAULT", Path(__file__).parent.parent))
EVENTS_DIR   = VAULT / "events"
FINDINGS_DIR = VAULT / "findings"
OUTPUT       = VAULT / "dashboard.html"

BIGMODEL_API_KEY = os.environ.get("BIGMODEL_API_KEY", "")

STATUS_ORDER = ["HOT", "ACTIVE", "TRACKING", "WATCHING", "COOLING", "DORMANT", "CLOSED"]

# 按状态决定"近期"窗口（天）和历史上下文条数
RECENCY_DAYS = {
    "HOT":      5,
    "ACTIVE":   10,
    "TRACKING": 21,
    "WATCHING": 30,
    "COOLING":  45,
    "DORMANT":  90,
    "CLOSED":   0,
}
HISTORY_CTX = 10   # 传给 LLM 的历史背景条数（用于避免重复）
MIN_RECENT_FOR_UPDATE = 2   # 至少这么多近期发现才合成摘要

STATUS_COLORS = {
    "HOT":      ("#ff4d4d", "#3a1010"),
    "ACTIVE":   ("#f59e0b", "#2a1f08"),
    "TRACKING": ("#60a5fa", "#0d1f3a"),
    "WATCHING": ("#a78bfa", "#1a1030"),
    "COOLING":  ("#6ee7b7", "#0a2a20"),
    "DORMANT":  ("#94a3b8", "#1e2530"),
    "CLOSED":   ("#64748b", "#181d25"),
}


# ══════════════════════════════════════════════════════════════════
# 数据读取
# ══════════════════════════════════════════════════════════════════

def parse_md(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                return fm, parts[2].strip()
            except yaml.YAMLError:
                pass
    return {}, text


def extract_summary(body: str) -> str:
    """从 finding body 提取摘要段落"""
    m = re.search(r"## 摘要\s*\n+([\s\S]+?)(?=\n##|\Z)", body)
    if m:
        text = m.group(1).strip()
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        return text.strip()
    return ""


def source_name(url: str, fallback: str = "") -> str:
    """从 URL 提取可读的来源名称，用于内联引用"""
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
        host = re.sub(r"^www\.", "", host)
        # 常见媒体映射
        KNOWN = {
            "thenextweb.com": "The Next Web",
            "the-decoder.com": "The Decoder",
            "seekingalpha.com": "Seeking Alpha",
            "trendforce.com": "TrendForce",
            "esmchina.com": "国际电子商情",
            "pconline.com.cn": "太平洋电脑网",
            "163.com": "网易",
            "huxiu.com": "虎嗅",
            "cnbc.com": "CNBC",
            "bnnbloomberg.ca": "BNN Bloomberg",
            "firstpost.com": "Firstpost",
            "storyboard18.com": "Storyboard18",
            "alphaspread.com": "Alpha Spread",
            "siliconrepublic.com": "Silicon Republic",
            "qz.com": "Quartz",
            "hrtechedge.com": "HR Tech Edge",
            "blackstone.com": "Blackstone",
            "marketsmedia.com": "Markets Media",
            "chromestatus.com": "Chrome Platform Status",
            "developer.chrome.com": "Chrome Developers",
            "web.dev": "web.dev",
            "linkedin.com": "LinkedIn",
            "reddit.com": "Reddit",
            "youtube.com": "YouTube",
            "facebook.com": "Facebook",
            "instagram.com": "Instagram",
            "x.com": "X",
            "twitter.com": "X",
            "github.com": "GitHub",
            "fortune.com": "Fortune",
            "techcrunch.com": "TechCrunch",
            "bloomberg.com": "Bloomberg",
            "reuters.com": "Reuters",
            "wsj.com": "WSJ",
            "ft.com": "FT",
            "anthropic.com": "Anthropic",
            "openai.com": "OpenAI",
            "finance.yahoo.com": "Yahoo Finance",
        }
        if host in KNOWN:
            return KNOWN[host]
        # 自动美化：去掉 .com 等后缀，首字母大写
        base = host.split(".")[0]
        return base.replace("-", " ").title()
    except Exception:
        return fallback or url


def load_events() -> list[dict]:
    events = []
    for f in sorted(EVENTS_DIR.glob("*.md")):
        fm, body = parse_md(f)
        if not fm:
            continue
        fm["_path"] = f
        fm["_id"]   = str(fm.get("id") or f.stem)
        fm["_body"] = body
        events.append(fm)

    def sort_key(e):
        status = str(e.get("status", "DORMANT"))
        order  = STATUS_ORDER.index(status) if status in STATUS_ORDER else 99
        return (order, str(e.get("last_activity", "2000-01-01")))

    events.sort(key=sort_key)
    return events


def load_relevant_findings(event_id: str) -> list[dict]:
    """
    加载该事件所有 RELEVANT 发现，按日期倒序。
    若已有 quality 字段，LOW 排到后面（不丢弃，但降优先级）。
    """
    all_f = []
    for f in FINDINGS_DIR.glob(f"*-{event_id}-*.md"):
        fm, body = parse_md(f)
        if fm and str(fm.get("relevance", "")) == "RELEVANT":
            fm["_body"]    = body
            fm["_summary"] = extract_summary(body)
            all_f.append(fm)

    quality_order = {"HIGH": 0, "OK": 1, "LOW": 2, "": 1}
    all_f.sort(key=lambda x: (
        quality_order.get(str(x.get("quality", "")), 1),
        str(x.get("date", "2000-01-01"))
    ), reverse=True)
    # 同一日期内，HIGH 排前；跨日期，最新排前 → 二级排序取反
    all_f.sort(key=lambda x: (
        str(x.get("date", "2000-01-01")),
        -quality_order.get(str(x.get("quality", "")), 1)
    ), reverse=True)
    return all_f


def split_recent_vs_history(findings: list[dict], days: int) -> tuple[list, list]:
    """按天数切分近期 / 历史"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent  = [f for f in findings if str(f.get("date", "")) >= cutoff]
    history = [f for f in findings if str(f.get("date", "")) < cutoff]
    return recent, history


# ══════════════════════════════════════════════════════════════════
# BigModel 合成
# ══════════════════════════════════════════════════════════════════

FILTER_MODEL = "glm-5.1"      # 推理模型：价值筛选（需要判断力）
SYNTH_MODEL  = "glm-4-flash"  # 高效模型：文本合成（需要干净输出）


def _call_glm(prompt: str, max_tokens: int = 800, temperature: float = 0.4,
              model: str = None) -> str:
    """统一 GLM API 调用，返回原始文本，失败抛异常。

    reasoning_content fallback 只对推理模型（glm-5.x）生效：
    这类模型 content 字段为空，答案在 reasoning_content 的最后段落里。
    合成模型（glm-4-flash 等）直接使用 content。
    """
    used_model = model or SYNTH_MODEL
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {BIGMODEL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": used_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    msg  = resp.json()["choices"][0]["message"]
    text = (msg.get("content") or "").strip()
    # 推理模型（glm-5.x）：content 通常为空，答案在 reasoning_content
    if not text and used_model.startswith("glm-5"):
        text = (msg.get("reasoning_content") or "").strip()
    return text


def filter_valuable(
    event_title: str,
    findings: list[dict],
    history: list[dict],
) -> list[dict]:
    """
    用 GLM-5.1 对近期发现做价值评估，返回真正有新信息的子集。
    评估标准：是否包含历史背景中没有的新事实、新数据、新行为者、新因果关系。
    """
    if not findings or not BIGMODEL_API_KEY:
        return findings

    def fmt(i, f):
        name    = source_name(str(f.get("url","")), str(f.get("source_title","")))
        summary = f.get("_summary", "")
        return f"{i}. [{name}]：{summary}"

    items_block   = "\n".join(fmt(i, f) for i, f in enumerate(findings))
    history_block = "\n".join(f"- {f.get('_summary','')}" for f in history[:HISTORY_CTX])

    prompt = f"""你是信息质量评审员，正在为课题「{event_title}」筛选近期发现。

判断标准：一条发现"有价值"，当且仅当它包含以下至少一项：
- 历史背景中未出现的新事实或新数据
- 新的行为者、机构、决策
- 事态的实质性进展或反转
- 具体数字、时间节点、合同/协议细节

"无价值"的情形：重复已知事实、仅转载旧新闻、泛泛评论、无具体信息。

【待评估发现（编号 0 开始）】
{items_block}

【已知历史背景（用于比对是否重复）】
{history_block if history_block else "（无）"}

请只输出有价值的发现编号，用逗号分隔，例如：0,2,4
不要输出任何解释，只输出编号列表："""

    try:
        raw = _call_glm(prompt, max_tokens=100, temperature=0.1, model=FILTER_MODEL)
        # 解析编号：推理模型可能在末尾输出 "0,2,4" 或 "有价值：0, 2, 4"
        # 优先取最后一行含数字的行（推理链末行最可信）
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        target = raw  # 默认全文搜索
        for ln in reversed(lines):
            if re.search(r"\d", ln):
                target = ln
                break
        indices = [int(x) for x in re.findall(r"\d+", target)]
        # 去重并过滤越界
        seen_idx = set()
        valuable = []
        for i in indices:
            if 0 <= i < len(findings) and i not in seen_idx:
                seen_idx.add(i)
                valuable.append(findings[i])
        dropped  = len(findings) - len(valuable)
        if dropped:
            print(f"    Value filter: {len(findings)} → {len(valuable)} (dropped {dropped})")
        return valuable if valuable else findings  # 全被过滤时兜底保留原列表
    except Exception as e:
        print(f"  [WARN] value filter failed: {e}, using all findings")
        return findings


def synthesize_update(
    event_title: str,
    status: str,
    recent: list[dict],
    history: list[dict],
) -> str:
    """
    用 GLM-4-Flash 将近期高价值发现合成为叙述性进展摘要。
    返回 HTML 字符串（内联来源链接）。
    """
    if not BIGMODEL_API_KEY:
        return _fallback_list(recent)

    # 先做价值筛选
    valuable = filter_valuable(event_title, recent, history)

    def fmt_finding(f):
        url  = str(f.get("url", ""))
        name = source_name(url, str(f.get("source_title", "")))
        summ = f.get("_summary", "")
        ref  = f"[{name}]({url})" if url else name
        return f"{ref}：{summ}"

    recent_block  = "\n".join(f"- {fmt_finding(f)}" for f in valuable[:12])
    history_block = "\n".join(f"- {f.get('_summary','')}" for f in history[:HISTORY_CTX])

    prompt = f"""你是 AI 行业分析师，追踪课题「{event_title}」。

请根据下方已筛选的高价值发现，写一段 150～220 字的中文话题进展：
1. 以话题为主语，写观点和实质变化，不转述新闻标题
2. 每引用信源，必须将链接内联在句子里，格式：[媒体名](URL)
   示例：[TechCrunch](https://...) 确认，NSA 已将 Mythos 纳入网络行动规划。
3. 不要 bullet list 或标题，只输出流畅中文段落
4. 不重复历史已知事实
5. 结尾可用「——」提出 1～2 个值得关注的问题

【高价值发现】（直接复用括号内链接）
{recent_block}

【历史背景（勿重复）】
{history_block if history_block else "（无）"}

话题进展："""

    try:
        text = _call_glm(prompt, max_tokens=700, temperature=0.5, model=SYNTH_MODEL)
        # 清理多余 markdown，但保留 [name](url)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*",     r"\1", text)
        return md_links_to_html(text)
    except Exception as e:
        print(f"  [WARN] synthesis failed: {e}")
        return _fallback_list(recent)


def _fallback_list(findings: list[dict]) -> str:
    """API 失败时退化为简单列表"""
    items = []
    for f in findings[:6]:
        url   = str(f.get("url", ""))
        title = esc(str(f.get("source_title", url)))
        summ  = esc(f.get("_summary", ""))
        date  = esc(str(f.get("date", "")))
        link  = f'<a href="{esc(url)}" target="_blank" rel="noopener">{title}</a>' if url else title
        items.append(f'<li class="fb-item"><span class="fb-date">{date}</span> {link}{"：" + summ if summ else ""}</li>')
    return f'<ul class="fallback-list">{"".join(items)}</ul>'


# ══════════════════════════════════════════════════════════════════
# HTML 渲染
# ══════════════════════════════════════════════════════════════════

def esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _render_sources(findings: list[dict], max_n: int = 8) -> str:
    """始终在摘要下方显示的来源链接列表"""
    items = []
    seen  = set()
    for f in findings[:max_n]:
        url  = str(f.get("url", ""))
        name = source_name(url, str(f.get("source_title", url)))
        date = str(f.get("date", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        items.append(
            f'<a class="src-pill" href="{esc(url)}" target="_blank" rel="noopener">'
            f'<span class="src-date">{esc(date)}</span>{esc(name)}'
            f'</a>'
        )
    if not items:
        return ""
    return '<div class="src-row">' + "".join(items) + "</div>"


def md_links_to_html(text: str) -> str:
    """
    把 LLM 输出中的 [Name](url) 转成 HTML <a>，
    其余文本做 HTML 转义（防 XSS）。
    """
    # 先切分：普通文本段 vs [name](url) 段
    pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
    parts   = []
    last    = 0
    for m in pattern.finditer(text):
        # 转义普通文本
        parts.append(esc(text[last:m.start()]))
        name = esc(m.group(1))
        url  = esc(m.group(2))
        parts.append(f'<a href="{url}" target="_blank" rel="noopener" class="inline-src">{name}</a>')
        last = m.end()
    parts.append(esc(text[last:]))
    return "".join(parts)


def render_card(ev: dict) -> str:
    event_id = ev["_id"]
    title    = esc(str(ev.get("title", event_id)))
    status   = str(ev.get("status", "DORMANT"))
    findings_count = int(ev.get("findings_count", 0))
    last_activity  = str(ev.get("last_activity", ev.get("last_check", "")[:10]))
    interval_hours = int(ev.get("interval_hours", 6))

    color_fg, color_bg = STATUS_COLORS.get(status, ("#94a3b8", "#1e2530"))
    is_hot  = status == "HOT"
    pulse   = '<span class="pulse-dot"></span>' if is_hot else ""

    # 加载发现并分层
    days        = RECENCY_DAYS.get(status, 14)
    all_relevant = load_relevant_findings(event_id)
    recent, history = split_recent_vs_history(all_relevant, days)

    # 实体 chips
    entities = ev.get("entities") or {}
    chips_html = ""
    if isinstance(entities, dict):
        chips = []
        for p in (entities.get("people") or [])[:3]:
            chips.append(f'<span class="chip chip-person">{esc(str(p))}</span>')
        for o in (entities.get("orgs") or [])[:3]:
            chips.append(f'<span class="chip chip-org">{esc(str(o))}</span>')
        if chips:
            chips_html = f'<div class="chips">{"".join(chips[:5])}</div>'

    # ── 核心内容区 ──
    if recent:
        if len(recent) >= MIN_RECENT_FOR_UPDATE:
            print(f"  Synthesizing update for {event_id} ({len(recent)} recent, {len(history)} history)...")
            synopsis = synthesize_update(ev.get("title",""), status, recent, history)
        else:
            # 只有 1 条，直接展示摘要（内联来源链接）
            f0  = recent[0]
            url = str(f0.get("url",""))
            nm  = source_name(url, str(f0.get("source_title","")))
            summ = esc(f0.get("_summary",""))
            link = f'<a href="{esc(url)}" target="_blank" rel="noopener" class="inline-src">{esc(nm)}</a>' if url else esc(nm)
            synopsis = f"{link} 报道，{summ}" if summ else link

        sources_html = _render_sources(recent)
        content_html = f'<div class="synopsis">{synopsis}</div>{sources_html}'
    else:
        window_label = f"{days} 天内" if days else "—"
        content_html = f'<div class="no-update">近 {window_label} 暂无新发现</div>'

    recent_count = len(recent)

    return f"""
    <div class="card" data-status="{esc(status)}">
      <div class="card-header">
        <div class="card-title-row">
          <h2 class="card-title">{title}</h2>
          <span class="badge" style="color:{color_fg};background:{color_bg}">{pulse}{esc(status)}</span>
        </div>
        {chips_html}
        <div class="card-meta">
          <span>📄 {findings_count} 条发现</span>
          <span>🆕 近期 {recent_count} 条</span>
          <span>🕐 {esc(last_activity)}</span>
          <span>🔄 每 {interval_hours}h</span>
        </div>
      </div>
      <div class="card-body">
        {content_html}
      </div>
    </div>"""


def generate(events: list[dict]) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_findings = sum(int(e.get("findings_count", 0)) for e in events)
    hot_count = sum(1 for e in events if str(e.get("status")) == "HOT")

    print(f"\nGenerating dashboard for {len(events)} events...")
    cards_html = "\n".join(render_card(e) for e in events)

    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StoryTeller — AI 事件追踪</title>
<style>
  :root {{
    --bg:          #0d0d12;
    --surface:     #13131a;
    --card:        #17171f;
    --border:      #1e1e2e;
    --border-hi:   #2e2e42;
    --text:        #e2e8f0;
    --text-dim:    #94a3b8;
    --text-muted:  #64748b;
    --accent:      #6366f1;
    --hot:         #ef4444;
    --font-mono:   'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
    font-size: 14px;
    line-height: 1.7;
    min-height: 100vh;
  }}

  /* ── Header ── */
  .header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .header-left h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }}
  .header-left p  {{ color: var(--text-muted); font-size: 12px; margin-top: 2px; }}
  .stats {{ display: flex; gap: 24px; }}
  .stat {{ text-align: center; }}
  .stat-value {{ font-size: 22px; font-weight: 700; font-family: var(--font-mono); }}
  .stat-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .live-badge {{
    display: flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.25);
    border-radius: 999px; padding: 4px 12px;
    font-size: 12px; color: var(--hot); font-weight: 600;
  }}

  /* ── Grid ── */
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(520px, 1fr));
    gap: 20px;
    padding: 24px 32px;
    max-width: 1600px;
    margin: 0 auto;
  }}

  /* ── Card ── */
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: border-color 0.2s;
  }}
  .card:hover {{ border-color: var(--border-hi); }}
  .card[data-status="HOT"]    {{ border-color: rgba(239,68,68,.22); }}
  .card[data-status="ACTIVE"] {{ border-color: rgba(245,158,11,.15); }}

  .card-header {{
    padding: 18px 20px 14px;
    border-bottom: 1px solid var(--border);
  }}
  .card-title-row {{
    display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px;
  }}
  .card-title {{
    font-size: 15px; font-weight: 600; flex: 1; line-height: 1.4;
  }}
  .badge {{
    display: flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 700;
    padding: 3px 9px; border-radius: 6px;
    white-space: nowrap; flex-shrink: 0;
    font-family: var(--font-mono); letter-spacing: 0.5px;
  }}
  .pulse-dot {{
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%; background: #ef4444;
    animation: pulse 1.8s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.4; transform: scale(0.7); }}
  }}

  .chips {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }}
  .chip {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
  .chip-person {{ background: rgba(139,92,246,.15); color: #a78bfa; }}
  .chip-org    {{ background: rgba(59,130,246,.15);  color: #60a5fa; }}

  .card-meta {{ display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--text-muted); }}

  /* ── Card body ── */
  .card-body {{ padding: 18px 20px 20px; flex: 1; display: flex; flex-direction: column; gap: 14px; }}

  /* 合成摘要 */
  .synopsis {{
    font-size: 14px;
    color: var(--text-dim);
    line-height: 1.9;
  }}

  /* 内联来源引用链接 */
  .inline-src {{
    color: var(--text-dim);
    text-decoration: none;
    border-bottom: 1px solid var(--border-hi);
    transition: color 0.12s, border-color 0.12s;
  }}
  .inline-src:hover {{
    color: var(--text);
    border-color: var(--accent);
  }}

  /* 来源链接行（始终显示） */
  .src-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    margin-top: 4px;
  }}
  .src-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--text-muted);
    background: rgba(255,255,255,.03);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 2px 8px;
    text-decoration: none;
    transition: color 0.12s, border-color 0.12s;
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .src-pill:hover {{ color: var(--text-dim); border-color: var(--border-hi); }}
  .src-date {{
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-muted);
    opacity: 0.7;
    flex-shrink: 0;
  }}

  .no-update {{
    font-size: 13px; color: var(--text-muted); font-style: italic; padding: 8px 0;
  }}

  /* fallback list */
  .fallback-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
  .fb-item {{ font-size: 13px; color: var(--text-dim); }}
  .fb-item a {{ color: var(--text-dim); text-decoration: none; border-bottom: 1px solid var(--border-hi); }}
  .fb-item a:hover {{ color: var(--text); }}
  .fb-date {{ font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); margin-right: 4px; }}

  /* ── Footer ── */
  .footer {{
    text-align: center; padding: 24px; color: var(--text-muted);
    font-size: 12px; border-top: 1px solid var(--border);
  }}
  .footer a {{ color: var(--text-muted); }}

  @media (max-width: 600px) {{
    .header {{ padding: 16px; }}
    .grid   {{ padding: 16px; grid-template-columns: 1fr; }}
    .stats  {{ gap: 16px; }}
  }}
</style>
</head>
<body>

<header class="header">
  <div class="header-left">
    <h1>🔭 StoryTeller</h1>
    <p>AI 事件持续追踪 · 更新于 {esc(now_utc)}</p>
  </div>
  <div class="stats">
    <div class="stat">
      <div class="stat-value">{len(events)}</div>
      <div class="stat-label">追踪事件</div>
    </div>
    <div class="stat">
      <div class="stat-value">{total_findings}</div>
      <div class="stat-label">总发现数</div>
    </div>
    <div class="stat">
      <div class="stat-value">{hot_count}</div>
      <div class="stat-label">HOT</div>
    </div>
  </div>
  <div class="live-badge">
    <span class="pulse-dot"></span>
    每小时自动更新
  </div>
</header>

<main class="grid">
{cards_html}
</main>

<footer class="footer">
  <a href="https://github.com/fxp/storyteller-deepdive-vault" target="_blank">GitHub</a>
  &nbsp;·&nbsp; 情报合成由 BigModel GLM-5.1 × GLM-4-Flash 驱动 · 搜索由 Tavily 提供
</footer>

</body>
</html>"""


if __name__ == "__main__":
    events = load_events()
    html   = generate(events)
    OUTPUT.write_text(html, encoding="utf-8")
    total = sum(int(e.get("findings_count", 0)) for e in events)
    print(f"\nDashboard → {OUTPUT}  ({len(events)} events, {total} findings)")
