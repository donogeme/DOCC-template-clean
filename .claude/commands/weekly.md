---
title: "/weekly - Weekly Review & Planning"
type: note
---

# /weekly - Weekly Review & Planning

Weekly review: clean the system, check OKR progress, set next-week priorities.

$ARGUMENTS optionally specifies focus or audience (e.g., `/weekly boss` generates a [YOUR BOSS] update).

## Execution Order & Concurrency (no coverage dropped)

Mirror the `/gm` + `/followup` concurrency pattern:

- **Kick off the email ingest (step 4a0) in the background first** — it must not block anything.
- **One parallel batch:** the state-file reads (step 1), the week scans (step 2), and the reconciliation scans (steps 4a-g) are mutually independent — fire them together, never sequentially. Active-project context files can also be read in this batch.
- **Scope step 3 with the scan results:** rows whose sources already lit up in the 7d scans are confirmed-live — record the activity, skip the re-read. Rows source-verified by a same-week `/followup` carry forward. Only true silence candidates get the full multi-source read.
- **Fan out step 3 verification across 2-4 parallel READ-ONLY subagents** when candidates exceed ~15 rows (batches in file order; agents return classification + evidence + recommended update; they never edit files). The main session applies all edits serially.
- `/kb-lint` and the Deferred/contacts hygiene reviews (step 5) are independent of the channel scans and can run while scan results come back.
- **Coverage caveat:** scoping skips redundant reads only. A no-hit row gets its full read regardless of age.

## Steps

1. **Read state:** `ops/_index.md`, `ops/_tasks.md`, `ops/_awaiting.md`, `ops/_goals.yaml`, `ops/_contacts.md`. Then each active project's `{project-name}.context.md`. *(Batched in parallel with steps 2 + 4a-g.)*

2. **Scan the week across all channels:** Gmail key threads (7d), Google Chat active spaces (7d), Slack Workspace 1 + Workspace 2 (7d), Notion Signals (7d), Notion Transcripts (7d — flag any unprocessed). *(Same parallel batch.)*

3. **Loop resolution via linked sources (MANDATORY first).** For every awaiting item and every Critical/High task *(candidates only — confirmed-live rows per Execution Order are recorded from the scan)*, open every linked source in the Source field. A loop may span multiple sources (Gmail thread + Chat space + Notion meeting + Slack thread). Read the latest activity in each — re-list the thread/space for its NEWEST messages, never just the message ID stored in the row, and check delegate sends ([YOUR DIRECT REPORTS]), not just [YOUR NAME]'s. If ANY source shows resolution, mark CLOSED. If nudged, update Last Nudge. Only fall back to keyword search when all sources are inconclusive.

   Tools by source type:
   - Gmail thread: `mcp__google__gmail_get_message`
   - Google Chat: `chat_list_messages` on the space
   - Slack: `slack_thread_replies` (Workspace 1 or Workspace 2)
   - Notion: query Signals/Transcripts DB for the meeting/signal

4. **Activity reconciliation across all channels (work done outside DOCC):**

   a0. **Verbatim email archive (recall layer) — background, window-matched.** Ingest any not-yet-captured mail into the gbrain recall layer:
   ```
   python tools/ingest_emails.py --after <YYYY/MM/DD = 7 days before today>
   ```
   Run with `run_in_background` — it only feeds the "Written (new)" count and must not block the scans. The `--after` date matches the 7d review window; dedup by message_id makes a wider window harmless, so widen only for a known gap (post-OOO, missed days). Writes one verbatim file per thread to `raw/emails/`, skipping already-ingested messages. Independent of the summary-row capture in step 4h. Report "Written (new)" in the review. See [[docc-system/gbrain-email-ingestion]].

   a. **Gmail outbound:** `from:[YOUR EMAIL] newer_than:7d`. New asks, decisions, threads with untracked people, vendor relationships.

   b. **Gmail inbound:** `to:[YOUR EMAIL] newer_than:7d`. Responses [YOUR NAME] handled directly, new asks, threads worth promoting.

   c. **Google Chat:** For each space in `ops/_google-chat-spaces.md`, scan recent messages. Filter by [YOUR NAME]'s user ID `[YOUR GOOGLE USER ID]` for outbound; scan for asks/mentions for inbound.

   d. **Slack Workspace 1:** `[SLACK_WORKSPACE_1_BOT_ID]` for mentions; scan active channels for [YOUR NAME] outbound.

   e. **Slack Workspace 2:** `[SLACK_WORKSPACE_2_BOT_ID]` for mentions; scan active channels for [YOUR NAME] outbound.

   f. **Notion Signals:** Recent signals (7d). Decisions, action items, contacts.

   g. **Notion Transcripts:** Recent meetings (7d). Capture meeting-resolved loops, project-relevant discussions, new people.

   h. For each untracked item across all channels, classify and persist:
   - New ask → `_awaiting.md`
   - Closed loop → Resolved in `_awaiting.md`
   - New commitment → `_tasks.md`
   - New person → `_contacts.md`
   - Decision/knowledge → `ops/_kb/_inbox.md` (or scoped `_kb/{scope}/{topic}.md`) or project context
   - Pure FYI → skip

