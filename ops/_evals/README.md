---
title: Evals — command-output test harness (placeholder)
type: note
---

# Evals

**Status: optional / placeholder.** This subsystem is reserved and currently empty.

## Intended purpose

An eval/test harness for command outputs. As the system's slash commands (briefings,
follow-up scans, status reports, drafts) mature, you may want regression coverage on
what they produce — not just that they run, but that they produce the *right* output.

The intended shape:

- **Fixtures** — frozen inputs (a captured channel scan, a set of tracking files) that a
  command runs against deterministically.
- **Expectations** — assertions on the output: did the briefing surface the known-overdue
  loop? did the follow-up scan match the archived reply to its open loop? did a draft
  avoid fabricated facts and keep the recipient list intact?
- **A runner** — executes each command against its fixture and reports pass/fail, so a
  prompt/spec change that breaks a behavior fails loudly instead of silently regressing.

## Why it's a placeholder

Evals earn their keep once you have commands stable enough that "did this change break a
behavior?" becomes a real question. Until then this directory just holds the intent. Add
real evals when a command's output has burned you and you want a guardrail.

```
ops/_evals/
  README.md     <- this file
  .gitkeep
  <command>/    <- (future) fixtures + expectations per command
```
