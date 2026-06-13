# YTM Radar Card Prompt v0.2

## Purpose

This prompt is for local-only analysis of a model packet generated from a public YouTube transcript source.

The output must produce clean structured observations, not copied content.

## Policy

Public Source, Private Processing, Clean Output

Rules:
- Public/free source may be processed privately.
- Source transcript text must not be reproduced.
- Do not output long quotes.
- Do not write a rewritten third-party article, video, or script.
- Do not produce plagiarism-style output.
- Do not extract personal data beyond what is necessary for source identification.
- Output is structured observation, not source replacement.
- Local model output is not source of truth.
- Uncertainty must be marked.
- Clean output only.

## Input Expectation

The model receives a local-only model packet that may contain transcript text.

The packet is runtime-only and must not be committed.

## Output Format

Return exactly one Markdown radar card using this schema.

# YTM Radar Card

source_id:
source_title:
source_type:
primary_scope:
action_class:
signal_strength:
noise_risk:
confidence:
transcript_reopen:
finance_trading_quarantine:
source_keywords:
observed_patterns:
opportunities:
risks:
workflow_insights:
clean_summary:
validation_notes:
source_attribution_note:

## Controlled Vocabularies

primary_scope:
- ai_tool
- workflow
- business
- education
- finance_trading
- generic_noise
- unknown

action_class:
- keep
- watch
- quarantine
- discard
- reopen_later

signal_strength:
- low
- medium
- high

noise_risk:
- low
- medium
- high

confidence:
- low
- medium
- high

transcript_reopen:
- yes
- no
- maybe

finance_trading_quarantine:
- yes
- no
- not_applicable

## Field Rules

- All required fields must be present.
- Controlled vocabulary fields must use only the allowed values.
- `clean_summary` must be short and must not contain copied transcript text.
- `observed_patterns`, `opportunities`, `risks`, and `workflow_insights` must be abstracted.
- `source_keywords` may contain short keywords only, not phrases copied from the transcript.
- `source_attribution_note` should preserve internal attribution, not public citation text.
- If finance/trading content appears, set `primary_scope` to `finance_trading` and `finance_trading_quarantine` to `yes` unless clearly irrelevant.
- If uncertain, lower `confidence` and add `validation_notes`.

## Validation Checklist

- All required fields present.
- Controlled vocabulary values valid.
- No long quote.
- No transcript reproduction.
- No rewritten third-party content.
- No unprocessed personal data.
- `clean_summary` is own wording.
- Quarantine flag checked.
- Uncertainty marked.
