---
title: Traces — local-only session/debug artifacts
type: note
---

# Traces

This directory holds **local-only** session traces: work-in-progress drafts, debug
artifacts, raw scan dumps, intermediate reasoning logs, and feedback notes captured
while a session runs.

## Gitignored by default

Trace contents are **gitignored** — they are scratch artifacts, often contain
unredacted fetched data (emails, chat messages), and have no business in version
control. Only this `README.md` and a `.gitkeep` are tracked, so the directory exists
on a fresh clone while its contents stay local.

If you want a trace preserved, deliberately copy the sanitized parts into the proper
home (a project context file, a knowledge-base entry, an archive file) — don't commit
the raw trace.

```
ops/_traces/
  README.md     <- tracked
  .gitkeep      <- tracked
  *             <- everything else: local-only, gitignored
```
