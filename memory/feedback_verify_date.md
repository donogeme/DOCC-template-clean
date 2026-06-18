---
name: feedback_verify_date
description: Verify the current date at session start; never trust stale date context.
metadata:
  type: feedback
---

# Verify the current date at session start

Never trust stale date context carried in from a prompt, a cached file, or a previous
session. Establish the actual current date before doing anything date-sensitive.

**Why:** Many behaviors depend on "now" — what's overdue, what's stale, how many days
until a deadline, whether a loop has gone quiet. A wrong date silently corrupts all of
that: a flagged-overdue item may not be overdue, a "stale" loop may be fresh.

**How to apply:** At session start, confirm today's date from a reliable signal. When
computing anything relative ("3 days overdue," "closes in X days"), anchor it to the
verified current date, not to a date string you found in a file.