5. **Task hygiene (BEFORE producing the review):**
   - Move completed items to Recently Completed
   - Critical/High overdue 5+ business days: flag for decision (demote/complete/escalate)
   - Anything overdue 10+ business days: move to Deferred with reason
   - Critical target is 8 (NOT a hard cap). If more than 8, surface a trim suggestion (list Critical items, recommend which to demote/complete/defer) — [YOUR NAME] decides. Never auto-demote or block tasks to force the count down.
   - Move Recently Completed older than 2 weeks to `ops/_archive/tasks-archive.md` (see `ops.md` → Archive Routing)
   - Move struck/closed rows out of all hot sections to `ops/_archive/` — hot files keep only open items
   - Flag contacts not referenced in 60+ days; archive confirmed-inactive ones to `ops/_archive/contacts-history.md`
   - Check Deferred: surface items whose Revisit-When condition is met

6. **Produce the review:**

```
## Weekly Review - Week of [Date Range]

### OKR Check (Q[X] closes in [N] days)
| Objective | Status | Movement | On Track? |
|---|---|---|---|
| OBJ-1 | ... | ... | ... |
| OBJ-2 | ... | ... | ... |
...

### What Got Done
- ...

### What Didn't Get Done (and why)
- [Honest reason: deprioritized / blocked / no capacity / forgot]

### Stale Items Requiring Decision
| Item | Days Open | Recommendation |
|---|---|---|
| ... | N | Demote / Nudge / Escalate / Drop |

### Deferred Items to Revisit
- ...

### Active Project Count: [N] (target ≤8)
- [If >8, recommend which to park]

### Awaiting: [N] active, [N] stale (5+ days)

### Work Done Outside DOCC
- New awaiting added: ...
- Loops closed: ...
- New contacts: ...
- Decisions/knowledge captured: ...
- Untracked threads flagged: ...

### Systemic Issues
- [Patterns, process gaps, recurring friction]

### Next Week: Top 5 Priorities
1. [Priority] — [why this week] — [OKR connection]
...

### What I'm NOT Doing Next Week
- [Items deliberately parked]
```

7. **Update files:** Apply task hygiene to `_tasks.md`. Update `_goals.yaml` progress fields. Add `_index.md` processing log entry. Persist Gmail reconciliation. Reactivate eligible Deferred items.

8. **Publish shared team context (Drive).** After the project context files are current (step 7), refresh the read-only team folder so teammates see the latest state:
   ```
   node tools/sync-shared-context.cjs
   ```
   Idempotent — updates the existing Google Docs IN PLACE (stable IDs/links the team has bookmarked), creates only what's missing. Applies publish-time redactions and a denylist guard. **If it reports `failed > 0`, a banned token (comp/pay, a personal number, a named account-weakness) survived redaction in a source file — that doc is NOT published; investigate and fix the REDACTIONS map before relying on the folder.** To add/remove shared docs or KB scopes, edit the `PROJECTS` / `MANUAL` / `REFERENCE` arrays in the script; any new sensitive content goes in `REDACTIONS` + `DENYLIST`. Folder "[YOUR ORG UNIT] Team - Project Context (read-only)" (`[DRIVE_SHARED_FOLDER_ID]`), shared read-only with [YOUR DIRECT REPORTS]. Background: `ops/_changelog.md` 2026-06-16.

9. **If audience specified:** Spawn `ops--briefer` for audience-appropriate update. Present draft for review.

10. **Close with:** "Anything to adjust? Deferred items to reactivate? Want me to draft nudges?"

## Rules

- Read every linked source before declaring stale. Source field is source of truth. A task may span multiple sources. (Scan-hit scoping skips redundant reads only — never coverage.)
- Verification subagents are READ-ONLY; all hot-file edits happen serially in the main session.
- Cover all 4 channel families: Gmail (in + out), Google Chat, Slack (Workspace 1 + Workspace 2), Notion (Signals + Transcripts).
- Weekly is the ONLY time items move to Deferred. Capture freely during the week, curate weekly.
- OKR check is mandatory and comes first. Name objectives that didn't move.
- "What I'm NOT Doing" is as important as "What I'm Doing."
- A task pending 2+ weeks without movement is a systemic issue, not just a task issue.
- 5-minute scan target. Keep it digestible.
- This is when `_goals.yaml` progress fields get updated.
