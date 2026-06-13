#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

REQUIRED_FIELDS = [
    "source_id",
    "source_title",
    "source_type",
    "primary_scope",
    "action_class",
    "signal_strength",
    "noise_risk",
    "confidence",
    "transcript_reopen",
    "finance_trading_quarantine",
    "source_keywords",
    "observed_patterns",
    "opportunities",
    "risks",
    "workflow_insights",
    "clean_summary",
    "validation_notes",
    "source_attribution_note",
]

CONTROLLED_VALUES = {
    "primary_scope": {"ai_tool", "workflow", "business", "education", "finance_trading", "generic_noise", "unknown"},
    "action_class": {"keep", "watch", "quarantine", "discard", "reopen_later"},
    "signal_strength": {"low", "medium", "high"},
    "noise_risk": {"low", "medium", "high"},
    "confidence": {"low", "medium", "high"},
    "transcript_reopen": {"yes", "no", "maybe"},
    "finance_trading_quarantine": {"yes", "no", "not_applicable"},
}

POLICY_CONTEXT_TERMS = ("policy", "validation", "guardrail", "checklist", "note")


def field_values(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        for field in REQUIRED_FIELDS:
            prefix = field + ":"
            if line.lower().startswith(prefix):
                values[field] = line.split(":", 1)[1].strip()
    return values


def clean_output_warnings(text: str) -> list[str]:
    warnings = []
    lines = text.splitlines()

    long_lines = [index + 1 for index, line in enumerate(lines) if len(line) > 500]
    if long_lines:
        warnings.append("line longer than 500 characters: " + ", ".join(str(item) for item in long_lines[:5]))

    clean_summary_total = 0
    for line in lines:
        if line.lower().startswith("clean_summary:"):
            clean_summary_total += len(line.split(":", 1)[1].strip())
    if clean_summary_total > 3000:
        warnings.append("clean_summary content longer than 3000 characters")

    quote_count = text.count('"') + text.count("'")
    if quote_count > 40:
        warnings.append("suspicious quote density")

    if "00:00:" in text or "WEBVTT" in text:
        warnings.append("obvious transcript timing pattern found")

    for phrase in ["transcript content", "raw transcript"]:
        for line in lines:
            lowered = line.lower()
            if phrase in lowered and not any(term in lowered for term in POLICY_CONTEXT_TERMS):
                warnings.append("phrase outside policy context: " + phrase)
                break

    return warnings


def validate_card(card: Path) -> dict[str, object]:
    text = card.read_text(encoding="utf-8", errors="ignore")
    values = field_values(text)
    missing = [field for field in REQUIRED_FIELDS if field not in values]
    invalid = []

    for field, allowed in CONTROLLED_VALUES.items():
        value = values.get(field, "").strip()
        if value and value not in allowed:
            invalid.append(field + "=" + value)

    warnings = clean_output_warnings(text)
    status = "passed"
    if missing or invalid:
        status = "failed"
    elif warnings:
        status = "warning"

    return {
        "file": card.name,
        "status": status,
        "missing": missing,
        "invalid": invalid,
        "warnings": warnings,
    }


def write_report(run_id: str, radar_dir: Path, results: list[dict[str, object]]) -> Path:
    report = radar_dir / "radar-card-validation-report.md"
    passed = sum(1 for item in results if item["status"] == "passed")
    warned = sum(1 for item in results if item["status"] == "warning")
    failed = sum(1 for item in results if item["status"] == "failed")

    lines = []
    lines.append("# YTM Radar Card Validation Report")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input radar-card folder: " + str(radar_dir))
    lines.append("Radar-card count: " + str(len(results)))
    lines.append("Passed count: " + str(passed))
    lines.append("Warning count: " + str(warned))
    lines.append("Failed count: " + str(failed))
    lines.append("")
    lines.append("Note: validator does not prove legal compliance.")
    lines.append("Note: local model output is not source of truth.")
    lines.append("Note: radar-card outputs and validation reports are runtime-only and must not be committed.")
    lines.append("")
    lines.append("## Per-file Status")
    lines.append("")

    for item in results:
        lines.append("### " + str(item["file"]))
        lines.append("")
        lines.append("Status: " + str(item["status"]))
        lines.append("")
        lines.append("Missing fields: " + (", ".join(item["missing"]) if item["missing"] else "none"))
        lines.append("Invalid controlled vocabulary values: " + (", ".join(item["invalid"]) if item["invalid"] else "none"))
        lines.append("Clean-output warnings: " + (", ".join(item["warnings"]) if item["warnings"] else "none"))
        lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate local-only YTM radar-card outputs.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    radar_dir = OUTPUT_ROOT / args.run_id / "derived" / "radar_cards"

    if not radar_dir.exists():
        raise SystemExit("Radar-card folder not found: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    cards = sorted([
        path for path in radar_dir.glob("*.md")
        if path.is_file()
        and path.name not in {"radar-card-run-log.md", "radar-card-validation-report.md"}
    ])
    if not cards:
        raise SystemExit("No radar-card .md files found in: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    results = [validate_card(card) for card in cards]
    report = write_report(args.run_id, radar_dir, results)

    passed = sum(1 for item in results if item["status"] == "passed")
    warned = sum(1 for item in results if item["status"] == "warning")
    failed = sum(1 for item in results if item["status"] == "failed")

    print("Radar-card count:", len(results))
    print("Passed count:", passed)
    print("Warning count:", warned)
    print("Failed count:", failed)
    print("Report path:", report)


if __name__ == "__main__":
    main()
