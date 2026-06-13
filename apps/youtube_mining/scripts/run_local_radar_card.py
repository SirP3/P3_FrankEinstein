#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
PROMPT_TEMPLATE = ROOT / "apps" / "youtube_mining" / "prompts" / "ytm_radar_card_prompt_v0_2.md"


def safe_output_name(packet: Path) -> str:
    value = packet.name.replace(".model-packet.md", "")
    value = value.lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value or "radar-card") + ".radar-card.md"


def require_ollama() -> str:
    ollama = shutil.which("ollama")
    if not ollama:
        raise SystemExit("ollama not found. Install Ollama or run with --dry-run for smoke testing.")
    return ollama


def build_model_input(prompt_template: Path, packet: Path) -> str:
    return (
        prompt_template.read_text(encoding="utf-8", errors="ignore")
        + "\n\n---\n\n# Local Model Packet\n\n"
        + packet.read_text(encoding="utf-8", errors="ignore")
    )


def write_run_log(
    run_id: str,
    prompt_template: Path,
    packet_dir: Path,
    output_dir: Path,
    model: str,
    dry_run: bool,
    candidate_count: int,
    processed_count: int,
    skipped_count: int,
    planned_packets: list[Path],
) -> Path:
    log_path = output_dir / "radar-card-run-log.md"
    lines = []
    lines.append("# YTM Radar Card Run Log")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Prompt template path: " + str(prompt_template))
    lines.append("Input model packet folder: " + str(packet_dir))
    lines.append("Output radar card folder: " + str(output_dir))
    lines.append("Model name: " + model)
    lines.append("Dry-run: " + ("yes" if dry_run else "no"))
    lines.append("Packet candidate count: " + str(candidate_count))
    lines.append("Processed count: " + str(processed_count))
    lines.append("Skipped count: " + str(skipped_count))
    lines.append("")
    lines.append("Note: radar-card outputs are runtime-only and must not be committed.")
    lines.append("Note: local model output is not source of truth.")
    lines.append("Note: clean output policy applies.")

    if planned_packets:
        lines.append("")
        lines.append("## Packets")
        lines.append("")
        for packet in planned_packets:
            lines.append("- " + packet.name)

    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def run_model(model: str, model_input: str) -> str:
    ollama = require_ollama()
    result = subprocess.run(
        [ollama, "run", model],
        input=model_input,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("ollama run failed:\n" + result.stdout.strip())
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local-only YTM radar-card generation from model packets.")
    parser.add_argument("run_id")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    run_dir = OUTPUT_ROOT / args.run_id
    packet_dir = run_dir / "derived" / "model_packets"
    output_dir = run_dir / "derived" / "radar_cards"

    if not PROMPT_TEMPLATE.exists():
        raise SystemExit("Prompt template not found: " + str(PROMPT_TEMPLATE))

    if not packet_dir.exists():
        raise SystemExit("Model packet folder not found: " + str(packet_dir))

    packets = sorted([p for p in packet_dir.glob("*.model-packet.md") if p.is_file()])
    if not packets:
        raise SystemExit("No model packet files found in: " + str(packet_dir))

    selected = packets[:args.limit]
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        log_path = write_run_log(
            args.run_id,
            PROMPT_TEMPLATE,
            packet_dir,
            output_dir,
            args.model,
            True,
            len(packets),
            0,
            len(packets) - len(selected),
            selected,
        )
        print("DRY RUN")
        print("Prompt template:", PROMPT_TEMPLATE)
        print("Input model packet folder:", packet_dir)
        print("Output radar card folder:", output_dir)
        print("Packet candidate count:", len(packets))
        print("Would process:", len(selected))
        for packet in selected:
            print("Packet:", packet.name)
        print("Wrote:", log_path)
        return

    written = []
    for packet in selected:
        model_input = build_model_input(PROMPT_TEMPLATE, packet)
        output = run_model(args.model, model_input)
        target = output_dir / safe_output_name(packet)
        target.write_text(output, encoding="utf-8")
        written.append(target)

    log_path = write_run_log(
        args.run_id,
        PROMPT_TEMPLATE,
        packet_dir,
        output_dir,
        args.model,
        False,
        len(packets),
        len(written),
        len(packets) - len(selected),
        selected,
    )

    print("RADAR CARDS", output_dir)
    print("Packet candidate count:", len(packets))
    print("Processed count:", len(written))
    print("Skipped count:", len(packets) - len(selected))
    print("Wrote:", log_path)
    print("Safety: radar-card outputs are local-only runtime data. Do not commit.")


if __name__ == "__main__":
    main()
