#!/usr/bin/env python3
"""
StoryTeller Vault — 创建 Managed Agent 和 Environment

在 vault repo 根目录运行一次即可：
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 scripts/setup_agent.py

会自动读取 system/monitor-cloud.md 作为 system prompt，
并将 agent_id + environment_id 写回 agent_ids.json。
"""

import json
import os
import sys
from pathlib import Path

import anthropic


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent

    # 读取 system prompt
    prompt_path = repo_root / "system" / "monitor-cloud.md"
    if not prompt_path.exists():
        print(f"ERROR: {prompt_path} not found", file=sys.stderr)
        sys.exit(1)
    system_prompt = prompt_path.read_text(encoding="utf-8")
    print(f"System prompt loaded: {len(system_prompt)} chars from {prompt_path.name}")

    client = anthropic.Anthropic(api_key=api_key)

    # 1. 创建 Agent
    print("\nCreating Managed Agent...")
    agent = client.beta.agents.create(
        name="storyteller-deepdive",
        model={"id": "claude-sonnet-4-5"},
        system=system_prompt,
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"  Agent ID: {agent.id}")

    # 2. 创建 Environment
    print("\nCreating Environment...")
    environment = client.beta.environments.create(
        name="storyteller-deepdive-env",
        config={
            "type": "cloud",
            "packages": {
                "apt": ["git", "curl", "jq"],
            },
            "networking": {
                "type": "unrestricted",
            },
        },
    )
    print(f"  Environment ID: {environment.id}")

    # 3. 保存 IDs
    ids = {
        "agent_id": agent.id,
        "environment_id": environment.id,
        "deployment": "deepdive",
        "model": "claude-sonnet-4-5",
    }
    ids_path = repo_root / "agent_ids.json"
    ids_path.write_text(json.dumps(ids, indent=2, ensure_ascii=False) + "\n")
    print(f"\nSaved to {ids_path}")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("  1. Commit agent_ids.json:  git add agent_ids.json && git commit -m 'chore: add agent IDs'")
    print("  2. Set GitHub repo Secrets (Settings → Secrets → Actions):")
    print("     ANTHROPIC_API_KEY  — your Anthropic API key")
    print("     VAULT_REPO         — https://github.com/YOUR_USER/YOUR_VAULT_REPO")
    print("     VAULT_GITHUB_TOKEN — GitHub PAT with repo write access")
    print("     TAVILY_API_KEY     — your Tavily API key")
    print("     SLACK_WEBHOOK_URL  — your Slack incoming webhook URL")
    print("  3. Enable Actions in the GitHub repo settings")
    print("  4. Test: manually trigger workflow from GitHub Actions tab")


if __name__ == "__main__":
    main()
