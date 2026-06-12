# YTM Output Policy

## Rule

Committed app code and local generated outputs must stay separate.

## Committed app zone

Allowed in committed app paths:

- source code
- generic config templates
- public-safe documentation
- tests without private data
- safety notes

## Local-only output zone

Must stay local-only:

- transcripts
- VTT/TXT files
- radar-card outputs
- quality-pass outputs
- handoff packs
- source-derived notes
- private prompts
- run logs containing source-specific details

## Future target run shape

Future local run outputs should use a separated structure:

- source/
- derived/
- handoffs/
- archive/
- run-info.md

## Operator sentence

If a file was produced from a real source, treat it as local-only unless explicitly anonymized.
