# YTM Donor Target Files

## Purpose

This file lists the first public-safe donor target files to inspect from the v0.1 archive.

It is not an import.

It is a controlled target list for later inspection and selective rebuild.

## Primary code targets

### Streamlit UI app

Old donor role:
- local YouTube Mining operator UI
- main workflow surface
- likely first rebuild reference

Target classification:
- inspect first
- code candidate
- do not copy blindly

Old donor path class:
- youtube-mining UI application entry file

### Handoff generator

Old donor role:
- handoff and index generation
- run-level output preparation

Target classification:
- inspect first
- code candidate with output-risk
- must rewrite local/output boundaries before reuse

Old donor path class:
- youtube-mining handoff logic file

### Start command

Old donor role:
- local launch helper
- Streamlit startup path

Target classification:
- inspect first
- local convenience script candidate
- must remove machine-specific assumptions if present

Old donor path class:
- youtube-mining start command

## Primary documentation targets

### YTM runbook

Old donor role:
- explains how the old YTM was used

Target classification:
- document candidate
- extract generic workflow only

### YTM signal matrix spec

Old donor role:
- describes old signal classification logic

Target classification:
- blueprint/config candidate
- extract generic schema only

### YTM v1.2 stabilization plan

Old donor role:
- records previous rebuild planning

Target classification:
- planning candidate
- extract public-safe target logic only

### YTM audit notes

Old donor role:
- previous test/audit knowledge

Target classification:
- document candidate
- summarize, do not copy blindly

## Local stack targets

### local-stack notes

Old donor role:
- runtime and UI development notes

Target classification:
- local environment candidate
- extract generic setup only

## Blocked from direct target list

Do not inspect first as import targets:

- transcript outputs
- radar-card outputs
- handoff packs
- backup dumps
- private config
- local-private material

## Next inspection order

1. Streamlit UI app
2. handoff generator
3. start command
4. YTM runbook
5. YTM signal matrix spec
6. v1.2 stabilization plan
7. audit notes
8. local-stack notes

## Operator sentence

The target list tells us where to look.

It does not give permission to copy.
