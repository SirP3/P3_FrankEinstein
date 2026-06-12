#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import argparse
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

def safe_run_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "run"

def create_run_folder(run_id: str) -> Path:
    run_id = safe_run_id(run_id)
    run_path = OUTPUT_ROOT / run_id

    for sub in ["source", "derived", "handoffs", "archive"]:
        (run_path / sub).mkdir(parents=True, exist_ok=True)

    info = run_path / "run-info.md"
    if not info.exists():
        info.write_text(
            "# YTM Run Info\\n\\n"
            + "Run ID: `" + run_id + "`\\n\\n"
            + "Created: " + datetime.now().isoformat(timespec=\"seconds\") + "\\n\\n"
            + "Safety: local-only runtime output. Do not commit.\\n",
            encoding="utf-8",
        )

    return run_path

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local-only YTM run folder.")
    parser.add_argument("run_id", help="Human-readable run id, e.g. test-run-001")
    args = parser.parse_args()

    run_path = create_run_folder(args.run_id)
    print("CREATED", run_path)

if __name__ == "__main__":
    main()
