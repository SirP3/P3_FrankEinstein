# YTM v1.2 Target Definition

## Purpose

This file defines what YTM v1.2 should become during the clean rebuild.

It is not implementation code.

It is the target shape for rebuilding the YouTube Mining adapter.

## Core target

YTM v1.2 should become an operator-usable, safety-aware YouTube source adapter.

It should not be only a mining experiment.

## Main upgrade from v1.1

YTM v1.1 proved that local YouTube mining can work.

YTM v1.2 must make it safer, clearer, more restartable, and easier for a non-developer operator to understand.

## Required v1.2 layers

### 1. Clean folder hierarchy

Future YTM runs should separate:

- source material
- derived AI material
- handoff material
- local-only outputs
- archive/quarantine material

Target run shape:

- source/
- derived/
- handoffs/
- archive/
- run-info.md

### 2. Safety boundary

YTM must not mix public-safe code with private/raw outputs.

Local-only material includes:

- transcripts
- VTT/TXT files
- source-derived radar cards
- handoff packs
- private prompts
- business-specific context

### 3. Operator brief

The full handoff is not enough.

YTM v1.2 should produce or support an operator brief that shows:

- top signals
- use-now candidates
- validate candidates
- park/archive candidates
- noise/reject candidates
- risky or regulated topics
- next recommended action

### 4. Batch and resume logic

Large channels must not be processed blindly in one pass.

YTM v1.2 should support:

- skip-existing
- resume
- small batch processing
- run status visibility
- clear failure recovery

### 5. Config separation

Prompt/schema/routing logic should not live only inside code.

YTM v1.2 should move toward separate config files for:

- signal matrix
- market/context fit
- action classes
- quarantine rules
- output templates

Private business-specific config must remain local-only.

### 6. Local model role clarity

YTM v1.2 should document which local model does what.

Known direction:

- stronger local model for structured extraction
- weaker/local small model only for experiments or low-risk tasks
- quality pass is not external validation

### 7. Optional community-signal layer

YouTube comments may become an optional source layer later.

Rule:

- transcript = creator signal
- comments = community signal
- comments must not be mixed into transcript-derived signal by default
- comment mining is optional and later

## Explicitly not now

YTM v1.2 should not yet include:

- Reddit Radar
- GitHub Radar
- agent framework
- full custom dashboard app
- automatic mass processing
- public publishing workflow
- business-specific private strategy in committed files

## Safety-first rebuild order

1. module skeleton
2. safety/local-only boundaries
3. run folder structure
4. minimal launch path
5. import audited YTM code
6. small test run
7. operator brief
8. batch/resume support
9. config separation
10. optional comment/community layer

## Success condition

YTM v1.2 is successful when the operator can answer:

- where is the source material?
- where is the AI-derived material?
- what is safe to commit?
- what is local-only?
- what run is active?
- what should be done next?
- what should not be touched?

## Core sentence

YTM v1.2 is not more mining.

YTM v1.2 is controlled, restartable, operator-visible source mining.
