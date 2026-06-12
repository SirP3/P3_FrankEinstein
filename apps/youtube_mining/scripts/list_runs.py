#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

EXPECTED_DIRS = ["source", "derived", "handoffs", "archive"]

def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())

def describe_run(run_path: Path) -> str:
    run_id = run_path.name
    parts = []

    for folder in EXPECTED_DIRS:
        folder_path = run_path / folder
        exists = "yes" if folder_path.exists() else "no"
        files = count_files(folder_path)
        parts.append(f"{folder}: {exists}, files={files}")

    run_info = "yes" if (run_path / "run-info.md").exists() else "no"

    return f"- {run_id} | run-info={run_info} | " + " | ".join(parts)

def main() -> None:
    print("YTM Local Runs")
    print("==============")
    print()

    if not OUTPUT_ROOT.exists():
        print("No output root yet.")
        print(f"Expected: {OUTPUT_ROOT}")
        return

    runs = sorted([p for p in OUTPUT_ROOT.iterdir() if p.is_dir()], key=lambda x: x.name.lower())

    if not runs:
        print("No local runs found.")
        return

    print(f"Output root: {OUTPUT_ROOT}")
    print(f"Run count: {len(runs)}")
    print()

    for run in runs:
        print(describe_run(run))

if __name__ == "__main__":
    main()
