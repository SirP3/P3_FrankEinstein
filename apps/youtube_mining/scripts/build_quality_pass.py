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


def package_status(path: Path) -> str:
    return "available" if path.exists() else "missing"


def final_assessment(radar_count: int, failed: int, warnings: int, required_present: bool) -> tuple[str, str]:
    if radar_count == 0 or failed > 0 or not required_present:
        return "warning", "The package needs follow-up before handoff preparation."
    if warnings > 0:
        return "review", "The package is usable, but warnings should be checked before handoff preparation."
    return "usable", "The package looks usable for handoff preparation."


def write_quality_pass(
    run_id: str,
    target: Path,
    radar_count: int,
    passed: int,
    warnings: int,
    failed: int,
    combined_radar: Path,
    keyword_index: Path,
    validation_report: Path,
) -> None:
    required_present = combined_radar.exists() and keyword_index.exists() and validation_report.exists()
    assessment, assessment_note = final_assessment(radar_count, failed, warnings, required_present)

    missing = []
    if radar_count == 0:
        missing.append("radar-card files")
    if not combined_radar.exists():
        missing.append("combined radar artifact")
    if not keyword_index.exists():
        missing.append("radar keyword index artifact")
    if not validation_report.exists():
        missing.append("validation report")

    lines = []
    lines.append("# YTM Quality Pass")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Assessment: " + assessment)
    lines.append("")
    lines.append("## Package Checks")
    lines.append("")
    lines.append("- Radar-cards present: " + ("yes" if radar_count > 0 else "no"))
    lines.append("- Radar-card count: " + str(radar_count))
    lines.append("- Combined radar present: " + ("yes" if combined_radar.exists() else "no"))
    lines.append("- Radar keyword index present: " + ("yes" if keyword_index.exists() else "no"))
    lines.append("- Validation report present: " + ("yes" if validation_report.exists() else "no"))
    lines.append("- Validation passed count: " + str(passed))
    lines.append("- Validation warning count: " + str(warnings))
    lines.append("- Validation failed count: " + str(failed))
    lines.append("")
    lines.append("## Quality Assessment")
    lines.append("")
    lines.append("- Package usable for handoff preparation: " + ("yes" if assessment in {"usable", "review"} else "no"))
    lines.append("- Assessment note: " + assessment_note)
    lines.append("")
    lines.append("## Warnings / Follow-up Checks")
    lines.append("")
    if missing:
        for item in missing:
            lines.append("- Missing artifact: " + item)
    if warnings > 0:
        lines.append("- Validation warnings exist and should be reviewed.")
    if failed > 0:
        lines.append("- Validation failures exist and block a clean handoff package.")
    if not missing and warnings == 0 and failed == 0:
        lines.append("- No obvious package-level blockers detected in this deterministic quality pass.")
    lines.append("")
    lines.append("## Policy Notes")
    lines.append("")
    lines.append("- Public Source, Private Processing, Clean Output.")
    lines.append("- Quality pass is local-only runtime output and must not be committed.")
    lines.append("- Local model output is not source of truth.")
    lines.append("- This quality pass is a deterministic package check, not legal/compliance proof.")

    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic local-only YTM quality-pass artifact.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    radar_dir = run_dir / "derived" / "radar_cards"
    target = radar_dir / "qwinni_quality_pass_001.md"
    combined_radar = radar_dir / "all-video-radar-cards-combined.md"
    keyword_index = radar_dir / "radar_keyword_index_001.md"
    validation_report = radar_dir / "radar-card-validation-report.md"

    if not radar_dir.exists():
        raise SystemExit("Radar-card folder not found: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    cards = sorted(path for path in radar_dir.glob("*.radar-card.md") if path.is_file())
    if not cards:
        raise SystemExit("No *.radar-card.md files found in: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    counts = read_key_values(validation_report, ["Passed count", "Warning count", "Failed count"])
    passed = int(counts.get("Passed count", "0") or "0")
    warnings = int(counts.get("Warning count", "0") or "0")
    failed = int(counts.get("Failed count", "0") or "0")

    write_quality_pass(
        args.run_id,
        target,
        len(cards),
        passed,
        warnings,
        failed,
        combined_radar,
        keyword_index,
        validation_report,
    )

    print("QUALITY PASS", target)
    print("Radar-card count:", len(cards))
    print("Validation warnings:", warnings)
    print("Validation failed:", failed)
    print("Safety: quality pass is local-only runtime output. Do not commit.")


if __name__ == "__main__":
    main()
