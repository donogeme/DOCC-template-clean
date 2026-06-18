---
title: /archive - Inbox Archive Sweep
type: note
---

# /archive - Inbox Archive Sweep

Scan inbox for archivable threads. Present grouped by confidence. Archive only what [YOUR NAME] approves.

$ARGUMENTS optional time window. Default: `newer_than:3d`.

## Steps

1. **Read:** `ops/_awaiting.md` (protect open loops), `ops/_tasks.md` (protect linked tasks), `ops/_contacts.md`, `ops/_index.md`.

2. **Scan inbox:** `in:inbox $ARGUMENTS`. Read sender, subject, snippet, TO/CC, date, threadId. Group by thread (one entry per thread).

3. **Classify each thread.**

   **Cross-reference by source ID, not subject.** Match inbox threadIds against the Gmail thread IDs in the Source fields of `_awaiting.md` and `_tasks.md`. A task's Source may list multiple IDs (Gmail thread + Chat + Slack + Notion); check the Gmail one for matches. Subjects collide and get re-purposed.

   **For ambiguous threads, read the latest message.** When a thread looks archivable but [YOUR NAME] was a primary recipient, open it with `mcp__google__gmail_get_message` and confirm the latest message has no unanswered ask.

   **SAFE TO ARCHIVE:**
   - Automated notifications (OTP codes, learning-platform alerts, system alerts, calendar auto-responses)
   - Newsletters, marketing, vendor promos
   - Threads where [YOUR NAME]'s reply is the latest message
   - Threads matching CLOSED items in `_awaiting.md` (by thread ID)
   - FYI-only CCs with no action signals
   - Read receipts, delivery confirmations, signature notifications
   - Threads >48h where [YOUR NAME] is CC'd and not directly asked

   **PROBABLY ARCHIVABLE (review):**
   - [YOUR NAME] CC'd, conversation continued without them
   - Informational updates from known contacts, no ask
   - [YOUR NAME] TO'd but ask was answered by someone else in the thread
   - 5+ days in inbox, no follow-up

   **DO NOT ARCHIVE:**
   - Thread ID matches ACTIVE `_awaiting.md` item
   - Thread ID matches active Critical/High `_tasks.md` task
   - Unanswered question to [YOUR NAME] ("can you", "please", "need your", "approve", "review", "decision", "by EOD", "ASAP")
   - Anything from [YOUR BOSS] or [YOUR DIRECT REPORTS] without [YOUR NAME]'s reply
   - [YOUR NAME] is the only TO and hasn't replied
   - Budget/legal/HR without resolution

4. **Present the report:**

```
## Archive Sweep - [Date/Time]

**Scanned [N] threads. [X] safe, [Y] probably, [Z] protected.**

### Safe to Archive ([X])
| # | Subject | From | Why Safe | Age |
|---|---|---|---|---|

### Probably Archivable ([Y]) — Review
| # | Subject | From | Why | Age |
|---|---|---|---|---|

### Protected ([Z])
- [Brief: "3 with open awaiting items, 2 unanswered from [YOUR BOSS]"]
```

5. **Approval:** "Archive all [X] safe? Review first?" Accept: "archive safe", "archive all", "archive safe + 2,4,5", "skip 3".

6. **Execute:** `gmail_archive_messages` with approved IDs. Report: "Archived [N]. [M] remain."

7. **If archived thread had a loop update:** "Heads up — [thread] had a response to [awaiting item]. Archived but loop still tracked in `_awaiting.md`."

## Rules

- NEVER auto-archive without presenting the list first.
- NEVER archive threads with unanswered asks to [YOUR NAME]. When in doubt, protect.
- Cross-reference by source ID, not subject. Source field may list multiple sources per item; check Gmail thread IDs for inbox matches.
- Read the latest message on ambiguous threads before classifying SAFE.
- Tier 1 senders ([YOUR BOSS], [YOUR DIRECT REPORTS]) are protected by default unless [YOUR NAME] replied.

## Notes

- Archive is hygiene, not action surfacing. For action items, run `/gm` or `/followup`.
- One thread = one archive decision.
- Pair: `/followup` first (handle action), `/archive` second (clean up).
