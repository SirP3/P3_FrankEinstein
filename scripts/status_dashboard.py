#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def run(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout.strip()

def section(title: str) -> None:
    print()
    print("## " + title)
    print("-" * (len(title) + 3))

def main() -> None:
    print("P3FE v0.2 Status Dashboard")
    print("==========================")

    section("Git")
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--short"])
    last_commit = run(["git", "log", "--oneline", "-1"])
    print("Branch:", branch or "unknown")
    print("Last commit:", last_commit or "none")
    print("Working tree:", "clean" if not status else "has changes")
    if status:
        print(status)

    section("Safety audit")
    audit = run(["python3", "scripts/safety/public_safety_audit.py"])
    print(audit)

    section("YTM local runs")
    runs = run(["python3", "apps/youtube_mining/scripts/list_runs.py"])
    print(runs)

    section("Workspace zones")
    for folder in ["00_STEM_CELL", "apps", "docs", "scripts", "private", "output", "quarantine", "donor"]:
        path = ROOT / folder
        print(f"{folder}/:", "exists" if path.exists() else "missing")

if __name__ == "__main__":
    main()
