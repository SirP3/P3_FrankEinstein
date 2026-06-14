#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def validation_counts(report: Path) -> dict[str, str]:
    labels = ["Radar-card count", "Passed count", "Warning count", "Failed count"]
    values = {}
    if not report.exists():
        return values
    for line in report.read_text(encoding="utf-8", errors="ignore").splitlines():
        for label in labels:
            prefix = label + ":"
            if line.startswith(prefix):
                values[label] = line[len(prefix):].strip()
    return values


def write_combined(run_id: str, radar_dir: Path, cards: list[Path], target: Path) -> None:
    report = radar_dir / "radar-card-validation-report.md"
    counts = validation_counts(report)

    lines = []
    lines.append("# YTM Combined Radar")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input radar-card folder: " + str(radar_dir))
    lines.append("Radar-card count: " + str(len(cards)))
    lines.append("Validation passed count: " + counts.get("Passed count", "not available"))
    lines.append("Validation warning count: " + counts.get("Warning count", "not available"))
    lines.append("Validation failed count: " + counts.get("Failed count", "not available"))
    lines.append("")
    lines.append("Note: combined radar is local-only runtime output and must not be committed.")
    lines.append("Note: local model output is not source of truth.")
    lines.append("Note: this file combines local radar-card outputs without exposing transcript or model packet files in the public repo.")
    lines.append("")
    lines.append("## Included Radar Cards")
    lines.append("")
    for card in cards:
        lines.append("- " + card.name)
    lines.append("")
    lines.append("## Combined Radar Content")
    lines.append("")

    for index, card in enumerate(cards, start=1):
        lines.append("### Radar Card " + str(index) + ": " + card.name)
        lines.append("")
        lines.append(card.read_text(encoding="utf-8", errors="ignore").rstrip())
        lines.append("")

    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only combined radar artifact from YTM radar-card files.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    radar_dir = run_dir / "derived" / "radar_cards"
    target = radar_dir / "all-video-radar-cards-combined.md"

    if not radar_dir.exists():
        raise SystemExit("Radar-card folder not found: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    cards = sorted(path for path in radar_dir.glob("*.radar-card.md") if path.is_file())
    if not cards:
        raise SystemExit("No *.radar-card.md files found in: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    write_combined(args.run_id, radar_dir, cards, target)

    print("COMBINED RADAR", target)
    print("Radar-card count:", len(cards))
    print("Safety: combined radar is local-only runtime output. Do not commit.")


if __name__ == "__main__":
    main()
