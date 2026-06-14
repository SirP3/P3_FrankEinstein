#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
SCRIPT_DIR = ROOT / "apps" / "youtube_mining" / "scripts"


def run_script(script_name: str, args: list[str]) -> tuple[bool, str]:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    note = result.stdout.strip()
    if len(note) > 700:
        note = note[-700:].strip()
    return result.returncode == 0, note


def add_stage(stages: list[dict[str, str]], name: str, status: str, note: str) -> None:
    stages.append({"name": name, "status": status, "note": note})


def print_summary(stages: list[dict[str, str]]) -> None:
    print("stage name | status | note")
    print("--- | --- | ---")
    for stage in stages:
        print(stage["name"] + " | " + stage["status"] + " | " + stage["note"].replace("\n", " / "))


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>").strip()


def write_report(run_id: str, model: str, skip_model: bool, stages: list[dict[str, str]], final_status: str) -> Path:
    handoffs_dir = OUTPUT_ROOT / run_id / "handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)
    report = handoffs_dir / "ytm_pipeline_smoke_report.md"

    lines = []
    lines.append("# YTM Pipeline Smoke Report")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Model name: " + model)
    lines.append("Skip-model: " + ("yes" if skip_model else "no"))
    lines.append("Final status: " + final_status)
    lines.append("")
    lines.append("## Stage Summary")
    lines.append("")
    lines.append("| Stage | Status | Note |")
    lines.append("| --- | --- | --- |")
    for stage in stages:
        lines.append(
            "| "
            + markdown_cell(stage["name"])
            + " | "
            + markdown_cell(stage["status"])
            + " | "
            + markdown_cell(stage["note"])
            + " |"
        )
    lines.append("")
    lines.append("## Policy Notes")
    lines.append("")
    lines.append("- Public Source, Private Processing, Clean Output.")
    lines.append("- Runtime-only report, do not commit.")
    lines.append("- Local model output is not source of truth.")

    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def has_radar_cards(run_id: str) -> bool:
    radar_dir = OUTPUT_ROOT / run_id / "derived" / "radar_cards"
    return radar_dir.exists() and any(path.is_file() for path in radar_dir.glob("*.radar-card.md"))


def failed_validation(note: str) -> bool:
    for line in note.splitlines():
        if line.startswith("Failed count:"):
            try:
                return int(line.split(":", 1)[1].strip()) > 0
            except ValueError:
                return True
    return False


def run_required_stage(stages: list[dict[str, str]], name: str, script_name: str, args: list[str]) -> bool:
    ok, note = run_script(script_name, args)
    add_stage(stages, name, "passed" if ok else "failed", note or "completed")
    return ok


def refresh_run_summary(run_id: str) -> bool:
    ok, _ = run_script("build_ytm_run_summary.py", [run_id])
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the existing YTM v0.2 pipeline as a local smoke test.")
    parser.add_argument("run_id")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--skip-model", action="store_true")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--langs", default="hu,en")
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    stages: list[dict[str, str]] = []
    final_status = "pass"

    required_stages = [
        ("build derived placeholder", "build_derived_placeholder.py", [args.run_id]),
        ("build operator brief placeholder", "build_operator_brief_placeholder.py", [args.run_id]),
        ("download transcript", "download_youtube_transcripts.py", [args.run_id, "--langs", args.langs, "--limit", str(args.limit)]),
        ("convert VTT to TXT", "convert_vtt_to_txt.py", [args.run_id, "--limit", str(args.limit)]),
        ("build transcript index", "build_transcript_index.py", [args.run_id]),
        ("build model input manifest", "build_model_input_manifest.py", [args.run_id]),
        ("build model packet", "build_model_packet.py", [args.run_id]),
    ]

    for name, script_name, stage_args in required_stages:
        if not run_required_stage(stages, name, script_name, stage_args):
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

    if args.skip_model:
        add_stage(stages, "run local radar-card model", "skipped", "--skip-model was provided")
    else:
        ok = run_required_stage(
            stages,
            "run local radar-card model",
            "run_local_radar_card.py",
            [args.run_id, "--model", args.model, "--limit", str(args.limit)],
        )
        if not ok:
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

    if args.skip_model and not has_radar_cards(args.run_id):
        add_stage(stages, "validate radar cards", "skipped", "no existing radar-card files available")
        add_stage(stages, "build radar-card brief", "skipped", "no existing radar-card files available")
    else:
        ok, note = run_script("validate_radar_cards.py", [args.run_id])
        validation_failed = ok and failed_validation(note)
        status = "passed" if ok and not validation_failed else "failed"
        add_stage(stages, "validate radar cards", status, note or "completed")
        if status == "failed":
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

        if not run_required_stage(stages, "build combined radar", "build_combined_radar.py", [args.run_id]):
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

        if not run_required_stage(stages, "build radar keyword index", "build_radar_keyword_index.py", [args.run_id]):
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

        if not run_required_stage(stages, "build quality pass", "build_quality_pass.py", [args.run_id]):
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

        if not run_required_stage(stages, "build radar-card brief", "build_radar_card_brief.py", [args.run_id]):
            final_status = "fail"
            report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Report path:", report)
            raise SystemExit(1)

    if not run_required_stage(stages, "build YTM run summary", "build_ytm_run_summary.py", [args.run_id]):
        final_status = "fail"
        report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
        print_summary(stages)
        print("Report path:", report)
        raise SystemExit(1)

    report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
    if not refresh_run_summary(args.run_id):
        final_status = "fail"
        report = write_report(args.run_id, args.model, args.skip_model, stages, final_status)
        print_summary(stages)
        print("Report path:", report)
        raise SystemExit(1)
    print_summary(stages)
    print("Final status:", final_status)
    print("Report path:", report)
    print("Safety: smoke report is local-only runtime data. Do not commit.")


if __name__ == "__main__":
    main()
