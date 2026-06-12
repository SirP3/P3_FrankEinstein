from pathlib import Path
import argparse
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
ALLOWED_EXTENSIONS = {".md", ".txt", ".vtt", ".srt", ".json"}

def safe_run_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "run"

def main() -> None:
    parser = argparse.ArgumentParser(description="Add one local-only source file to a YTM run.")
    parser.add_argument("run_id")
    parser.add_argument("source_file")
    args = parser.parse_args()

    run_id = safe_run_id(args.run_id)
    source = Path(args.source_file).expanduser().resolve()

    if not source.exists() or not source.is_file():
        raise SystemExit("Source file not found: " + str(source))

    if source.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise SystemExit("Unsupported source extension: " + source.suffix)

    target_dir = OUTPUT_ROOT / run_id / "source"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name

    shutil.copy2(source, target)
    print("COPIED", target)
    print("Safety: local-only output. Do not commit.")

if __name__ == "__main__":
    main()
