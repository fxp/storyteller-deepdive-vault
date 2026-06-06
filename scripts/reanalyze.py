#!/usr/bin/env python3
"""
StoryTeller — 历史发现批量重分析
用 GLM-5.1 对所有已存储的 findings 重新做价值评估，
给每条发现添加 quality: HIGH / OK / LOW 字段。

运行：
  BIGMODEL_API_KEY=... python3 scripts/reanalyze.py
  BIGMODEL_API_KEY=... python3 scripts/reanalyze.py --dry-run   # 只打印不写文件
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from collections import defaultdict

import requests
import yaml

VAULT        = Path(os.environ.get("VAULT", Path(__file__).parent.parent))
FINDINGS_DIR = VAULT / "findings"
EVENTS_DIR   = VAULT / "events"

BIGMODEL_API_KEY = os.environ.get("BIGMODEL_API_KEY", "")
MODEL            = "glm-5.1"
BATCH_SIZE       = 15   # 每次送给 GLM 的发现数量
SLEEP_BETWEEN    = 1.2  # 批次间隔（秒），避免限速

# ── 解析 ──────────────────────────────────────────────────────────

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


def write_md(path: Path, fm: dict, body: str):
    # yaml.dump 对中文用 allow_unicode
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")


def extract_summary(body: str) -> str:
    m = re.search(r"## 摘要\s*\n+([\s\S]+?)(?=\n##|\Z)", body)
    if m:
        text = m.group(1).strip()
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        return text.strip()
    return ""


# ── GLM 调用 ──────────────────────────────────────────────────────

def call_glm(prompt: str, max_tokens: int = 500) -> str:
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {BIGMODEL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── 批量评估 ──────────────────────────────────────────────────────

QUALITY_LABELS = {"HIGH", "OK", "LOW"}

def evaluate_batch(
    event_title: str,
    event_seed: str,
    batch: list[dict],
    all_summaries: list[str],
) -> dict[int, str]:
    """
    对一批发现做质量评估，返回 {batch_index: quality} 字典。
    quality: HIGH（有实质新洞察）/ OK（有效但平淡）/ LOW（低价值/重复）
    """
    items = "\n".join(
        f"{i}. {b.get('_summary', b.get('source_title', ''))}"
        for i, b in enumerate(batch)
    )
    # 把所有其他已知摘要作为参照（只取前30条避免 prompt 过长）
    other_ctx = "\n".join(f"- {s}" for s in all_summaries[:30] if s)

    prompt = f"""你是信息质量评审员，正在评估课题「{event_title}」的近期发现质量。

【课题种子事件】
{event_seed}

【已知背景摘要（用于判断是否重复）】
{other_ctx if other_ctx else "（无）"}

【待评估发现（编号从 0 开始）】
{items}

请对每条发现打质量标签：
- HIGH：包含历史背景中没有的实质新事实、新数据、新行为者、重要转折
- OK  ：相关且有效，但信息增量有限（背景补充、轻微更新、侧面印证）
- LOW ：基本重复已知事实、泛泛转载、无具体信息、与课题关联薄弱

输出格式（严格按此，每行一条）：
0: HIGH
1: LOW
2: OK
...

