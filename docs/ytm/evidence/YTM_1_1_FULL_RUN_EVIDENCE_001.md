# YTM 1.1 Full-Run Evidence - 001

## Evidence Source

- Snapshot path: `local v0.1 archive snapshot / _ytm_watch_snapshots / ytm11_FINAL_snapshot_20260614_200948.txt`
- Observed date/time from snapshot: `2026 jún. 14 V 20:09:48 CEST`
- Evidence base: file names, sizes, timestamps, running-process list, and folder counts visible in the snapshot

## Observed Run Folder

- Run folder: `sample-full-channel-run-26W24`
- Observed path:
  `local v0.1 archive / modules / youtube-mining / transcripts / sample-full-channel-run-26W24`
- Observed folder size: `14M`

## Key Generated Artifacts Observed

- `all-video-radar-cards-combined.md` - `307814` bytes
- `radar_keyword_index_001.md` - `106239` bytes
- `qwinni_quality_pass_001.md` - `695` bytes
- `handoff package artifact` - `487409` bytes
- `handoff package artifact 002` - `487409` bytes
- `run-bound handoff package artifact` - `487409` bytes

## Radar-Card Evidence

- Observed radar-card count for this folder: `206`
- Snapshot shows both `.hu.radar-card.md` and `.en.radar-card.md` files under the same run folder
- This is direct evidence that bilingual Hungarian/English radar-card output existed for the run

Inference:

The snapshot strongly suggests one bilingual radar-card pair per processed source item in many cases, but the exact pairing completeness is not proven by this snapshot alone.

## Observed Full-Run Flow

Based on the artifact set visible in the snapshot, the observed run appears to have produced:

```text
run folder
-> radar-cards/
-> all-video-radar-cards-combined.md
-> radar_keyword_index_001.md
-> qwinni_quality_pass_001.md
-> handoff package variants
```

Inference:

This is consistent with a larger end-to-end YTM 1.1 full-run workflow where transcript-derived material was processed into radar output, indexed, quality-checked, and then assembled into a large handoff package artifact.

The snapshot does not by itself prove every internal stage in sequence, but it does prove the existence of the final artifact family.

## Operator Value Proven

The snapshot demonstrates that the old YTM 1.1 system could produce a substantial operator-facing work package from one full-channel run:

- many radar-card outputs
- bilingual radar-card evidence
- a combined radar file
- a keyword index
- a quality-pass file
- a large final handoff package artifact

This is the key operator value signal:

The system did not stop at transcript collection. It produced a transferable, reviewable work package with multiple layers of structured output.

## Lessons For YTM v1.2

- The operator value was in the output package, not in the intermediate plumbing.
- Radar-card count matters as visible evidence.
- Bilingual output mattered enough to be reflected in filenames.
- The combined radar file and keyword index were part of the usable package.
- A quality-pass layer existed as a visible artifact, not only as hidden logic.
- The handoff package artifact was the emotional and practical destination of the run.

## Validation Queue

The following points are not yet proven by this snapshot alone:

- the exact source input used in the run
- the exact transcript success/failure counts
- whether every source item received both HU and EN radar-card outputs
- the exact internal ordering and duration of each stage
- the exact model names used in this specific run
- whether the handoff package artifact quality was operator-useful without later human cleanup

## Safe Conclusion

This snapshot is sufficient to record one important historical fact:

YTM 1.1 demonstrably produced a full output package for a sample full-channel run, including a large handoff package artifact, keyword index, quality-pass file, combined radar file, and `206` radar-card outputs with visible HU/EN bilingual evidence.
