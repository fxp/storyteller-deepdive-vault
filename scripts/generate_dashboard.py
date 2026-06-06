#!/usr/bin/env python3
"""
StoryTeller Dashboard Generator
从 events/ 和 findings/ 目录读取数据，生成 dashboard.html
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

import yaml

VAULT = Path(os.environ.get("VAULT", Path(__file__).parent.parent))
EVENTS_DIR   = VAULT / "events"
FINDINGS_DIR = VAULT / "findings"
OUTPUT       = VAULT / "dashboard.html"

# ── 状态配置 ─────────────────────────────────────────────────────

STATUS_ORDER  = ["HOT", "ACTIVE", "TRACKING", "WATCHING", "COOLING", "DORMANT", "CLOSED"]
STATUS_COLORS = {
    "HOT":      ("#ff4d4d", "#3a1010"),
    "ACTIVE":   ("#f59e0b", "#2a1f08"),
    "TRACKING": ("#60a5fa", "#0d1f3a"),
    "WATCHING": ("#a78bfa", "#1a1030"),
    "COOLING":  ("#6ee7b7", "#0a2a20"),
    "DORMANT":  ("#94a3b8", "#1e2530"),
    "CLOSED":   ("#64748b", "#181d25"),
}

# ── 解析 ─────────────────────────────────────────────────────────

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


def load_events() -> list[dict]:
    events = []
    for f in sorted(EVENTS_DIR.glob("*.md")):
        fm, _ = parse_md(f)
        if not fm:
            continue
        fm["_path"] = f
        fm["_id"]   = str(fm.get("id") or f.stem)
        events.append(fm)

    def sort_key(e):
        status = str(e.get("status", "DORMANT"))
        order  = STATUS_ORDER.index(status) if status in STATUS_ORDER else 99
        activity = str(e.get("last_activity", "2000-01-01"))
        return (order, activity)

    events.sort(key=sort_key)
    return events


def load_findings_for(event_id: str, limit: int = 8) -> list[dict]:
    prefix = FINDINGS_DIR
    all_findings = []
    for f in prefix.glob(f"*-{event_id}-*.md"):
        fm, body = parse_md(f)
        if fm:
            fm["_body"] = body
            all_findings.append(fm)
    # 按日期倒序
    all_findings.sort(key=lambda x: str(x.get("date", "2000-01-01")), reverse=True)
    return all_findings[:limit]


# ── HTML 生成 ─────────────────────────────────────────────────────

def esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def render_finding(f: dict) -> str:
    url   = str(f.get("url", ""))
    title = esc(str(f.get("source_title", url or "未知来源")))
    date  = str(f.get("date", ""))

    # 摘要：从 body 里取 ## 摘要 段落
    body  = f.get("_body", "")
    summary = ""
    m = re.search(r"## 摘要\s*\n+([\s\S]+?)(?=\n##|\Z)", body)
    if m:
        summary = m.group(1).strip()
        # 去掉 markdown 链接
        summary = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", summary)
        summary = esc(summary[:200])

    link_open  = f'<a href="{esc(url)}" target="_blank" rel="noopener">' if url else "<span>"
    link_close = "</a>" if url else "</span>"

    return f"""
      <div class="finding">
        <div class="finding-meta">
          <span class="finding-date">{esc(date)}</span>
          {link_open}<span class="finding-title">{title}</span>{link_close}
        </div>
        {f'<div class="finding-summary">{summary}</div>' if summary else ""}
      </div>"""


def render_event_card(ev: dict) -> str:
    event_id  = ev["_id"]
    title     = esc(str(ev.get("title", event_id)))
    status    = str(ev.get("status", "DORMANT"))
    findings_count = int(ev.get("findings_count", 0))
    last_activity  = str(ev.get("last_activity", ""))
    last_check     = str(ev.get("last_check", ""))

    color_fg, color_bg = STATUS_COLORS.get(status, ("#94a3b8", "#1e2530"))
    is_hot = status == "HOT"
    pulse  = '<span class="pulse-dot"></span>' if is_hot else ""

    findings = load_findings_for(event_id, limit=8)
    findings_html = "".join(render_finding(f) for f in findings) if findings else \
        '<div class="no-findings">暂无最新发现</div>'

    interval = int(ev.get("interval_hours", 6))
    interval_label = f"每 {interval}h 检查"

    entities = ev.get("entities") or {}
    tags_html = ""
    if isinstance(entities, dict):
        people  = entities.get("people") or []
        orgs    = entities.get("orgs") or []
        tags = [(p, "person") for p in people[:3]] + [(o, "org") for o in orgs[:3]]
        chips = "".join(
            f'<span class="chip chip-{kind}">{esc(str(name))}</span>'
            for name, kind in tags[:5]
        )
        if chips:
            tags_html = f'<div class="chips">{chips}</div>'

    return f"""
    <div class="card" data-status="{esc(status)}">
      <div class="card-header">
        <div class="card-title-row">
          <h2 class="card-title">{title}</h2>
          <span class="badge" style="color:{color_fg};background:{color_bg}">{pulse}{esc(status)}</span>
        </div>
        {tags_html}
        <div class="card-meta">
          <span>📄 {findings_count} 条发现</span>
          <span>🕐 {esc(last_activity) or esc(last_check[:10])}</span>
          <span>🔄 {interval_label}</span>
        </div>
      </div>
      <div class="findings-list">
        {findings_html}
      </div>
    </div>"""


def generate(events: list[dict]) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_findings = sum(int(e.get("findings_count", 0)) for e in events)
    hot_count = sum(1 for e in events if str(e.get("status")) == "HOT")
    active_count = sum(1 for e in events if str(e.get("status")) in ("HOT","ACTIVE"))

    cards_html = "\n".join(render_event_card(e) for e in events)

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
    --border-bright: #2e2e42;
    --text:        #e2e8f0;
    --text-dim:    #94a3b8;
    --text-muted:  #64748b;
    --accent:      #6366f1;
    --hot:         #ef4444;
    --font-mono:   'JetBrains Mono', 'Fira Code', monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
    font-size: 14px;
    line-height: 1.6;
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
  .header-left h1 {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
  }}
  .header-left p {{
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 2px;
  }}
  .stats {{
    display: flex;
    gap: 24px;
  }}
  .stat {{
    text-align: center;
  }}
  .stat-value {{
    font-size: 22px;
    font-weight: 700;
    font-family: var(--font-mono);
    color: var(--text);
  }}
  .stat-label {{
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .live-badge {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(239,68,68,.12);
    border: 1px solid rgba(239,68,68,.3);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--hot);
    font-weight: 600;
  }}

  /* ── Grid ── */
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
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
  .card:hover {{ border-color: var(--border-bright); }}
  .card[data-status="HOT"] {{ border-color: rgba(239,68,68,.25); }}

  .card-header {{
    padding: 18px 20px 14px;
    border-bottom: 1px solid var(--border);
  }}
  .card-title-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
  }}
  .card-title {{
    font-size: 15px;
    font-weight: 600;
    flex: 1;
    line-height: 1.4;
  }}
  .badge {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    white-space: nowrap;
    flex-shrink: 0;
    font-family: var(--font-mono);
    letter-spacing: 0.5px;
  }}

  /* ── Pulse animation ── */
  .pulse-dot {{
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ef4444;
    animation: pulse 1.8s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.4; transform: scale(0.7); }}
  }}

  /* ── Chips ── */
  .chips {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }}
  .chip {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
  }}
  .chip-person {{ background: rgba(139,92,246,.15); color: #a78bfa; }}
  .chip-org    {{ background: rgba(59,130,246,.15);  color: #60a5fa; }}

  .card-meta {{
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text-muted);
  }}

  /* ── Findings ── */
  .findings-list {{
    flex: 1;
    padding: 12px 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .finding {{
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }}
  .finding:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .finding-meta {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .finding-date {{
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    flex-shrink: 0;
  }}
  .finding-title {{
    font-size: 13px;
    font-weight: 500;
    color: var(--text-dim);
    line-height: 1.3;
  }}
  .finding-meta a {{
    text-decoration: none;
    border-bottom: 1px solid var(--border-bright);
    transition: color 0.12s, border-color 0.12s;
  }}
  .finding-meta a:hover .finding-title {{
    color: var(--text);
    border-color: var(--text-dim);
  }}
  .finding-meta a:hover {{ border-color: var(--text-dim); }}
  .finding-summary {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
    line-height: 1.5;
  }}
  .no-findings {{
    font-size: 13px;
    color: var(--text-muted);
    font-style: italic;
    padding: 8px 0;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    padding: 24px;
    color: var(--text-muted);
    font-size: 12px;
    border-top: 1px solid var(--border);
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
  &nbsp;·&nbsp; 数据由 BigModel GLM-4-Flash + Tavily 驱动
</footer>

</body>
</html>"""


if __name__ == "__main__":
    events = load_events()
    html   = generate(events)
    OUTPUT.write_text(html, encoding="utf-8")
    total = sum(int(e.get("findings_count", 0)) for e in events)
    print(f"Dashboard generated: {len(events)} events, {total} findings → {OUTPUT}")
