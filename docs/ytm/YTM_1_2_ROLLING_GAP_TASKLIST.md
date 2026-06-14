# YTM 1.2 Rolling Gap Tasklist

## Current Minimum Rolling Flow

The current YTM v1.2 baseline can already complete this minimum rolling flow on a small source:

```text
source
-> transcript download
-> VTT to TXT conversion
-> model packet build
-> local radar-card generation
-> radar-card validation
-> radar-card brief
-> YTM run summary
-> UI evidence detection
```

This is enough for a small end-to-end operator run, but it is not yet the full old YTM v1.1 value surface.

## Still Missing Or Partial

- Channel / full-channel mode
- First/latest N source scope beyond the current bounded small-selection controls
- Browser-session handling for harder YouTube transcript access cases
- Content-hours calculation
- Rich transcript success / fail / unavailable detail in operator evidence
- Radar keyword index generation
- Quality-pass generation
- Full handoff package generation
- Comment extraction as a later, separate layer

## Notes

- These items should be added only if they fit the existing Public Source, Private Processing, Clean Output boundary.
- Missing artifacts must not be faked in the UI or runtime summaries.
- The next steps should extend the current rolling flow, not restart the version line or redesign the product story again.
