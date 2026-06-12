# Local Stack Map

## Purpose

This file describes the local tools and surfaces around P3FE v0.2.

It separates the repository from the operator environment.

## Core distinction

The repository is the project body.

The local stack is the workshop around the body.

Do not confuse them.

## Operator surfaces

### Finder

Role:
- physical folder visibility
- confirms what exists as real folders/files

Use:
- inspect v0.2 structure
- inspect archive/donor location
- check private/output/quarantine zones

Not for:
- editing code
- commit control

### VS Code

Role:
- file-tree dashboard
- markdown reading and editing
- code inspection
- lightweight project navigation

Use:
- read 00_STEM_CELL files
- inspect source maps and blueprints
- inspect future app code
- see physical/context modules

Not for:
- blind automated modification
- raw private content review unless local-only and intentional

### GitHub Desktop

Role:
- visual Git status and commit/diff viewer

Use:
- inspect changed files
- understand what is staged/committed
- visual confidence layer

Not for:
- pushing without safety audit
- treating GitHub as a secret vault

### Terminal

Role:
- controlled command execution

Use:
- short Sanyi-provided commands
- git status/log
- running safety audit
- running local scripts

Not for:
- long heredoc blocks
- blind file dumping
- uncontrolled mass operations

### ChatGPT / Sanyi

Role:
- command generation
- interpretation
- routing
- safety reasoning
- rebuild co-pilot

Use:
- explain terminal output
- provide next commands
- keep workflow moving
- detect safety gates

Not for:
- being the only source of truth
- replacing committed files
- storing private archive data

## Local AI layer

### Ollama

Role:
- local model runner

Current state:
- used in v0.1 archive context
- not yet rebuilt into v0.2

### Qwen / Qwinni

Role:
- stronger local structured extraction model candidate

Known use:
- radar-card generation
- quality-pass style checks

Current state:
- local stack component, not repo content

### Llama / Lámácska

Role:
- smaller local model / experiment layer

Known limitation:
- weak for strict schema-following

Current state:
- local stack component, not repo content

## UI / dashboard direction

No custom dashboard app is built yet.

Current dashboard stack:

- Finder = physical structure
- VS Code = file tree and markdown dashboard
- GitHub Desktop = Git/diff visibility
- Terminal = controlled execution
- Sanyi = interpretation and next-step logic

## Safety rule

Local tools may see private context.

Git commits must not contain private context.

## Next rebuild implication

Before importing code, every module must declare:

- where it lives
- what local tools it needs
- what output it creates
- what must stay private/local-only
