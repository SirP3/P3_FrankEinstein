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
```

## One-command Smoke Test

```bash
python3 apps/youtube_mining/scripts/run_ytm_pipeline_smoke.py youtube-intake-test-001 --model qwen2.5:7b --limit 1
```

## Safety Policy

Public Source, Private Processing, Clean Output.

- Raw transcripts stay local-only.
- Cleaned TXT transcripts stay local-only.
- Model packets stay local-only.
- Radar-card outputs stay local-only.
- The public/committed repo contains workflow, scripts, prompts, and validators, not third-party content.

## Current Status

- Core pipeline works.
- One-command smoke test works.
- Radar-card validation can reach pass.
- UI is not fully wired for the whole pipeline yet.
- Batch/channel processing is not implemented.
- RR / Reddit Radar is not started yet.

## Next Likely Steps

- UI wiring for later pipeline stages.
- Run summary / operator dashboard.
- Docs cleanup.
- Later RR adapter after YTM baseline stabilizes.
