#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
MAX_PACKET_CHARS = 20000


def safe_packet_name(txt_file: Path) -> str:
    value = txt_file.stem.lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value or "transcript") + ".model-packet.md"


def write_packet(run_id: str, txt_file: Path, run_dir: Path, packet_dir: Path, text: str) -> Path:
    target = packet_dir / safe_packet_name(txt_file)
    relative_source = txt_file.relative_to(run_dir).as_posix()

    lines = []
    lines.append("# YTM Local Model Packet")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Source TXT relative path: " + relative_source)
    lines.append("Policy: Public Source, Private Processing, Clean Output")
    lines.append("")
    lines.append("## Model Guardrails")
    lines.append("")
    lines.append("- Do not reproduce transcript text.")
    lines.append("- Do not output long quotes.")
    lines.append("- Do not write rewritten third-party content.")
    lines.append("- Extract only structured observations, categories, risks, opportunities, and workflow patterns.")
    lines.append("- Mark uncertainty.")
    lines.append("- Clean output only.")
    lines.append("- Local model output is not source of truth.")
    lines.append("")
    lines.append("## Transcript Content")
    lines.append("")
    lines.append(text)

    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def write_log(run_id: str, input_dir: Path, packet_dir: Path, candidate_count: int, packet_count: int, skipped: list[str]) -> Path:
    log_path = packet_dir / "model-packet-log.md"
    lines = []
    lines.append("# YTM Model Packet Log")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input folder: " + str(input_dir))
    lines.append("Output folder: " + str(packet_dir))
    lines.append("Candidate TXT file count: " + str(candidate_count))
    lines.append("Packet file count: " + str(packet_count))
    lines.append("Skipped file count: " + str(len(skipped)))
    lines.append("")
    lines.append("Note: model packets are runtime-only and must not be committed.")
    lines.append("Note: no AI, model, or radar-card processing has been performed yet.")

    if skipped:
        lines.append("")
        lines.append("## Skipped Files")
        lines.append("")
        for item in skipped:
            lines.append("- " + item)

    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local-only YTM model packets from cleaned TXT transcripts.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    manifest = run_dir / "derived" / "model_input_manifest.md"
    input_dir = run_dir / "derived" / "transcripts_txt"
    packet_dir = run_dir / "derived" / "model_packets"

    if not manifest.exists():
        raise SystemExit("Model input manifest not found: " + str(manifest) + "\nRun build_model_input_manifest.py first.")

    if not input_dir.exists():
        raise SystemExit("Cleaned TXT transcripts folder not found: " + str(input_dir))

    txt_files = sorted([p for p in input_dir.glob("*.txt") if p.is_file()])
    if not txt_files:
        raise SystemExit("No TXT transcript files found in cleaned transcripts folder: " + str(input_dir))

    packet_dir.mkdir(parents=True, exist_ok=True)
    written = []
    skipped = []

    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8", errors="ignore")
        chars = len(text)
        if chars == 0:
            skipped.append(txt_file.relative_to(run_dir).as_posix() + " :: empty")
            continue
        if chars < 200:
            skipped.append(txt_file.relative_to(run_dir).as_posix() + " :: too small")
            continue
        if chars > MAX_PACKET_CHARS:
            skipped.append(txt_file.relative_to(run_dir).as_posix() + " :: chunk later")
            continue
        written.append(write_packet(args.run_id, txt_file, run_dir, packet_dir, text))

    log_path = write_log(args.run_id, input_dir, packet_dir, len(txt_files), len(written), skipped)

    print("MODEL PACKETS", packet_dir)
    print("Candidate TXT file count:", len(txt_files))
    print("Packet file count:", len(written))
    print("Skipped file count:", len(skipped))
    print("Wrote:", log_path)
    print("Safety: model packets are local-only runtime data. Do not commit.")


if __name__ == "__main__":
    main()
