#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

INPUT_PATHS = [
    "handoffs/operator_brief.md",
    "handoffs/radar_card_brief.md",
    "handoffs/ytm_pipeline_smoke_report.md",
    "derived/radar_cards/radar-card-validation-report.md",
    "derived/transcript_index.md",
    "derived/model_input_manifest.md",
]


def read_key_values(path: Path, keys: list[str]) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for key in keys:
            prefix = key + ":"
            if line.startswith(prefix):
                values[key] = line[len(prefix):].strip()
    return values


def model_manifest_counts(path: Path) -> dict[str, int]:
    counts = {"eligible": 0, "skipped": 0}
    if not path.exists():
        return counts

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("| ") or line.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 6 or cells[0] == "Relative path":
            continue
        status = cells[4]
        action = cells[5]
        if status == "eligible" and action == "include":
            counts["eligible"] += 1
        else:
            counts["skipped"] += 1
    return counts


def status_for(path: Path) -> str:
    return "available" if path.exists() else "missing"


def final_status(run_dir: Path) -> str:
    validation = read_key_values(
        run_dir / "derived" / "radar_cards" / "radar-card-validation-report.md",
        ["Radar-card count", "Passed count", "Warning count", "Failed count"],
    )
    smoke = read_key_values(run_dir / "handoffs" / "ytm_pipeline_smoke_report.md", ["Final status"])

    if validation:
        failed = int(validation.get("Failed count", "0") or "0")
        warnings = int(validation.get("Warning count", "0") or "0")
        passed = int(validation.get("Passed count", "0") or "0")
        if failed > 0:
            return "warning"
        if warnings > 0:
            return "warning"
        if passed > 0:
            return "pass"

    if smoke.get("Final status") == "pass":
        return "pass"

    return "incomplete"


def write_summary(run_id: str, run_dir: Path, handoffs_dir: Path) -> Path:
    transcript_index = run_dir / "derived" / "transcript_index.md"
    model_manifest = run_dir / "derived" / "model_input_manifest.md"
    validation_report = run_dir / "derived" / "radar_cards" / "radar-card-validation-report.md"

    transcript_values = read_key_values(transcript_index, ["Transcript TXT file count", "Total characters"])
    model_values = read_key_values(model_manifest, ["Transcript TXT file count", "Total characters"])
    model_counts = model_manifest_counts(model_manifest)
    validation_values = read_key_values(
        validation_report,
        ["Radar-card count", "Passed count", "Warning count", "Failed count"],
    )

    target = handoffs_dir / "ytm_run_summary.md"
    lines = []
    lines.append("# YTM Run Summary")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Final status: " + final_status(run_dir))
    lines.append("")
    lines.append("## Available Runtime Outputs")
    lines.append("")
    lines.append("| Path | Status |")
    lines.append("| --- | --- |")
    for relative_path in INPUT_PATHS:
        lines.append("| " + relative_path + " | " + status_for(run_dir / relative_path) + " |")
    lines.append("")
    lines.append("## Transcript Metadata Summary")
    lines.append("")
    lines.append("- Transcript TXT file count: " + transcript_values.get("Transcript TXT file count", "not available"))
    lines.append("- Total characters: " + transcript_values.get("Total characters", "not available"))
    lines.append("")
    lines.append("## Model Input Summary")
    lines.append("")
    lines.append("- Transcript TXT file count: " + model_values.get("Transcript TXT file count", "not available"))
    lines.append("- Total characters: " + model_values.get("Total characters", "not available"))
    lines.append("- Eligible files: " + str(model_counts["eligible"]) if model_manifest.exists() else "- Eligible files: not available")
    lines.append("- Skipped files: " + str(model_counts["skipped"]) if model_manifest.exists() else "- Skipped files: not available")
    lines.append("")
    lines.append("## Radar-card Validation Summary")
    lines.append("")
    lines.append("- Radar-card count: " + validation_values.get("Radar-card count", "not available"))
    lines.append("- Passed count: " + validation_values.get("Passed count", "not available"))
    lines.append("- Warning count: " + validation_values.get("Warning count", "not available"))
    lines.append("- Failed count: " + validation_values.get("Failed count", "not available"))
    lines.append("")
    lines.append("## Handoff Outputs")
    lines.append("")
    lines.append("- operator_brief.md: " + status_for(run_dir / "handoffs" / "operator_brief.md"))
    lines.append("- radar_card_brief.md: " + status_for(run_dir / "handoffs" / "radar_card_brief.md"))
    lines.append("- ytm_pipeline_smoke_report.md: " + status_for(run_dir / "handoffs" / "ytm_pipeline_smoke_report.md"))
    lines.append("")
    lines.append("## Policy Notes")
    lines.append("")
    lines.append("- Public Source, Private Processing, Clean Output.")
    lines.append("- Runtime-only summary, do not commit.")
    lines.append("- Local model output is not source of truth.")
    lines.append("- This summary is an operator checkpoint, not legal/compliance proof.")

    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only YTM operator run summary.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    if not run_dir.exists():
        raise SystemExit("Run folder not found: " + str(run_dir))

    handoffs_dir = run_dir / "handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)
    summary = write_summary(args.run_id, run_dir, handoffs_dir)

    print("YTM RUN SUMMARY", summary)
    print("Final status:", final_status(run_dir))
    print("Safety: run summary is local-only runtime data. Do not commit.")


if __name__ == "__main__":
    main()
