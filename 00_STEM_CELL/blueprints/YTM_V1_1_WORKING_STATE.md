# YTM v1.1 Working State Blueprint

## Purpose

This file describes the known working state of the old YouTube Mining module.

It is a rebuild blueprint, not an import of old source material.

## Known status

YTM v1.1 existed as a local YouTube mining workflow.

It had enough working parts to prove that the system can:

- collect YouTube subtitle/transcript material
- convert source text into local mining input
- generate structured radar cards with a local LLM
- run a quality-pass layer
- generate handoff-style outputs
- operate through a Streamlit-based local UI

## Known donor organs

The v0.1 donor archive contains these reusable organs:

- YouTube Mining module
- local Streamlit UI application
- radar-card generation logic
- handoff generation logic
- YTM runbook
- YTM specs
- YTM audit notes
- local stack notes

## Known local model roles

Known model role split from v0.1:

- Qwen / Qwinni: stronger structured extraction and radar-card generation
- Llama / Lámácska: useful as experiment, but weak for strict schema-following

Exact local model setup must be documented separately in LOCAL_STACK.

## Known output classes

YTM v1.1 produced or managed these output classes:

- source transcript material
- converted text material
- radar cards
- quality-pass notes
- handoff packs
- run-level notes

These outputs are local-only unless separately anonymized.

## Known problem areas

YTM v1.1 was working, but not operator-clean.

Known issues:

- folder layout was not clear enough
- source, derived, and handoff material were mixed too much
- handoff names were inconsistent
- large channel processing was risky
- operator brief was missing
- public/private isolation was not strong enough
- prompts and config logic were too embedded in code
- GitHub safety boundary was not clear enough

## Rebuild instruction

Do not copy the old YTM body blindly.

Rebuild YTM v1.2 from this blueprint:

1. create clean module skeleton
2. separate source / derived / handoff / local-only output
3. rebuild safety boundaries first
4. import only audited code
5. test with small sample before large channel mining

## Next related file

YTM v1.2 target definition should specify what the rebuilt module must become.
