#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

BRIEF_FIELDS = [
    "source_id",
    "source_title",
    "primary_scope",
    "action_class",
    "signal_strength",
    "noise_risk",
    "confidence",
    "transcript_reopen",
    "finance_trading_quarantine",
    "clean_summary",
    "validation_notes",
]

VALIDATION_FIELDS = [
    "Radar-card count",
    "Passed count",
    "Warning count",
    "Failed count",
]

FIELD_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?([a-z_]+)\s*:\s*(.*)$")


def field_values(text: str, allowed_fields: list[str]) -> dict[str, str]:
    allowed = set(allowed_fields)
    values = {}
    current_field = ""
    parts = []

    def flush_current() -> None:
        if current_field:
            values[current_field] = "\n".join(parts).strip()

    for line in text.splitlines():
        match = FIELD_PATTERN.match(line)
        field = match.group(1).lower() if match else ""

        if field in allowed:
            flush_current()
            current_field = field
            parts = [match.group(2).strip()]
            continue

        if current_field:
            parts.append(line.strip())

    flush_current()
    return values


def first_scalar(value: str) -> str:
    for line in value.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def compact_multiline(value: str, max_chars: int = 500) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        return text[: max_chars - 3].rstrip() + "..."
    return text


def markdown_cell(value: str) -> str:
    value = value.replace("|", "\\|")
    value = value.replace("\n", " ")
    return value.strip() or "not set"


def validation_summary(report_path: Path) -> dict[str, str]:
    if not report_path.exists():
        return {field: "not available" for field in VALIDATION_FIELDS}

    values = {}
    for line in report_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for field in VALIDATION_FIELDS:
            prefix = field + ":"
            if line.startswith(prefix):
                values[field] = line[len(prefix):].strip()

    return {field: values.get(field, "not available") for field in VALIDATION_FIELDS}


def card_summary(card: Path) -> dict[str, str]:
    text = card.read_text(encoding="utf-8", errors="ignore")
    values = field_values(text, BRIEF_FIELDS)
    summary = {"file": card.name}

    for field in BRIEF_FIELDS:
        if field in {"clean_summary", "validation_notes"}:
            summary[field] = compact_multiline(values.get(field, ""))
        else:
            summary[field] = first_scalar(values.get(field, ""))

    return summary


def write_brief(run_id: str, handoffs_dir: Path, validation: dict[str, str], cards: list[dict[str, str]]) -> Path:
    brief_path = handoffs_dir / "radar_card_brief.md"
    lines = []
    lines.append("# YTM Radar Card Brief")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    lines.append("- Radar-card count: " + validation["Radar-card count"])
    lines.append("- Passed count: " + validation["Passed count"])
    lines.append("- Warning count: " + validation["Warning count"])
    lines.append("- Failed count: " + validation["Failed count"])
    lines.append("")
    lines.append("## Per-card Summary")
    lines.append("")
    lines.append(
        "| File | Source ID | Title | Scope | Action | Signal | Noise | Confidence | Reopen | Finance quarantine |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for card in cards:
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(card["file"]),
                    markdown_cell(card["source_id"]),
                    markdown_cell(card["source_title"]),
                    markdown_cell(card["primary_scope"]),
                    markdown_cell(card["action_class"]),
                    markdown_cell(card["signal_strength"]),
                    markdown_cell(card["noise_risk"]),
                    markdown_cell(card["confidence"]),
                    markdown_cell(card["transcript_reopen"]),
                    markdown_cell(card["finance_trading_quarantine"]),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Short Notes")
    lines.append("")
    for card in cards:
        lines.append("### " + card["file"])
        lines.append("")
        lines.append("- Clean summary: " + markdown_cell(card["clean_summary"]))
        lines.append("- Validation notes: " + markdown_cell(card["validation_notes"]))
        lines.append("")

    lines.append("## Policy Notes")
    lines.append("")
    lines.append("- Public Source, Private Processing, Clean Output.")
    lines.append("- Local model output is not source of truth.")
    lines.append("- Runtime-only handoff, do not commit.")

    brief_path.write_text("\n".join(lines), encoding="utf-8")
    return brief_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only YTM radar-card handoff brief.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    radar_dir = run_dir / "derived" / "radar_cards"
    handoffs_dir = run_dir / "handoffs"

    if not radar_dir.exists():
        raise SystemExit("Radar-card folder not found: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    card_paths = sorted(path for path in radar_dir.glob("*.radar-card.md") if path.is_file())
    if not card_paths:
        raise SystemExit("No *.radar-card.md files found in: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    handoffs_dir.mkdir(parents=True, exist_ok=True)
    validation = validation_summary(radar_dir / "radar-card-validation-report.md")
    cards = [card_summary(path) for path in card_paths]
    brief_path = write_brief(args.run_id, handoffs_dir, validation, cards)

    print("RADAR CARD BRIEF", brief_path)
    print("Radar-card count:", len(cards))
    print("Safety: handoff brief is local-only runtime data. Do not commit.")


if __name__ == "__main__":
    main()
