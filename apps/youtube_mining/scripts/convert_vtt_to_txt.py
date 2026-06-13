#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def clean_vtt_text(vtt_text: str) -> str:
    lines = []

    for raw in vtt_text.splitlines():
        line = raw.strip()

        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if line.startswith("NOTE"):
            continue

        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)
        line = re.sub(r"</?(?:c|i|b|u)(?:\.[^>]*)?>", "", line)
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()

        if line and (not lines or line != lines[-1]):
            lines.append(line)

    return "\n".join(lines)


def convert_files(vtt_files: list[Path], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    converted = []

    for vtt in vtt_files:
        cleaned = clean_vtt_text(vtt.read_text(encoding="utf-8", errors="ignore"))
        target = output_dir / (vtt.stem + ".txt")
        target.write_text(cleaned + "\n", encoding="utf-8")
        converted.append(target)

    return converted


def write_log(run_id: str, input_dir: Path, output_dir: Path, vtt_count: int, processed_count: int) -> Path:
    log_path = output_dir.parent / "transcript-conversion-log.md"
    lines = []
    lines.append("# YTM Transcript Conversion Log")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input folder: " + str(input_dir))
    lines.append("Output folder: " + str(output_dir))
    lines.append("VTT file count: " + str(vtt_count))
    lines.append("Processed file count: " + str(processed_count))
    lines.append("")
    lines.append("Note: cleaned TXT transcripts are derived runtime data and must not be committed.")
    lines.append("Note: no AI, model, or radar-card processing has been performed yet.")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert local-only YTM VTT transcripts to cleaned TXT files.")
    parser.add_argument("run_id")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    run_dir = OUTPUT_ROOT / args.run_id
    input_dir = run_dir / "source" / "transcripts"
    output_dir = run_dir / "derived" / "transcripts_txt"

    if not input_dir.exists():
        raise SystemExit("Source transcripts folder not found: " + str(input_dir))

    vtt_files = sorted([p for p in input_dir.glob("*.vtt") if p.is_file()])
    if not vtt_files:
        raise SystemExit("No VTT files found in source transcripts folder: " + str(input_dir))

    selected = vtt_files[:args.limit] if args.limit is not None else vtt_files
    converted = convert_files(selected, output_dir)
    log_path = write_log(args.run_id, input_dir, output_dir, len(vtt_files), len(converted))

    print("TRANSCRIPT CONVERSION", output_dir)
    print("VTT file count:", len(vtt_files))
    print("Processed file count:", len(converted))
    print("Wrote:", log_path)
    print("Safety: cleaned TXT transcripts are local-only derived runtime data. Do not commit.")


if __name__ == "__main__":
    main()
