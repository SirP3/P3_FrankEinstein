from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

SOURCE_EXTENSIONS = {".txt", ".md", ".vtt", ".srt", ".json"}

def source_files(run_id: str) -> list[Path]:
    source_dir = OUTPUT_ROOT / run_id / "source"
    if not source_dir.exists():
        return []
    return sorted([
        p for p in source_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SOURCE_EXTENSIONS
    ])

def main() -> None:
    parser = argparse.ArgumentParser(description="Show local-only YTM source status for a run.")
    parser.add_argument("run_id", help="Run id under output/youtube_mining/")
    args = parser.parse_args()

    files = source_files(args.run_id)

    print("YTM Source Status")
    print("=================")
    print()
    print("Run ID:", args.run_id)
    print("Source file count:", len(files))
    print()

    if not files:
        print("No source files found.")
        return

    for file in files:
        rel = file.relative_to(OUTPUT_ROOT / args.run_id)
        print("-", rel)

if __name__ == "__main__":
    main()
