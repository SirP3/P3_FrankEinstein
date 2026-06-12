from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
ALLOWED_SOURCE_EXTENSIONS = {".md", ".txt", ".vtt", ".srt", ".json"}

def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only derived placeholder from YTM source files.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    source_dir = run_dir / "source"
    derived_dir = run_dir / "derived"

    if not source_dir.exists():
        raise SystemExit("Source folder not found: " + str(source_dir))

    files = sorted([
        p for p in source_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_SOURCE_EXTENSIONS
    ])

    derived_dir.mkdir(parents=True, exist_ok=True)
    target = derived_dir / "source_inventory.md"

    lines = []
    lines.append("# Source Inventory")
    lines.append("")
    lines.append("Run ID: " + args.run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Source file count: " + str(len(files)))
    lines.append("")
    lines.append("## Files")
    lines.append("")
    if files:
        for file in files:
            lines.append("- " + str(file.relative_to(run_dir)))
    else:
        lines.append("- No source files found.")
    lines.append("")
    lines.append("Status: placeholder only. No transcript processing yet.")

    target.write_text("\n".join(lines), encoding="utf-8")
    print("DERIVED", target)
    print("Source file count:", len(files))

if __name__ == "__main__":
    main()
