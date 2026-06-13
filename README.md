# P3_FrankEinstein

Experimental AI workshop for source mining, workflow discovery, and knowledge-system prototyping.

The goal is not content collection, but signal discovery, workflow discovery, and opportunity discovery from public sources.

P3_FrankEinstein is the first carrier/workbench inside the broader P3 system. "Frenki" is only an internal nickname, not the public product name.

The first active tool/module is YTM, a YouTube/source-mining adapter. FE v0.1 / YTM v1.1 are treated as donor history and learning input, not as the current source of truth. The current public baseline is a safety-first rebuild toward YTM 1.2.

## Policy

Public Source, Private Processing, Clean Output.

- Public/free sources may be processed locally and privately.
- Source transcript data, model packets, and runtime outputs stay local-only.
- The public repository contains workflow code, safety checks, prompts, validators, and documentation.
- The repository should not contain third-party source content or private runtime data.

Source != Output: the goal is to generate new insights, classifications, workflows, and decision-support artifacts rather than reproduce source material.

## Current Capabilities

- YouTube URL pipeline.
- Transcript intake.
- Cleaned local TXT generation.
- Metadata-only indexes.
- Local model packet generation.
- Local Ollama radar-card runner.
- Radar-card validation.
- Final runtime run summary.
- Streamlit UI controls for key workflow steps.

## Current Limitations

- Not a production service.
- Not legal or compliance proof.
- No batch/channel-scale processing yet.
- No RR / Reddit Radar implementation yet.
- Local model output is not source of truth.
- Runtime output is intentionally gitignored.
- Cross-source validation is still largely manual.

## Quick Start

From the repository root:

```bash
python3 apps/youtube_mining/scripts/run_ytm_url_pipeline.py ytm-example-001 --url "https://www.youtube.com/watch?v=tBOEhYs8vSQ" --model qwen2.5:7b --limit 1
```

Expected final local-only output:

```text
output/youtube_mining/<run_id>/handoffs/ytm_run_summary.md
```

## License

No license is currently granted. This is a public research/workshop repository; usage rights may be clarified later.

## Direction

Current focus: YTM 1.2 Safety-First Rebuild.

Future directions:

- RR / Reddit Radar.
- GitHub validation workflows.
- Cross-source signal validation.
