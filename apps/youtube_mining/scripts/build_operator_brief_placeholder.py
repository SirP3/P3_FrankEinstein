from pathlib import Path
import argparse
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def extract_source_file_count(text: str) -> str:
    match = re.search(r"^Source file count:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return "unknown"
    return match.group(1).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only operator brief placeholder from YTM derived inventory.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    inventory = run_dir / "derived" / "source_inventory.md"
    handoffs_dir = run_dir / "handoffs"

    if not inventory.exists():
        raise SystemExit("Derived source inventory not found: " + str(inventory))

    inventory_text = inventory.read_text(encoding="utf-8", errors="ignore")
    source_file_count = extract_source_file_count(inventory_text)

    handoffs_dir.mkdir(parents=True, exist_ok=True)
    target = handoffs_dir / "operator_brief.md"

    lines = []
    lines.append("# Operator Brief")
    lines.append("")
    lines.append("Run ID: " + args.run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("")
    lines.append("## Source Inventory Status")
    lines.append("")
    lines.append("Source inventory: available")
    lines.append("Source file count: " + source_file_count)
    lines.append("")
    lines.append("## Current Limitation")
    lines.append("")
    lines.append("Placeholder only. No AI, model call, transcript mining, or source interpretation has been performed yet.")
    lines.append("")
    lines.append("## Next Suggested Operator Action")
    lines.append("")
    lines.append("Review the source inventory and confirm the run is ready for the first local analysis step.")

    target.write_text("\n".join(lines), encoding="utf-8")
    print("HANDOFF", target)
    print("Source inventory:", inventory)
    print("Source file count:", source_file_count)


if __name__ == "__main__":
    main()
