# YouTube Mining Adapter

## Purpose

This is the clean v0.2 YouTube Mining adapter skeleton.

It is rebuilt from the v0.1 donor knowledge, not copied blindly.

## Current state

Skeleton only.

No old donor code has been imported yet.

## Safety boundary

This app must not store raw mining output inside committed paths.

Local-only runtime material must go outside Git-tracked code, under ignored output/private zones.

## Intended responsibilities

Future responsibilities:

- local YouTube source preparation
- transcript/source handling
- structured radar-card generation
- quality-pass support
- operator brief generation
- safe handoff generation
- run status visibility

## Not included yet

- old Streamlit app code
- old handoff generator code
- transcript downloader
- model calls
- output generation
- private config
- raw transcripts
