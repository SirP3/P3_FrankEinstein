#!/usr/bin/env python3
from pathlib import Path
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
FIELD_PATTERN = re.compile(r"^\s*(?:[-*]\s*)?([a-z_]+)\s*:\s*(.*)$")
LIST_FIELDS = {"source_keywords", "observed_patterns", "opportunities", "risks", "workflow_insights"}
STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "their", "them", "they", "using",
    "used", "about", "latest", "video", "videos", "speaker", "source", "internal", "output", "clean",
    "local", "runtime", "card", "cards", "summary", "none", "required", "derived", "content",
    "egy", "vagy", "mert", "hogy", "mint", "ezt", "azt", "csak", "már", "lesz", "nincs", "igen",
    "nem", "van", "itt", "aki", "ami", "egyik", "másik", "video", "videó", "videók", "személyes",
}


def field_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    current_field = ""
    parts: list[str] = []

    def flush_current() -> None:
        if current_field:
            values[current_field] = "\n".join(parts).strip()

    for line in text.splitlines():
        match = FIELD_PATTERN.match(line)
        field = match.group(1).lower() if match else ""
        if field:
            flush_current()
            current_field = field
            parts = [match.group(2).strip()]
            continue
        if current_field:
            parts.append(line.strip())

    flush_current()
    return values


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^0-9a-záéíóöőúüű_-]+", " ", text)
    tokens = []
    for token in text.split():
        token = token.strip("_-")
        if len(token) < 3 or token in STOPWORDS or token.isdigit():
            continue
        tokens.append(token)
    return tokens


def collect_keywords(card: Path) -> dict[str, object]:
    values = field_values(card.read_text(encoding="utf-8", errors="ignore"))
    buckets: list[str] = []
    for field in LIST_FIELDS:
        value = values.get(field, "")
        if value:
            buckets.append(value)
    keyword_counts: defaultdict[str, int] = defaultdict(int)
    for bucket in buckets:
        seen_in_card = set()
        for token in tokenize(bucket):
            if token in seen_in_card:
                continue
            keyword_counts[token] += 1
            seen_in_card.add(token)
    return {
        "file": card.name,
        "source_id": values.get("source_id", "").splitlines()[0].strip() if values.get("source_id") else "",
        "title": values.get("source_title", "").splitlines()[0].strip() if values.get("source_title") else "",
        "keywords": dict(keyword_counts),
    }


def write_index(run_id: str, radar_dir: Path, target: Path, card_records: list[dict[str, object]]) -> None:
    aggregate: defaultdict[str, int] = defaultdict(int)
    carriers: defaultdict[str, list[str]] = defaultdict(list)

    for record in card_records:
        card_name = str(record["file"])
        for keyword, count in dict(record["keywords"]).items():
            aggregate[keyword] += int(count)
            carriers[keyword].append(card_name)

    ranked = sorted(aggregate.items(), key=lambda item: (-item[1], item[0]))

    lines = []
    lines.append("# YTM Radar Keyword Index")
    lines.append("")
    lines.append("Run ID: " + run_id)
    lines.append("Generated UTC: " + datetime.now(timezone.utc).isoformat())
    lines.append("Input radar-card folder: " + str(radar_dir))
    lines.append("Radar-card count: " + str(len(card_records)))
    lines.append("Indexed keyword count: " + str(len(ranked)))
    lines.append("")
    lines.append("Note: keyword index is local-only runtime output and must not be committed.")
    lines.append("Note: this index is derived from radar-card fields, not from transcript bodies.")
    lines.append("Note: local model output is not source of truth.")
    lines.append("")
    lines.append("## Top Keywords")
    lines.append("")
    lines.append("| Keyword | Radar-card hits | Example radar cards |")
    lines.append("| --- | ---: | --- |")
    for keyword, count in ranked[:100]:
        examples = ", ".join(carriers[keyword][:3])
        lines.append("| " + keyword.replace("|", "/") + " | " + str(count) + " | " + examples.replace("|", "/") + " |")

    lines.append("")
    lines.append("## Per-card Keyword Snapshots")
    lines.append("")
    for record in card_records:
        local_ranked = sorted(dict(record["keywords"]).items(), key=lambda item: (-item[1], item[0]))[:12]
        lines.append("### " + str(record["file"]))
        lines.append("")
        lines.append("- Source ID: " + (str(record["source_id"]) or "not available"))
        lines.append("- Title: " + (str(record["title"]) or "not available"))
        lines.append("- Keywords: " + (", ".join(keyword for keyword, _ in local_ranked) if local_ranked else "not available"))
        lines.append("")

    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only radar keyword index from YTM radar-card files.")
    parser.add_argument("run_id")
    args = parser.parse_args()

    run_dir = OUTPUT_ROOT / args.run_id
    radar_dir = run_dir / "derived" / "radar_cards"
    target = radar_dir / "radar_keyword_index_001.md"

    if not radar_dir.exists():
        raise SystemExit("Radar-card folder not found: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    cards = sorted(path for path in radar_dir.glob("*.radar-card.md") if path.is_file())
    if not cards:
        raise SystemExit("No *.radar-card.md files found in: " + str(radar_dir) + "\nRun run_local_radar_card.py first.")

    records = [collect_keywords(card) for card in cards]
    write_index(args.run_id, radar_dir, target, records)

    print("RADAR KEYWORD INDEX", target)
    print("Radar-card count:", len(records))
    print("Safety: keyword index is local-only runtime output. Do not commit.")


if __name__ == "__main__":
    main()
