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
    print("stage | status | note")
    print("--- | --- | ---")
    for stage in stages:
        print(stage["name"] + " | " + stage["status"] + " | " + stage["note"].replace("\n", " / "))


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>").strip()


def write_report(
    run_id: str,
    input_mode: str,
    input_value: str,
    model: str,
    limit: int,
    skip_model: bool,
    stages: list[dict[str, str]],
    final_status: str,
) -> Path:
    handoffs_dir = OUTPUT_ROOT / run_id / "handoffs"
    handoffs_dir.mkdir(parents=True, exist_ok=True)
    report = handoffs_dir / "ytm_url_pipeline_report.md"

    lines = []
    lines.append("# YTM URL Pipeline Report")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input mode: " + input_mode)
    lines.append("Input value: " + input_value)
    lines.append("Model: " + model)
    lines.append("Limit: " + str(limit))
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

    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def run_stage(stages: list[dict[str, str]], name: str, script_name: str, args: list[str]) -> bool:
    ok, note = run_script(script_name, args)
    add_stage(stages, name, "passed" if ok else "failed", note or "completed")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full local-only YTM pipeline from YouTube source input.")
    parser.add_argument("run_id")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="YouTube URL or video ID")
    source.add_argument("--list-file", help="Local file containing YouTube URLs or video IDs")
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--langs", default="hu,en")
    parser.add_argument("--select-mode", choices=["all", "latest-5", "oldest-5"], default="all")
    parser.add_argument("--skip-model", action="store_true")
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    stages: list[dict[str, str]] = []
    final_status = "pass"

    smoke_args = [args.run_id, "--model", args.model, "--limit", str(args.limit), "--langs", args.langs]
    if args.skip_model:
        smoke_args.append("--skip-model")

    if args.url:
        source_args = ["--url", args.url]
        input_mode = "url"
        input_value = args.url
    else:
        source_args = ["--list-file", args.list_file]
        input_mode = "list-file"
        input_value = args.list_file

    pipeline = [
        ("create run folder", "create_run_folder.py", [args.run_id]),
        ("YouTube source intake", "intake_youtube_source.py", [args.run_id, *source_args, "--select-mode", args.select_mode]),
        ("full pipeline smoke", "run_ytm_pipeline_smoke.py", smoke_args),
    ]

    for name, script_name, stage_args in pipeline:
        if not run_stage(stages, name, script_name, stage_args):
            final_status = "fail"
            report = write_report(args.run_id, input_mode, input_value, args.model, args.limit, args.skip_model, stages, final_status)
            print_summary(stages)
            print("Final status:", final_status)
            print("Report path:", report)
            raise SystemExit(1)

    summary = OUTPUT_ROOT / args.run_id / "handoffs" / "ytm_run_summary.md"
    if not summary.exists():
        final_status = "fail"
        add_stage(stages, "final run summary", "failed", "missing handoffs/ytm_run_summary.md")
    else:
        add_stage(stages, "final run summary", "passed", "handoffs/ytm_run_summary.md")

    report = write_report(args.run_id, input_mode, input_value, args.model, args.limit, args.skip_model, stages, final_status)
    print_summary(stages)
    print("Final status:", final_status)
    print("Expected final output:", summary)
    print("Report path:", report)
    print("Safety: runtime output stays under output/youtube_mining/" + args.run_id + ". Do not commit.")

    if final_status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
