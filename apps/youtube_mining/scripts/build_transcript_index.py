#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

METADATA_PREFIXES = (
    "title:",
    "video:",
    "video id:",
    "video_id:",
    "source:",
    "url:",
    "language:",
    "lang:",
    "date:",
    "upload date:",
)


def safe_preview(lines: list[str]) -> str:
    for line in lines:
        value = line.strip()
        if not value:
            continue
        lowered = value.lower()
        if any(lowered.startswith(prefix) for prefix in METADATA_PREFIXES):
            return value
        return ""
    return ""


def transcript_status(size: int, chars: int) -> str:
    if size == 0 or chars == 0:
        return "empty"
    if chars < 80:
        return "too small"
    return "available"


def file_record(txt_file: Path, root: Path) -> dict[str, str | int]:
    text = txt_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    size = txt_file.stat().st_size
    chars = len(text)

    return {
        "relative_path": txt_file.relative_to(root).as_posix(),
        "size": size,
        "line_count": len(lines),
        "character_count": chars,
        "preview": safe_preview(lines),
        "status": transcript_status(size, chars),
    }


def write_index(run_id: str, input_dir: Path, target: Path, records: list[dict[str, str | int]]) -> None:
    total_bytes = sum(int(record["size"]) for record in records)
    total_chars = sum(int(record["character_count"]) for record in records)

    lines = []
    lines.append("# YTM Transcript Index")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input folder: " + str(input_dir))
    lines.append("Transcript TXT file count: " + str(len(records)))
    lines.append("Total bytes: " + str(total_bytes))
    lines.append("Total characters: " + str(total_chars))
    lines.append("")
    lines.append("Note: cleaned TXT transcripts are local-only derived runtime data and must not be committed.")
    lines.append("Note: this index contains metadata only, not transcript content.")
    lines.append("Note: no AI, model, or radar-card processing has been performed yet.")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("| Relative path | Bytes | Lines | Characters | Status | Safe metadata preview |")
    lines.append("| --- | ---: | ---: | ---: | --- | --- |")

    for record in records:
        preview = str(record["preview"])
        lines.append(
            "| "
            + str(record["relative_path"])
            + " | "
            + str(record["size"])
            + " | "
            + str(record["line_count"])
            + " | "
            + str(record["character_count"])
            + " | "
            + str(record["status"])
            + " | "
            + preview.replace("|", "/")
            + " |"
        )

    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a metadata-only index for local-only YTM cleaned TXT transcripts.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    input_dir = run_dir / "derived" / "transcripts_txt"
    target = run_dir / "derived" / "transcript_index.md"

    if not input_dir.exists():
        raise SystemExit("Cleaned TXT transcripts folder not found: " + str(input_dir))

    txt_files = sorted([p for p in input_dir.glob("*.txt") if p.is_file()])
    if not txt_files:
        raise SystemExit("No TXT transcript files found in cleaned transcripts folder: " + str(input_dir))

    records = [file_record(txt_file, run_dir) for txt_file in txt_files]
    write_index(args.run_id, input_dir, target, records)

    print("TRANSCRIPT INDEX", target)
    print("Transcript TXT file count:", len(records))
    print("Safety: metadata-only index. Transcript content is not included.")


if __name__ == "__main__":
    main()
