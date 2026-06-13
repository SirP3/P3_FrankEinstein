# Codex Workflow for P3FE v0.2

Codex is a bounded repo-native implementation assistant. It is not the project owner, not the architect, and not the source of truth.

Codex may:
- implement small scoped features
- create small scripts
- wire existing UI actions
- run py_compile checks
- run public safety audit checks
- report git status and git diff
- suggest commit messages

Codex must not:
- redesign the architecture
- touch the v0.1 archive unless explicitly asked
- create or connect a GitHub remote
- push changes
- commit automatically
- commit runtime, source, or private data
- implement real AI, model, or transcript mining unless explicitly scoped
- skip the public safety audit before recommending a commit

## Required Task Packet

Each Codex task should include:
- repo path
- current stable commit or known state
- exact task
- allowed files or module area
- forbidden actions
- required checks
- no automatic commit rule
- recommended commit message

## Validation Workflow

Sanyi/GPT or a human validates Codex output before commit.

Required validation:
- inspect changed files
- run py_compile where relevant
- run `python3 scripts/safety/public_safety_audit.py`
- inspect `git status --short`
- inspect `git diff`
- decide whether to commit

## Example Task Packet

Repo: `/Users/pomazipeter/P3_FrankEinstein v0.2`

Known state: latest stable commit and current pipeline summary.

Task: add one small placeholder or UI readback step.

Allowed area: `apps/youtube_mining/`

Forbidden: no archive edits, no GitHub remote, no push, no automatic commit, no runtime/source/private data in committed paths.

Checks: py_compile for changed Python files, public safety audit, git status, git diff.

Recommended commit message: short imperative summary.
