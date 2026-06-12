#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

IGNORED_DIRS = {
    ".git",
    "private",
    "output",
    "quarantine",
    "donor",
    ".local-private",
    "__pycache__",
    ".venv",
}

SENSITIVE_PATTERNS = [
    r"api[_-]?key",
    r"private[_-]?key",
    r"client[_-]?secret",
    r"bearer",
    r"access[_-]?token",
    r"refresh[_-]?token",
    r"cookie",
    r"\.env",
]

WARNING_PATTERNS = [
    r"raw transcript",
    r"\.vtt",
    r"handoff_pack",
    r"business secret",
    r"confidential",
    r"personal identifier",
    r"company-specific identifier",
]

ALLOWLIST_WARNING_FILES = {
    "README.md",
    "SAFETY.md",
    "STATUS.md",
    "RUNBOOK.md",
    "00_STEM_CELL/README_STEM_CELL.md",
    "00_STEM_CELL/SAFETY_RULES.md",
    "00_STEM_CELL/REBUILD_PLAN.md",
    "00_STEM_CELL/SOURCE_MAP.md",
    "00_STEM_CELL/YTM_V1_1_BLUEPRINT.md",
    "00_STEM_CELL/YTM_V1_2_TARGET.md",
    "00_STEM_CELL/LOCAL_STACK.md",
    "00_STEM_CELL/source_maps/V0_1_DONOR_MAP.md",
    "00_STEM_CELL/rebuild/YTM_CODE_INSPECTION_DECISION.md",
    "apps/youtube_mining/README.md",
    "apps/youtube_mining/docs/OUTPUT_POLICY.md",
    "scripts/safety/public_safety_audit.py",
    ".gitignore",
}

def is_ignored(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    return any(part in IGNORED_DIRS for part in rel_parts)

def should_scan(path: Path) -> bool:
    if not path.is_file():
        return False
    if is_ignored(path):
        return False
    if path.name == ".DS_Store":
        return False
    if path.stat().st_size > 1_000_000:
        return False
    return True

def scan_patterns(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return pattern
    return None

def main() -> int:
    findings = []
    warnings = []

    for path in ROOT.rglob("*"):
        if not should_scan(path):
            continue

        rel = path.relative_to(ROOT).as_posix()

        if rel in ALLOWLIST_WARNING_FILES:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        sensitive = scan_patterns(text, SENSITIVE_PATTERNS)
        if sensitive:
            findings.append(f"SENSITIVE PATTERN: {rel} :: {sensitive}")
            continue

        warning = scan_patterns(text, WARNING_PATTERNS)
        if warning and rel not in ALLOWLIST_WARNING_FILES:
            warnings.append(f"WARNING PATTERN: {rel} :: {warning}")

    if findings:
        print("PUBLIC SAFETY AUDIT: FAIL")
        print()
        for item in findings:
            print("-", item)
        print()
        print("Review before commit/push.")
        return 1

    if warnings:
        print("PUBLIC SAFETY AUDIT: PASS WITH WARNINGS")
        print()
        for item in warnings:
            print("-", item)
        print()
        print("Warnings are not blockers, but review them before push.")
        return 0

    print("PUBLIC SAFETY AUDIT: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
