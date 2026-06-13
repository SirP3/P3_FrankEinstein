#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def transcript_status(chars: int) -> tuple[str, str]:
    if chars == 0:
        return "empty", "skip"
    if chars < 200:
        return "too small", "skip"
    if chars > 20000:
        return "too large", "chunk later"
    return "eligible", "include"


def file_record(txt_file: Path, root: Path) -> dict[str, str | int]:
    text = txt_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    size = txt_file.stat().st_size
    chars = len(text)
    status, action = transcript_status(chars)

    return {
        "relative_path": txt_file.relative_to(root).as_posix(),
        "size": size,
        "line_count": len(lines),
        "character_count": chars,
        "status": status,
        "recommended_action": action,
    }


def write_manifest(run_id: str, transcript_index: Path, input_dir: Path, packet_dir: Path, target: Path, records: list[dict[str, str | int]]) -> None:
    total_bytes = sum(int(record["size"]) for record in records)
    total_chars = sum(int(record["character_count"]) for record in records)

    lines = []
    lines.append("# YTM Model Input Manifest")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input transcript index path: " + str(transcript_index))
    lines.append("Input cleaned transcript folder: " + str(input_dir))
    lines.append("Intended model packet folder: " + str(packet_dir))
    lines.append("Transcript TXT file count: " + str(len(records)))
    lines.append("Total bytes: " + str(total_bytes))
    lines.append("Total characters: " + str(total_chars))
    lines.append("Policy: Public Source, Private Processing, Clean Output")
    lines.append("")
    lines.append("Note: manifest is metadata only, not transcript content.")
    lines.append("Note: model packets and model outputs are runtime-only and must not be committed.")
    lines.append("Note: local model output is not source of truth.")
    lines.append("Note: no AI, model, or radar-card processing has been performed yet.")
    lines.append("")
    lines.append("## Model Input Guardrails")
    lines.append("")
    lines.append("- Do not reproduce transcript text.")
    lines.append("- Do not output long quotes.")
    lines.append("- Do not write rewritten third-party content.")
    lines.append("- Extract only structured observations, categories, risks, opportunities, and workflow patterns.")
    lines.append("- Mark uncertainty.")
    lines.append("- Preserve source attribution internally.")
    lines.append("- Clean output only.")
    lines.append("")
    lines.append("## Candidate Files")
    lines.append("")
    lines.append("| Relative path | Bytes | Lines | Characters | Status | Recommended action |")
    lines.append("| --- | ---: | ---: | ---: | --- | --- |")

    for record in records:
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
            + str(record["recommended_action"])
            + " |"
        )

    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a metadata-only YTM model input manifest.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    transcript_index = run_dir / "derived" / "transcript_index.md"
    input_dir = run_dir / "derived" / "transcripts_txt"
    packet_dir = run_dir / "derived" / "model_packets"
    target = run_dir / "derived" / "model_input_manifest.md"

    if not transcript_index.exists():
        raise SystemExit("Transcript index not found: " + str(transcript_index) + "\nRun build_transcript_index.py first.")

    if not input_dir.exists():
        raise SystemExit("Cleaned TXT transcripts folder not found: " + str(input_dir))

    txt_files = sorted([p for p in input_dir.glob("*.txt") if p.is_file()])
    if not txt_files:
        raise SystemExit("No TXT transcript files found in cleaned transcripts folder: " + str(input_dir))

    records = [file_record(txt_file, run_dir) for txt_file in txt_files]
    write_manifest(args.run_id, transcript_index, input_dir, packet_dir, target, records)

    print("MODEL INPUT MANIFEST", target)
    print("Transcript TXT file count:", len(records))
    print("Safety: metadata-only manifest. Transcript content is not included.")
    print("Intended model packet folder:", packet_dir)


if __name__ == "__main__":
    main()
