# YTM v1.2 Implementation Checklist

## Purpose

This checklist defines the remaining steps from the current v0.2 skeleton to a running YTM v1.2.

## Current completed foundation

- [x] v0.2 clean repo initialized
- [x] stem-cell structure created
- [x] safety audit added
- [x] donor archive mapped
- [x] YTM v1.1 working-state blueprint created
- [x] YTM v1.2 target definition created
- [x] physical/context module map created
- [x] local stack map created
- [x] rebuild workflow map created
- [x] YTM import candidates listed
- [x] YTM donor target files listed
- [x] YTM code inspection decision created
- [x] YTM module skeleton created
- [x] local runtime boundary created
- [x] runtime paths template created
- [x] local run folder creator created
- [x] local run lister created
- [x] status dashboard created

## Phase 1 — controlled donor inspection

- [ ] inspect old YTM app.py in detail
- [ ] inspect old handoff.py in detail
- [ ] inspect old start command
- [ ] identify reusable functions
- [ ] identify unsafe/private assumptions
- [ ] decide copy / rewrite / reject per component

## Phase 2 — minimal running YTM app

- [ ] create v0.2 app entry point
- [ ] create minimal Streamlit shell
- [ ] show status dashboard in UI or link to CLI dashboard
- [ ] show configured runtime output root
- [ ] show local run list
- [ ] create new run from UI or CLI
- [ ] no transcript mining yet

## Phase 3 — source handling

- [ ] define source folder policy
- [ ] add source import placeholder
- [ ] add transcript/VTT/TXT handling only under local output
- [ ] no source-derived output in committed paths

## Phase 4 — local model / radar-card layer

- [ ] define model boundary
- [ ] add generic prompt template
- [ ] keep private prompt/context local-only
- [ ] generate radar-card into derived local output
- [ ] run small sample only

## Phase 5 — operator output

- [ ] create operator brief skeleton
- [ ] create validation queue skeleton
- [ ] create handoff folder writer
- [ ] distinguish full handoff from operator brief

## Phase 6 — batch/resume

- [ ] add skip-existing logic
- [ ] add resume logic
- [ ] add run status summary
- [ ] add failure notes

## Phase 7 — v1.2 small acceptance test

- [ ] create one test run
- [ ] process one small source
- [ ] generate local derived output
- [ ] generate operator brief
- [ ] run safety audit
- [ ] confirm git status remains clean
- [ ] tag local state as YTM v1.2 candidate

## Definition of running v1.2

YTM v1.2 is running when:

- the app starts
- it creates local-only run folders
- it can process a small source
- it writes outputs only under ignored output/
- it can show run status
- it can generate at least a minimal operator brief
- safety audit passes
- git status stays clean after a run

## Current next step

Inspect old app.py and design the minimal v0.2 Streamlit shell.