只输出编号和标签，不要解释："""

    try:
        raw = call_glm(prompt, max_tokens=200)
        result = {}
        for line in raw.splitlines():
            line = line.strip()
            m = re.match(r"(\d+)\s*[:：]\s*(HIGH|OK|LOW)", line, re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                quality = m.group(2).upper()
                if 0 <= idx < len(batch) and quality in QUALITY_LABELS:
                    result[idx] = quality
        return result
    except Exception as e:
        print(f"    [WARN] evaluate_batch failed: {e}")
        return {}


# ── 主流程 ────────────────────────────────────────────────────────

def load_event_seed(event_id: str) -> tuple[str, str]:
    """返回 (title, seed_summary)"""
    for f in EVENTS_DIR.glob("*.md"):
        fm, body = parse_md(f)
        if str(fm.get("id", f.stem)) == event_id:
            title = str(fm.get("title", event_id))
            # 取种子事件摘要段落
            m = re.search(r"##\s*种子事件[\s\S]+?\*\*摘要\*\*[:：]\s*([\s\S]+?)(?=\n##|\Z)", body)
            seed = m.group(1).strip()[:500] if m else ""
            return title, seed
    return event_id, ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只分析不写文件")
    parser.add_argument("--event", help="只处理指定 event_id")
    args = parser.parse_args()

    if not BIGMODEL_API_KEY:
        print("ERROR: BIGMODEL_API_KEY not set")
        sys.exit(1)

    # 加载所有发现文件，按 event 分组
    by_event: dict[str, list[tuple[Path, dict, str]]] = defaultdict(list)
    for f in sorted(FINDINGS_DIR.glob("*.md")):
        fm, body = parse_md(f)
        if not fm:
            continue
        # 从文件名推断 event_id
        name = f.stem  # e.g. 20260606-trump-china-visit-ai-20260513-001
        # 去掉日期前缀和末尾 -NNN
        m = re.match(r"^\d{8}-(.+)-\d{3}$", name)
        event_id = m.group(1) if m else str(fm.get("event", "")).strip("[]").replace("[[","").replace("]]","")
        if not event_id:
            continue
        fm["_summary"] = extract_summary(body)
        fm["_path"]    = f
        by_event[event_id].append((f, fm, body))

    if args.event:
        by_event = {k: v for k, v in by_event.items() if k == args.event}

    total_files   = sum(len(v) for v in by_event.values())
    updated_count = 0
    stats = defaultdict(lambda: defaultdict(int))  # event → quality → count

    print(f"\n{'='*60}")
    print(f"GLM-5.1 质量重分析  ({total_files} 条发现，{len(by_event)} 个事件)")
    print(f"Dry-run: {args.dry_run}")
    print(f"{'='*60}\n")

    for event_id, entries in sorted(by_event.items()):
        event_title, event_seed = load_event_seed(event_id)
        print(f"\n── {event_id} ({len(entries)} 条) ──")

        # 所有摘要（用于上下文去重参照）
        all_summaries = [fm.get("_summary", "") for _, fm, _ in entries if fm.get("_summary")]

        # 按批处理
        for batch_start in range(0, len(entries), BATCH_SIZE):
            batch_entries = entries[batch_start: batch_start + BATCH_SIZE]
            batch_fms     = [fm for _, fm, _ in batch_entries]

            # 传入"其他所有发现"作为背景，排除本批
            other_summaries = [
                fm.get("_summary", "")
                for _, fm, _ in entries
                if fm not in batch_fms and fm.get("_summary")
            ]

            print(f"  Batch {batch_start//BATCH_SIZE + 1}: items {batch_start}–{batch_start+len(batch_entries)-1}", end=" ")
            results = evaluate_batch(event_title, event_seed, batch_fms, other_summaries)
            print(f"→ {results}")

            for i, (fpath, fm, body) in enumerate(batch_entries):
                quality = results.get(i, "OK")  # 未返回时默认 OK
                stats[event_id][quality] += 1

                old_quality = str(fm.get("quality", ""))
                if old_quality != quality:
                    updated_count += 1
                    if not args.dry_run:
                        fm_out = {k: v for k, v in fm.items() if not k.startswith("_")}
                        fm_out["quality"] = quality
                        write_md(fpath, fm_out, body)

            if batch_start + BATCH_SIZE < len(entries):
                time.sleep(SLEEP_BETWEEN)

        # 事件统计
        s = stats[event_id]
        total_e = sum(s.values())
        print(f"  结果: HIGH={s['HIGH']} OK={s['OK']} LOW={s['LOW']} / {total_e} 条")

    print(f"\n{'='*60}")
    print(f"完成: {total_files} 条发现，{updated_count} 条写入质量标签")
    if args.dry_run:
        print("（dry-run 模式，未写入文件）")
    print(f"{'='*60}\n")

    # 汇总
    all_high = sum(s["HIGH"] for s in stats.values())
    all_ok   = sum(s["OK"]   for s in stats.values())
    all_low  = sum(s["LOW"]  for s in stats.values())
    print(f"全局: HIGH={all_high}  OK={all_ok}  LOW={all_low}")


if __name__ == "__main__":
    main()
