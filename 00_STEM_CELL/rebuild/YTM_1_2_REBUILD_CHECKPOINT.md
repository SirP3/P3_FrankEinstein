# YTM 1.2 Rebuild Checkpoint - FE v0.2

## Version / Context

- FE / Frenki is the carrier platform, currently v0.2.
- YTM is the first tool/module in the rebuild.
- FE v0.1 / YTM v1.1 is donor history.
- Current work is a safety-first rebuild/renovation toward YTM v1.2.
- This is intentionally not strict semantic versioning.

## Current Proven Pipeline

```text
YouTube URL
-> selected-video-ids.txt
-> transcript download
-> VTT to TXT
-> transcript index
-> model input manifest
-> model packet
-> local Ollama radar-card
-> radar-card validation
-> radar-card brief
-> full pipeline smoke report
-> final YTM run summary
```

## One-command Smoke Test

```bash
python3 apps/youtube_mining/scripts/run_ytm_pipeline_smoke.py youtube-intake-test-001 --model qwen2.5:7b --limit 1
```

The full pipeline smoke runner is also wired into the Streamlit UI and now ends with:

```text
handoffs/ytm_run_summary.md
```

The final runtime handoff chain is:

```text
operator_brief.md
radar_card_brief.md
ytm_pipeline_smoke_report.md
ytm_run_summary.md
```

The smoke runner includes the YTM run summary builder as its final stage.

## One-command URL Pipeline

The URL pipeline runner exists:

```text
apps/youtube_mining/scripts/run_ytm_url_pipeline.py
```

It can run the full YTM chain from a YouTube URL/video ID and run ID:

```text
YouTube URL + run_id
-> create run folder if missing
-> source intake
-> full pipeline smoke
-> final ytm_run_summary.md
```

Example:

```bash
python3 apps/youtube_mining/scripts/run_ytm_url_pipeline.py youtube-url-pipeline-test-001 --url "https://www.youtube.com/watch?v=tBOEhYs8vSQ" --model qwen2.5:7b --limit 1
```

Current proven final output:

```text
output/youtube_mining/<run_id>/handoffs/ytm_run_summary.md
```

The Streamlit UI now has a control for:

```text
Run full pipeline from YouTube URL
```

The UI can call:

```text
apps/youtube_mining/scripts/run_ytm_url_pipeline.py
```

This means the operator can run the URL pipeline from the UI, not only from terminal:

```text
YouTube URL + run ID
-> full YTM pipeline
-> final handoff: handoffs/ytm_run_summary.md
```

## YTM Core Baseline Acceptance

- Baseline name: YTM Core Baseline Accepted
- Acceptance run: `ytm-acceptance-001`
- Acceptance result: pass
- HEAD at acceptance: `9a53ea4 Update YTM checkpoint with URL pipeline`
- Final output: `output/youtube_mining/ytm-acceptance-001/handoffs/ytm_run_summary.md`
- Git status: clean
- Meaning: one-command URL pipeline can process a YouTube URL into a final runtime-only YTM run summary.
- Policy confirmation: runtime outputs stay under `output/youtube_mining/`.
- Limitation: this is a core pipeline baseline, not full production UI, not batch/channel processing, not RR/Reddit Radar.

## Current UI Run Summary

The Streamlit UI has a Run summary panel showing available/missing status for key runtime outputs:

- `derived/source_inventory.md`
- `derived/transcript_index.md`
- `derived/model_input_manifest.md`
- `derived/radar_cards/radar-card-validation-report.md`
- `handoffs/operator_brief.md`
- `handoffs/radar_card_brief.md`
- `handoffs/ytm_pipeline_smoke_report.md`
- `handoffs/ytm_run_summary.md`

The UI must not display:

- raw transcript content
- cleaned TXT transcript content
- model packet content
- full radar-card content

## Safety Policy

Public Source, Private Processing, Clean Output.

- Raw transcripts stay local-only.
- Cleaned TXT transcripts stay local-only.
- Model packets stay local-only.
- Radar-card outputs stay local-only.
- The public/committed repo contains workflow, scripts, prompts, and validators, not third-party content.

## Current Status

- Core pipeline works.
- One-command URL pipeline works.
- UI URL pipeline control exists.
- Final YTM run summary exists.
- Local radar-card generation works.
- Radar-card validation can pass.
- UI run summary panel exists.
- Batch/channel processing is not implemented.
- RR / Reddit Radar is not started yet.

## Next Likely Steps

- UI wiring for later pipeline stages.
- Run summary / operator dashboard.
- Docs cleanup.
- Later RR adapter after YTM baseline stabilizes.
