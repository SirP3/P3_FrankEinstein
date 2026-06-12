# YTM Local Runtime Boundary

## Purpose

This file defines where the YouTube Mining adapter may read and write during local execution.

The goal is to prevent source-derived or private material from entering committed code paths.

## Core rule

App code is commit-safe.

Runtime output is local-only.

## Committed app path

The committed app lives under:

`apps/youtube_mining/`

Allowed here:

- source code
- generic documentation
- generic config templates
- tests without private/source-derived data
- placeholder examples only

Not allowed here:

- transcripts
- VTT/TXT source files
- real radar cards
- handoff packs
- source-derived notes
- private prompts
- private market context
- local model cache
- cookies
- credentials
- run output

## Local runtime output root

Future YTM runtime output should go under the ignored root:

`output/youtube_mining/`

This folder is local-only and ignored by git.

## Target run structure

A future local run should look like:

`output/youtube_mining/<run_id>/source/`
`output/youtube_mining/<run_id>/derived/`
`output/youtube_mining/<run_id>/handoffs/`
`output/youtube_mining/<run_id>/archive/`
`output/youtube_mining/<run_id>/run-info.md`

## Source folder

The source folder may contain:

- downloaded subtitles
- converted text
- comments if enabled later
- source metadata

Safety:
- local-only
- never commit by default

## Derived folder

The derived folder may contain:

- radar-card output
- quality-pass notes
- structured indexes
- intermediate model outputs

Safety:
- local-only
- must be reviewed before any extract is committed

## Handoffs folder

The handoffs folder may contain:

- full handoff packs
- operator briefs
- validation queues
- archive notes

Safety:
- local-only by default
- only anonymized summaries may become committed docs

## Archive folder

The archive folder may contain:

- failed partial outputs
- old run remnants
- rejected output
- diagnostic notes

Safety:
- local-only
- do not commit

## Private config

Private config must not live in committed app config.

Use local-only zones for private config:

- `private/`
- `.local-private/`
- ignored runtime config files

## Operator sentence

The app may be public-safe.

The run output is guilty until reviewed.
