# YTM Operator Story Recovery

## Purpose

This document defines the next planning direction for YTM v1.2.

The goal is not UI polish for its own sake, not donor-porting as a coding shortcut, and not feature creep.

The goal is to recover the old YTM v1.1 operator story on top of the safer v1.2 backend.

## 1. Core Operator Story

The operator gives a YouTube source, defines a sensible processing scope, starts one useful mining action, and receives a safe local handoff package with enough evidence to trust the run.

The operator should feel:

- I know what to feed into the system.
- I understand how large the run is.
- I understand what the system will attempt.
- I know where the run output will land.
- I can judge whether the run was useful without reading raw transcript content.

## 2. What Gave The Old YTM Wow Feeling

The old YTM felt compelling because it told a coherent story in a small number of steps:

- source in
- package size chosen
- transcript collection begins
- local AI processes the collected material
- radar/index/handoff comes out

The emotional effect did not come from dashboards.

It came from:

- a strong sense of direction
- visible transformation from source to artifact
- understandable run naming
- a feeling that the tool was doing meaningful work, not merely exposing plumbing

## 3. Correct Conceptual Flow

The correct YTM conceptual flow is:

```text
source
-> source size
-> processing scope
-> transcript coverage
-> local AI
-> radar/index
-> handoff
-> evidence
```

Meaning:

- `source`: one video, targeted package, list file, later channel/package classes
- `source size`: how many candidate videos were found or selected
- `processing scope`: full package, latest slice, oldest slice, limited run
- `transcript coverage`: how many succeeded, failed, skipped, or were unavailable
- `local AI`: only after transcript material exists
- `radar/index`: structure is produced from local transcript-derived input
- `handoff`: operator-facing result
- `evidence`: safe counts, paths, timing, validation status

## 4. Bad Concepts To Avoid

Avoid making these the primary operator story:

- operator limit as the main UI concept
- dashboard-first UI
- safety/debug/status panels dominating the first screen
- “pipeline” language as the main user-facing verb
- scattered controls that force the operator to infer the intended order

`limit` is important, but it is a safety cap, not the central mental model.

## 5. Correct UI Concepts

The UI should center around these concepts:

- processing scope
- source package
- transcript coverage
- content hours
- handoff evidence

These concepts are more intuitive than raw script-stage naming.

The operator should feel they are launching a bounded mining job, not manually orchestrating a dev pipeline.

## 6. Metrics Needed

The operator story needs these metrics as first-class safe outputs:

- found videos
- selected videos
- successful transcripts
- failed transcripts
- unavailable/member-only videos
- content hours
- time to transcript
- time to handoff
- radar-card count
- handoff path

These should be presented as safe evidence, not as raw transcript previews.

## 7. What v1.2 Already Has

Current v1.2 already provides a strong backend base:

- local run structure under `output/youtube_mining/<run_id>/`
- source intake from URL and list-file
- targeted video list support via local runtime list-file path
- transcript download
- VTT to TXT conversion
- transcript index
- model input manifest
- model packet generation
- local Ollama radar-card generation
- radar-card validation
- radar-card brief
- final YTM run summary
- one-command URL pipeline runner
- resume / skip-existing behavior for transcript download and TXT conversion
- safe summary preview and output folder helper
- public/private runtime boundary discipline

## 8. What v1.1 Donor Logic Should Inspire

The donor should inspire product logic and operator feeling, not direct code copying.

Useful inspiration points:

- simple “give source, choose scope, start” flow
- explicit source package concepts
- visible transcript language choice
- visible processing mode choice such as latest/oldest slice
- understandable run naming
- local model role explanation
- handoff as the emotional destination, not merely an implementation artifact
- transcript throttling awareness
- richer evidence framing around what happened in the run

## 9. What Must Stay Advanced / Diagnostic

These belong in advanced/diagnostic areas, not in the first-screen operator story:

- safety audit controls
- runtime boundary explanation
- previous local run inventory
- selected run artifact tables
- legacy URL pipeline controls
- optional manual step controls
- workspace dashboard
- raw command output
- implementation-stage placeholders

These tools remain valuable, but they are support surfaces, not the main operator experience.

## 10. Suggested Next Implementation Order

1. Recover the first-screen launcher story.
2. Replace stage-centric wording with mining/package/handoff wording.
3. Make safe result evidence clearer after a run.
4. Add transcript coverage metrics explicitly.
5. Add content-hours estimation from `video-list.txt` metadata.
6. Add timing evidence from run logs.
7. Reintroduce model-role explanation in a compact operator-friendly way.
8. Revisit channel-scale UX only after the bounded launcher story feels right.
9. Keep browser session handling parked until a separate safety decision is made.

## 11. Validation Queue

The following questions should be validated during the next implementation cycle:

- Does the first screen explain the intended operator flow within 5 seconds?
- Does the main button feel like it starts useful work rather than engineering plumbing?
- Does the operator understand run scope before starting?
- Does the post-run result explain success/failure using evidence instead of raw content?
- Are advanced/debug areas clearly secondary?
- Is the operator story stronger without weakening the public/private runtime boundary?

## Planning Note

YTM v1.2 should not chase the old implementation literally.

It should recover the old operator story with a safer structure:

- cleaner runtime separation
- better public repo compatibility
- smaller bounded runs
- better evidence
- less dashboard noise
