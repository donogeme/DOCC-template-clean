---
title: /sitrep - Status Report Generation
type: note
---

# /sitrep - Status Report Generation

Generate a status report. `/sitrep` or `/sitrep [audience]`.

$ARGUMENTS specifies the audience. If missing, ask.

## Audiences

- **boss** — Upstream report for [YOUR BOSS]
- **team** — Downstream update for [YOUR DIRECT REPORTS]
- **[project-name]** — Project-specific briefing
- **all** — Full sitrep across everything

## Steps

1. **Read state:** `ops/_index.md`, `ops/_tasks.md`, `ops/_goals.yaml`, `ops/_awaiting.md`, relevant project context files.

2. **Verify before reporting.** For every blocker, open loop, and "in progress" item that will appear, open every linked source on it (Gmail thread, Chat space, Slack thread, Notion signal — a loop may span multiple). Read the latest message in each. Update tracking if actually resolved before drafting. False-stale claims to leadership are worse than omissions.

3. **Spawn `ops--briefer`** with audience context and verified state.

4. **Present the draft for review.**

5. **If email:** Draft with To, CC, Subject, Body. Wait for explicit approval. Use `ops/_kb/people-and-tone/voice.md`.

## Report Types

**Boss (upstream):** [YOUR ORG UNIT] goal progress, blockers needing their help, decisions made, headcount impact. 5-10 bullets max, headlines first.

**Team (downstream):** This week's priorities per person, decisions affecting their work, context they need. Task-oriented and specific.

**Project:** Current state, recent decisions, open items, next steps, blockers. Comprehensive with sources.

**Full sitrep:** Everything. Structured overview with drill-down sections.

## Rules

- Frame blockers with proposed solutions
- Cite sources for any claims
- Use [YOUR NAME]'s voice
- NEVER send without approval
- Verify every blocker/awaiting item via reads of all linked sources before including
