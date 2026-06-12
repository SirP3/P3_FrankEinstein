# YTM Code Inspection Decision

## Purpose

This file records the first decision after inspecting the v0.1 YTM donor code.

It is a public-safe decision file.

It does not copy donor code.

## Inspected donor organs

The local-only inspection found the following donor organs:

- old YTM Streamlit UI app
- old handoff generator
- old start command

## Main finding

The old YTM code is useful, but it is not safe to copy blindly.

It mixes several concerns that v0.2 must separate:

- UI workflow
- transcript/source handling
- output generation
- handoff generation
- local model routing
- local machine assumptions
- cookie/browser-related workflow
- radar-card and handoff output paths

## Decision

Do not clone the old YTM app as-is.

Use it as a donor reference and rebuild the v0.2 YTM module consciously.

## Import strategy

### Streamlit UI app

Decision:
- rebuild from donor reference
- do not copy blindly

Reason:
- it contains the old working workflow shape
- it also contains mixed output/model/source assumptions

v0.2 target:
- clean UI shell first
- separate source / derived / handoff / output paths
- no raw output in committed paths

### Handoff generator

Decision:
- inspect and selectively extract logic later

Reason:
- useful run-level output concepts exist
- output boundaries must be rewritten

v0.2 target:
- operator brief first
- full handoff later
- no source-derived private content in committed files

### Start command

Decision:
- rewrite as new local convenience script later

Reason:
- old command is useful as launch reference
- v0.2 paths and safety rules are different

v0.2 target:
- simple local launcher
- no machine-specific private assumptions

## Required separation before code import

Before importing or rewriting code, define:

1. module folder location
2. local-only output root
3. source folder policy
4. derived output policy
5. handoff policy
6. model-call boundary
7. safety audit behavior
8. operator-visible status

## Next action

Create the v0.2 YTM module skeleton without importing old code.

The skeleton should include:

- app folder
- source/output boundary notes
- placeholder README
- no transcript files
- no donor code copied yet

## Operator sentence

The old YTM app proves the workflow.

The new YTM app must prove control.
