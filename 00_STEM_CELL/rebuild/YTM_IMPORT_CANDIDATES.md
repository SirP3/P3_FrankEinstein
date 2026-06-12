# YTM Import Candidates

## Purpose

This file lists candidate donor organs from the v0.1 archive that may be inspected for rebuilding YTM v1.2.

This is not an import.

No old code or raw output is copied by this file.

## Donor archive

Source:

`P3_FrankEinstein v0.1_archive`

Role:

- donor
- archive
- previous working state
- not active workspace

## Candidate donor organs

### 1. YTM Streamlit UI app

Candidate role:
- local operator UI
- old working launch surface
- possible app skeleton donor

Safety class:
- code candidate
- must be audited before copying

Expected old location:
- YouTube Mining UI application under the old youtube-mining module

Import decision:
- inspect first
- copy only if public-safe
- remove embedded private paths or prompts if found

### 2. Handoff generation logic

Candidate role:
- create run-level handoff outputs
- generate indexes or summary files
- help rebuild operator brief later

Safety class:
- code candidate with output-risk

Import decision:
- inspect first
- output paths and private-content assumptions must be rewritten

### 3. Transcript / subtitle handling logic

Candidate role:
- collect or convert YouTube subtitle material
- support source preparation

Safety class:
- code candidate with raw-output boundary

Import decision:
- inspect first
- source/output folder separation required before use

### 4. Radar-card generation logic

Candidate role:
- convert transcript text into structured radar-card
- local LLM prompt/response handling

Safety class:
- code + prompt candidate

Import decision:
- inspect first
- prompt must be separated from private business context
- schema/config should move toward separate files

### 5. Quality-pass logic

Candidate role:
- second-pass check over radar-card output

Safety class:
- code + prompt candidate

Import decision:
- inspect first
- must be described as quality-pass, not true external validation

### 6. YTM runbook / specs / audit notes

Candidate role:
- human-readable donor knowledge
- previous decisions and known issues

Safety class:
- document candidate

Import decision:
- do not copy blindly
- extract into public-safe blueprints or local-only notes

### 7. Local stack notes

Candidate role:
- reconstruct local model/runtime assumptions

Safety class:
- local environment candidate

Import decision:
- extract generic parts only
- machine-specific or private details stay local-only

## Explicitly blocked from import

Do not import directly:

- transcript folders
- VTT files
- TXT transcript outputs
- radar-card outputs
- handoff packs
- quality-pass outputs
- private config
- local backups
- archive dumps
- business-specific notes
- personal/company/client identifiers

## Required import process

Each candidate must pass this sequence:

1. identify source file
2. inspect content
3. classify safety
4. decide import / rewrite / reject
5. copy into v0.2 only if safe
6. run safety audit
7. commit separately

## First likely import target

The first code candidate should be the old YTM Streamlit UI app.

Reason:
- it is likely the main entry point
- it shows current workflow shape
- it helps rebuild the operator-visible surface

## Operator sentence

Candidate does not mean import.

Import does not mean trust.

Trust comes only after audit and local test.
