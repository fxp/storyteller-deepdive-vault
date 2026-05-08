#!/usr/bin/env python3
"""
StoryTeller — 触发 Managed Agent 监控 session

每次 cron 触发时调用此脚本，它会：
1. 从 agent_ids.json 读取 agent_id + environment_id
2. 在 Anthropic 云端创建一个新 session
3. 发送携带 secrets 的触发消息
4. 流式输出 agent 执行过程，直到 session 结束

用法（由 GitHub Actions 调用，也可本地测试）：
    export ANTHROPIC_API_KEY="..."
    export VAULT_REPO="https://github.com/youruser/storyteller-deepdive-vault"
    export GITHUB_TOKEN="..."
    export TAVILY_API_KEY="..."
    export SLACK_WEBHOOK_URL="..."
    python3 scripts/trigger.py [--deployment deepdive] [--dry-run]
"""

import json
import os
import sys
import argparse
import time
from pathlib import Path

import anthropic


def load_agent_ids(base_dir: Path, deployment: str) -> dict:
    # vault repo: agent_ids.json is at the repo root
    ids_path = base_dir / "agent_ids.json"
    if not ids_path.exists():
        raise FileNotFoundError(
            f"agent_ids.json not found at {ids_path}\n"
            f"Run setup_agent.py first: python3 scripts/setup_agent.py"
        )
    return json.loads(ids_path.read_text())


def build_trigger_message(required_vars: dict) -> str:
    """构建发给 agent 的触发消息，包含所有 secrets。"""
    lines = [
        "请立即执行 StoryTeller 监控工作流。",
        "",
        "以下是本次运行所需的环境变量（在步骤 0 中将其写入 /tmp/.env）：",
        "",
    ]
    for key, value in required_vars.items():
        lines.append(f"- {key}: {value}")
    lines += [
        "",
        "严格按照系统提示中的步骤 0 → Step 1 → ... → Step 10 顺序执行，不要跳过任何步骤。",
        "执行完毕后输出最终报告。",
    ]
    return "\n".join(lines)


def run_session(deployment: str, base_dir: Path, dry_run: bool = False) -> bool:
    """创建并运行一个监控 session，返回是否成功。"""

    # 检查必要的环境变量
    required_env = {
        "VAULT_REPO": os.environ.get("VAULT_REPO"),
        "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN"),
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
        "SLACK_WEBHOOK_URL": os.environ.get("SLACK_WEBHOOK_URL"),
    }
    missing = [k for k, v in required_env.items() if not v]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    ids = load_agent_ids(base_dir, deployment)
    agent_id = ids["agent_id"]
    environment_id = ids["environment_id"]

    print(f"[StoryTeller] Starting session — deployment: {deployment}")
    print(f"  Agent:       {agent_id}")
    print(f"  Environment: {environment_id}")
    print(f"  Vault:       {required_env['VAULT_REPO']}")
    print(f"  Time:        {time.strftime('%Y-%m-%dT%H:%M')}")
    print()

    if dry_run:
        print("[dry-run] Would create session and send trigger message.")
        print("[dry-run] Message preview:")
        print(build_trigger_message(required_env))
        return True

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # 创建 session
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=environment_id,
        title=f"storyteller-{deployment}-{time.strftime('%Y%m%d-%H%M')}",
    )
    print(f"  Session ID:  {session.id}")
    print(f"  Status:      {session.status}")
    print()

    trigger_message = build_trigger_message(required_env)

    # 流式运行：先打开 stream，再发送事件
    print("=" * 60)
    success = False
    try:
        with client.beta.sessions.events.stream(session.id) as stream:
            # 发送触发消息
            client.beta.sessions.events.send(
                session.id,
                events=[
                    {
                        "type": "user.message",
                        "content": [{"type": "text", "text": trigger_message}],
                    }
                ],
            )

            # 处理 streaming events
            for event in stream:
                match event.type:
                    case "agent.message":
                        for block in event.content:
                            if hasattr(block, "text"):
                                print(block.text, end="", flush=True)
                    case "agent.tool_use":
                        tool_name = getattr(event, "name", "unknown")
                        print(f"\n[Tool: {tool_name}]", flush=True)
                    case "agent.tool_result":
                        pass  # 不打印工具结果（避免输出过多）
                    case "session.status_idle":
                        print("\n" + "=" * 60)
                        print("[StoryTeller] Session completed (idle).")
                        success = True
                        break
                    case "session.status_error":
                        print("\n" + "=" * 60)
                        error_msg = getattr(event, "error", "unknown error")
                        print(f"[StoryTeller] Session ERROR: {error_msg}", file=sys.stderr)
                        success = False
                        break
    except KeyboardInterrupt:
        print("\n[StoryTeller] Interrupted by user.")
        success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="Trigger StoryTeller monitoring session")
    parser.add_argument("--deployment", default="deepdive", help="Deployment name (default: deepdive)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without calling API")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY") and not args.dry_run:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    base_dir = Path(__file__).parent.parent
    success = run_session(args.deployment, base_dir, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
