# Physical and Context Module Map

## Purpose

This file separates two different things:

1. physical modules that exist as folders/files
2. context modules that exist as plans, concepts, rules, or intended system layers

This distinction is important because P3FE should not pretend that a planned layer already exists in code.

## Physical workspace map

Current physical v0.2 workspace:

- `00_STEM_CELL/`
  - rebuild DNA
  - source maps
  - blueprints
  - safety rules
  - rebuild targets

- `apps/`
  - future application code
  - currently empty / not yet imported

- `docs/`
  - public-safe architecture and decisions

- `scripts/`
  - public-safe helper scripts
  - safety scripts

- `private/`
  - local-only private context
  - ignored by git

- `output/`
  - local-only generated output
  - ignored by git

- `quarantine/`
  - local-only unsafe or unknown material
  - ignored by git

- `donor/`
  - local-only donor inventory/import staging
  - ignored by git

## Current committed system modules

These already exist in v0.2 as committed structure or files:

- stem-cell rebuild structure
- public safety audit
- donor map
- YTM v1.1 working-state blueprint
- YTM v1.2 target definition

## Physical modules not yet imported

These do not yet exist in v0.2 as active code:

- YouTube Mining app
- Streamlit UI
- handoff generator
- transcript downloader
- radar-card generator
- batch/resume processor
- operator brief generator
- config loader
- local model runner integration

They may exist in the v0.1 archive, but they are not active v0.2 modules yet.

## Context modules

These exist as system ideas, rules, or plans.

They must not be treated as implemented code until rebuilt.

### Safety Gate

Role:
- prevent private/raw/sensitive material from crossing into commits or push

Current state:
- initial script exists
- must be improved later

### Stem Cell

Role:
- high-level rebuild DNA
- stores public-safe source maps and blueprints
- does not store raw private material

Current state:
- physical folder exists
- initial files exist

### Donor Archive

Role:
- old v0.1 system as reference
- source of inspectable organs
- not active workspace

Current state:
- separate physical folder outside v0.2
- local inventory exists under ignored donor folder

### YTM Adapter

Role:
- YouTube source adapter
- first source-mining implementation

Current state:
- blueprint exists
- code not yet imported

### Operator Dashboard

Role:
- make status visible to non-developer operator

Current state:
- not implemented as app
- current temporary dashboard is Finder / VS Code / Terminal / Sanyi workflow

### Local AI Stack

Role:
- local models and runtime environment

Current state:
- not rebuilt
- to be documented separately

### Signal Matrix

Role:
- classify mined source signals

Current state:
- concept exists
- clean config not yet implemented

### Market / Reality Context

Role:
- separate generic signal classification from private business-use context

Current state:
- concept exists
- must remain local-only if business-specific

### Community Signal Layer

Role:
- optional later layer for comments/community reactions

Current state:
- planned only
- not implemented

## Rule

A context module becomes a physical module only when it has:

1. a folder or file location
2. a clear role
3. safety classification
4. rebuild/import decision
5. committed implementation or committed blueprint

## Operator sentence

If I cannot point to a folder or file, it is not a physical module yet.

It is a context module or plan.
