#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"


def video_url(video_id: str) -> str:
    return "https://www.youtube.com/watch?v=" + video_id


def require_yt_dlp() -> str:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        raise SystemExit("yt-dlp not found. Install yt-dlp or make it available on PATH before transcript download.")
    return yt_dlp


def read_selected_video_ids(run_dir: Path) -> list[str]:
    ids_file = run_dir / "source" / "selected-video-ids.txt"
    if not ids_file.exists():
        raise SystemExit("Selected video IDs file not found: " + str(ids_file))

    ids = [line.strip() for line in ids_file.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    if not ids:
        raise SystemExit("Selected video IDs file is empty: " + str(ids_file))

    return ids


def existing_transcript_files(transcripts_dir: Path, video_id: str) -> list[Path]:
    if not transcripts_dir.exists():
        return []
    return sorted([
        path for path in transcripts_dir.glob("*_" + video_id + "_*")
        if path.is_file() and path.stat().st_size > 0
        and path.suffix.lower().removeprefix(".") == "vtt"
    ])


def download_transcripts(video_ids: list[str], transcripts_dir: Path, langs: str, limit: int) -> tuple[list[str], dict[str, int]]:
    yt_dlp = require_yt_dlp()
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    results = []
    counts = {
        "processed_attempts": 0,
        "successful": 0,
        "failed": 0,
        "skipped_existing": 0,
        "skipped_by_limit": 0,
    }

    for video_id in video_ids:
        if existing_transcript_files(transcripts_dir, video_id):
            counts["skipped_existing"] += 1
            results.append("skipped existing transcript " + video_id)
            continue
        if counts["processed_attempts"] >= limit:
            counts["skipped_by_limit"] += 1
            results.append("limit reached before " + video_id)
            continue

        before = set(existing_transcript_files(transcripts_dir, video_id))
        cmd = [
            yt_dlp,
            "--skip-download",
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs",
            langs,
            "--sub-format",
            "vtt",
            "-o",
            str(transcripts_dir / "%(upload_date)s_%(id)s_%(title).80s.%(ext)s"),
            video_url(video_id),
        ]
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        after = set(existing_transcript_files(transcripts_dir, video_id))
        wrote_new = bool(after - before)
        status = "ok" if wrote_new else "warning"
        results.append(status + " " + video_id)
        counts["processed_attempts"] += 1
        if wrote_new:
            counts["successful"] += 1
        else:
            counts["failed"] += 1
        if result.stdout.strip():
            results.append(result.stdout.strip()[-1200:])

    return results, counts


def write_log(run_id: str, run_dir: Path, selected_count: int, counts: dict[str, int], limit: int, langs: str, output_folder: Path) -> None:
    log_path = run_dir / "source" / "transcript-intake-log.md"
    outcome = "complete"
    if counts["failed"] > 0 or counts["skipped_by_limit"] > 0:
        outcome = "incomplete"
    lines = []
    lines.append("# YouTube Transcript Intake Log")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Selected video count: " + str(selected_count))
    lines.append("Processed video count: " + str(counts["processed_attempts"]))
    lines.append("Successful transcript count: " + str(counts["successful"]))
    lines.append("Failed transcript count: " + str(counts["failed"]))
    lines.append("Skipped existing count: " + str(counts["skipped_existing"]))
    lines.append("Skipped by limit count: " + str(counts["skipped_by_limit"]))
    lines.append("Processing limit: " + str(limit))
    lines.append("Language setting: " + langs)
    lines.append("Transcript outcome status: " + outcome)
    lines.append("Output folder: " + str(output_folder))
    lines.append("")
    lines.append("Note: transcript files are runtime source data and must not be committed.")
    lines.append("Note: no AI, model, or radar-card processing has been performed yet.")
    log_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download local-only YouTube transcript files for a YTM run.")
    parser.add_argument("run_id")
    parser.add_argument("--langs", default="hu,en")
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    run_dir = OUTPUT_ROOT / args.run_id
    video_ids = read_selected_video_ids(run_dir)
    transcripts_dir = run_dir / "source" / "transcripts"

    results, counts = download_transcripts(video_ids, transcripts_dir, args.langs, args.limit)
    write_log(args.run_id, run_dir, len(video_ids), counts, args.limit, args.langs, transcripts_dir)

    print("TRANSCRIPT INTAKE", transcripts_dir)
    print("Selected video count:", len(video_ids))
    print("Processed video count:", counts["processed_attempts"])
    print("Successful transcript count:", counts["successful"])
    print("Failed transcript count:", counts["failed"])
    print("Skipped existing count:", counts["skipped_existing"])
    print("Skipped by limit count:", counts["skipped_by_limit"])
    print("Processing limit:", args.limit)
    print("Language setting:", args.langs)
    print("Wrote:", run_dir / "source" / "transcript-intake-log.md")
    print("Safety: transcript files are local-only runtime source data. Do not commit.")
    if results:
        print()
        print("yt-dlp results:")
        for item in results:
            print(item)


if __name__ == "__main__":
    main()
