---
title: KB Inbox
type: note
---

# KB Inbox

> **Auto-save landing zone.** During normal sessions, when the console captures domain knowledge that doesn't yet have a home, it lands here as a dated entry. `/kb-lint --triage-inbox` triages entries to scoped files during `/weekly`.
>
> **Why this exists:** with many candidate KB files, asking the model to classify-on-the-fly during normal sessions fragments the same fact across multiple files session-to-session. Inbox-first routing eliminates that drift — classification becomes a deliberate weekly act with full manifest visibility, not a guess in the middle of other work.

## How to Use

**During normal sessions (auto-save):** when domain knowledge surfaces that doesn't clearly belong to an existing topic file, append a new entry below using the format:

```
## YYYY-MM-DD HH:MM TZ — [short title]

**Context:** [where this came from — email, chat, meeting, decision]
**Content:** [the fact, decision, or knowledge to capture]
**Source:** [thread ID / link / "session"]
**Tentative scope(s):** [best-guess scope(s); for triage]
```

**During `/weekly` triage:** `/kb-lint` reads each entry, suggests the target file(s), and asks you to confirm. Confirmed entries are merged into target file(s) and removed from inbox.

**Entries pending triage (newest first):**

<!-- New entries go below this line. Move triaged entries OUT of this file into the appropriate _kb/{scope}/{id}.md file. -->

_(empty — no entries pending triage)_
