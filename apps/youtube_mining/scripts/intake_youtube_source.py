#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def safe_run_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "run"


def extract_video_id(value: str) -> str:
    value = value.strip()
    match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{6,})", value)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", value):
        return value
    return ""


def video_url(video_id: str) -> str:
    return "https://www.youtube.com/watch?v=" + video_id


def require_yt_dlp() -> str:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        raise SystemExit("yt-dlp not found. Install yt-dlp or make it available on PATH before using --url intake.")
    return yt_dlp


def parse_printed_video_line(line: str) -> tuple[str, str]:
    parts = [part.strip() for part in line.split("\t")]
    while len(parts) < 5:
        parts.append("NA")

    video_id = parts[3]
    if not video_id or video_id == "NA":
        video_id = extract_video_id(parts[4])
    if not video_id:
        return "", ""

    date = parts[0] or "NA"
    duration = parts[1] or "NA"
    title = parts[2] or "untitled"
    url = parts[4] if parts[4] and parts[4] != "NA" else video_url(video_id)
    return video_id, " | ".join([date, duration, title, video_id, url])


def intake_from_url(source_url: str) -> tuple[list[str], list[str]]:
    yt_dlp = require_yt_dlp()
    lookup_value = source_url.strip()
    direct_video_id = extract_video_id(lookup_value)
    if direct_video_id and not re.search(r"https?://", lookup_value):
        lookup_value = video_url(direct_video_id)

    cmd = [
        yt_dlp,
        "--skip-download",
        "--flat-playlist",
        "--print",
        "%(upload_date)s\t%(duration_string)s\t%(title)s\t%(id)s\t%(webpage_url)s",
        lookup_value,
    ]
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise SystemExit("yt-dlp source intake failed:\n" + result.stderr.strip())

    ids = []
    video_lines = []
    seen = set()
    for raw_line in result.stdout.splitlines():
        video_id, video_line = parse_printed_video_line(raw_line)
        if video_id and video_id not in seen:
            ids.append(video_id)
            video_lines.append(video_line)
            seen.add(video_id)

    if not ids and direct_video_id:
        ids.append(direct_video_id)
        video_lines.append("NA | NA | direct-video | " + direct_video_id + " | " + video_url(direct_video_id))

    if not ids:
        raise SystemExit("No video IDs were discovered from the provided YouTube input.")

    return ids, video_lines


def intake_from_list_file(list_file: Path) -> tuple[list[str], list[str]]:
    if not list_file.exists() or not list_file.is_file():
        raise SystemExit("List file not found: " + str(list_file))

    ids = []
    video_lines = []
    seen = set()
    for raw_line in list_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        value = raw_line.strip()
        if not value or value.startswith("#"):
            continue
        video_id = extract_video_id(value)
        if not video_id:
            continue
        if video_id in seen:
            continue
        ids.append(video_id)
        video_lines.append("NA | NA | local-list | " + video_id + " | " + video_url(video_id))
        seen.add(video_id)

    if not ids:
        raise SystemExit("No video IDs were found in list file: " + str(list_file))

    return ids, video_lines


def write_source_files(source_dir: Path, ids: list[str], video_lines: list[str], mode: str, input_value: str) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "selected-video-ids.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    (source_dir / "video-list.txt").write_text("\n".join(video_lines) + "\n", encoding="utf-8")

    log_lines = []
    log_lines.append("# YouTube Source Intake Log")
    log_lines.append("")
    log_lines.append("Run ID: " + source_dir.parent.name)
    log_lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    log_lines.append("Input mode: " + mode)
    log_lines.append("Input value: " + input_value)
    log_lines.append("Selected videos: " + str(len(ids)))
    log_lines.append("")
    log_lines.append("Note: source intake only. No transcript download has been performed yet.")
    log_lines.append("Note: runtime output is local-only.")
    (source_dir / "source-intake-log.md").write_text("\n".join(log_lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create local-only YouTube source intake files for a YTM run.")
    parser.add_argument("run_id")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="YouTube video, playlist, channel/videos URL, or video ID")
    source.add_argument("--list-file", help="Local file containing YouTube URLs or video IDs")
    args = parser.parse_args()

    run_id = safe_run_id(args.run_id)
    source_dir = OUTPUT_ROOT / run_id / "source"

    if args.url:
        ids, video_lines = intake_from_url(args.url)
        mode = "url"
        input_value = args.url
    else:
        list_file = Path(args.list_file).expanduser().resolve()
        ids, video_lines = intake_from_list_file(list_file)
        mode = "list-file"
        input_value = str(list_file)

    write_source_files(source_dir, ids, video_lines, mode, input_value)
    print("SOURCE INTAKE", source_dir)
    print("Selected videos:", len(ids))
    print("Wrote:", source_dir / "selected-video-ids.txt")
    print("Wrote:", source_dir / "video-list.txt")
    print("Wrote:", source_dir / "source-intake-log.md")
    print("Safety: local-only runtime output. Do not commit.")


if __name__ == "__main__":
    main()
