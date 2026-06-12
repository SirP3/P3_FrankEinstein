#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

BLOCKED_PATHS = [
    "private/",
    "output/",
    "quarantine/",
    "donor/",
    "transcripts/",
]

SENSITIVE_PATTERNS = [
    r"password",
    r"passwd",
    r"secret",
    r"api[_-]?key",
    r"private[_-]?key",
    r"client[_-]?secret",
    r"bearer",
    r"token",
    r"cookie",
    r"session",
    r"\.env",
    r"\.vtt",
    r"raw transcript",
    r"handoff_pack",
    r"business secret",
    r"confidential",
]

ALLOWLIST_FILES = [
    ".gitignore",
    "README.md",
    "RUNBOOK.md",
    "SAFETY.md",
    "STATUS.md",
    "00_STEM_CELL/README_STEM_CELL.md",
    "00_STEM_CELL/SAFETY_RULES.md",
    "00_STEM_CELL/REBUILD_PLAN.md",
    "00_STEM_CELL/SOURCE_MAP.md",
    "00_STEM_CELL/YTM_V1_1_BLUEPRINT.md",
    "00_STEM_CELL/YTM_V1_2_TARGET.md",
    "00_STEM_CELL/LOCAL_STACK.md",
    "scripts/safety/public_safety_audit.py",
]

def is_inside_blocked_path(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel.startswith(x) or ("/" + x) in rel for x in BLOCKED_PATHS)

def should_scan(path: Path) -> bool:
    if not path.is_file():
        return False
    if ".git" in path.parts:
        return False
    if path.name == ".DS_Store":
        return False
    return True

def main() -> int:
    findings = []

    for path in ROOT.rglob("*"):
        if not should_scan(path):
            continue

        rel = path.relative_to(ROOT).as_posix()

        if is_inside_blocked_path(path):
            findings.append(f"BLOCKED PATH PRESENT IN WORKTREE: {rel}")
            continue

        if path.stat().st_size > 1_000_000:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if rel in ALLOWLIST_FILES:
                    continue
                findings.append(f"SENSITIVE PATTERN: {rel} :: {pattern}")
                break

    if findings:
        print("PUBLIC SAFETY AUDIT: FAIL")
        print()
        for item in findings:
            print("-", item)
        print()
        print("Review before commit/push.")
        return 1

    print("PUBLIC SAFETY AUDIT: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
