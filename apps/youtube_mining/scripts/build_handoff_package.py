#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


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


def status_for(path: Path) -> str:
    return "available" if path.exists() else "missing"


def relative_or_missing(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.exists() else "not available"


def final_recommendation(missing: list[str], validation_failed: int, validation_warnings: int) -> str:
    if validation_failed > 0:
        return "Review validation failures before any handoff use."
    if missing:
        return "Build the missing runtime artifacts before treating this run as handoff-ready."
    if validation_warnings > 0:
        return "Proceed with handoff preparation, but review warnings first."
    return "Proceed to operator review using the handoff package and linked runtime artifacts."


def build_package(run_id: str, run_dir: Path, handoffs_dir: Path) -> tuple[Path, Path]:
    source_log = run_dir / "source" / "source-intake-log.md"
    transcript_log = run_dir / "source" / "transcript-intake-log.md"
    conversion_log = run_dir / "derived" / "transcript-conversion-log.md"
    model_packet_log = run_dir / "derived" / "model_packets" / "model-packet-log.md"
    validation_report = run_dir / "derived" / "radar_cards" / "radar-card-validation-report.md"
    combined_radar = run_dir / "derived" / "radar_cards" / "all-video-radar-cards-combined.md"
    keyword_index = run_dir / "derived" / "radar_cards" / "radar_keyword_index_001.md"
    quality_pass = run_dir / "derived" / "radar_cards" / "qwinni_quality_pass_001.md"
    radar_brief = handoffs_dir / "radar_card_brief.md"
    operator_brief = handoffs_dir / "operator_brief.md"
    smoke_report = handoffs_dir / "ytm_pipeline_smoke_report.md"

    source_values = read_key_values(source_log, ["Input mode", "Input value", "Selected videos"])
    transcript_values = read_key_values(
        transcript_log,
        ["Selected video count", "Processed video count", "Skipped existing count", "Processing limit", "Language setting"],
    )
    conversion_values = read_key_values(
        conversion_log,
        ["Processed file count", "Skipped existing count", "Processing limit"],
    )
    model_packet_values = read_key_values(
        model_packet_log,
        ["Candidate TXT file count", "Packet file count", "Skipped file count"],
    )
    validation_values = read_key_values(
        validation_report,
        ["Radar-card count", "Passed count", "Warning count", "Failed count"],
    )

    failed = int(validation_values.get("Failed count", "0") or "0")
    warnings = int(validation_values.get("Warning count", "0") or "0")

    missing = []
    for label, path in [
        ("combined radar artifact", combined_radar),
        ("radar keyword index artifact", keyword_index),
        ("quality-pass artifact", quality_pass),
        ("radar-card brief", radar_brief),
        ("validation report", validation_report),
    ]:
        if not path.exists():
            missing.append(label)

    lines = []
    lines.append("# YTM Handoff Package")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("")
    lines.append("## Source Metadata")
    lines.append("")
    lines.append("- Source mode: " + source_values.get("Input mode", "not available"))
    lines.append("- Source input: " + source_values.get("Input value", "not available"))
    lines.append("- Subtitle language: " + transcript_values.get("Language setting", "not available"))
    lines.append("")
    lines.append("## Processing Counts")
    lines.append("")
    lines.append("- Selected videos: " + transcript_values.get("Selected video count", source_values.get("Selected videos", "not available")))
    lines.append("- Transcript processed: " + transcript_values.get("Processed video count", "not available"))
    lines.append("- Transcript skipped existing: " + transcript_values.get("Skipped existing count", "not available"))
    lines.append("- Conversion processed: " + conversion_values.get("Processed file count", "not available"))
    lines.append("- Conversion skipped existing: " + conversion_values.get("Skipped existing count", "not available"))
    lines.append("- Model packet count: " + model_packet_values.get("Packet file count", "not available"))
    lines.append("")
    lines.append("## Radar Package Status")
    lines.append("")
    lines.append("- Radar-card count: " + validation_values.get("Radar-card count", "not available"))
    lines.append("- Validation passed count: " + validation_values.get("Passed count", "not available"))
    lines.append("- Validation warning count: " + validation_values.get("Warning count", "not available"))
    lines.append("- Validation failed count: " + validation_values.get("Failed count", "not available"))
    lines.append("- Combined radar: " + status_for(combined_radar) + " (`" + relative_or_missing(combined_radar, run_dir) + "`)")
    lines.append("- Radar keyword index: " + status_for(keyword_index) + " (`" + relative_or_missing(keyword_index, run_dir) + "`)")
    lines.append("- Quality pass: " + status_for(quality_pass) + " (`" + relative_or_missing(quality_pass, run_dir) + "`)")
    lines.append("")
    lines.append("## Handoff Surfaces")
    lines.append("")
    lines.append("- Radar-card brief: " + status_for(radar_brief) + " (`" + relative_or_missing(radar_brief, run_dir) + "`)")
    lines.append("- Operator brief: " + status_for(operator_brief) + " (`" + relative_or_missing(operator_brief, run_dir) + "`)")
    lines.append("- Pipeline smoke report: " + status_for(smoke_report) + " (`" + relative_or_missing(smoke_report, run_dir) + "`)")
    lines.append("")
    lines.append("## Final Operator Summary")
    lines.append("")
    if failed > 0:
        lines.append("- Status: warning")
        lines.append("- Summary: Validation failures are present. Treat this run as incomplete for handoff use.")
    elif warnings > 0:
        lines.append("- Status: review")
        lines.append("- Summary: Core artifacts exist, but validation warnings should be reviewed before handoff use.")
    elif missing:
        lines.append("- Status: incomplete")
        lines.append("- Summary: Some expected handoff-supporting artifacts are still missing.")
    else:
        lines.append("- Status: usable")
        lines.append("- Summary: Core handoff-supporting artifacts exist and no obvious package-level blockers were detected.")
    lines.append("")
    lines.append("## Warnings / Missing Artifacts")
    lines.append("")
    if missing:
        for item in missing:
            lines.append("- Missing artifact: " + item)
    if warnings > 0:
        lines.append("- Validation warnings exist and should be reviewed.")
    if failed > 0:
        lines.append("- Validation failures exist and block a clean handoff package.")
    if not missing and warnings == 0 and failed == 0:
        lines.append("- No obvious missing artifacts detected in the current rolling handoff package.")
    lines.append("")
    lines.append("## Next Recommended Action")
    lines.append("")
    lines.append("- " + final_recommendation(missing, failed, warnings))
    lines.append("")
    lines.append("## Policy Notes")
    lines.append("")
    lines.append("- Public Source, Private Processing, Clean Output.")
    lines.append("- Runtime artifacts remain local-only and must not be committed.")
    lines.append("- This handoff package summarizes local runtime outputs and does not expose transcript bodies, cleaned TXT bodies, or model packet bodies.")
    lines.append("- Local model output is not source of truth.")

    handoff_pack = handoffs_dir / "handoff_pack.md"
    alias_pack = handoffs_dir / (run_id + "__handoff_pack.md")
    content = "\n".join(lines).rstrip() + "\n"
    handoff_pack.write_text(content, encoding="utf-8")
    alias_pack.write_text(content, encoding="utf-8")
    return handoff_pack, alias_pack


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only YTM handoff package.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    if not run_dir.exists():
        raise SystemExit("Run folder not found: " + str(run_dir))

    handoffs_dir = run_dir / "handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)
    handoff_pack, alias_pack = build_package(args.run_id, run_dir, handoffs_dir)

    print("HANDOFF PACK", handoff_pack)
    print("Run-bound alias:", alias_pack)
    print("Safety: handoff package is local-only runtime output. Do not commit.")


if __name__ == "__main__":
    main()
