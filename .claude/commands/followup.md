---
title: "/followup - Loop Lifecycle & Context Reconciliation"
type: note
---

# /followup - Loop Lifecycle & Context Reconciliation

Scan all channels, verify loop state, surface what needs you now and what's stale. Default is a 24-hour scan (`/followup` = `/followup 1d`); pass a wider window for deeper reconciliation (`/followup 7d`, `/followup 14d`).

$ARGUMENTS optionally narrows scope:
- Time window: `/followup 3d`, `/followup 7d`, `/followup 14d` (default 1d / last 24 hours)
- Project: `/followup staffing`
- Person: `/followup [a direct report]`
- Combine: `/followup staffing 3d`

## Execution Order & Concurrency (no coverage dropped)

Run the command in this order — it reduces wall-clock without skipping any source:

1. **Kick off the email ingest in the background** (Pass 2 step 0) — it only feeds the header count and must not block the scans.
2. **Fire one parallel batch:** the 4 state-file reads (Pass 1 step 1) + ALL Pass 2 discovery scans (steps 3-9) are mutually independent — issue them together, never one at a time.

2b. **Shadow mode — deterministic channel pullers (extractors slices 1-2, TRIAL 2026-06-12).** In the same batch, ALSO run in the background:
   ```
   node tools/pullers/pull-all.mjs --window {window} | node tools/extract.mjs
   ```
   This pulls all six channels (Gmail, Chat, Slack ×2, Notion ×2) deterministically — pagination to exhaustion — and does NOT replace the MCP scans yet. Use its JSON output four ways: (1) **completeness check** — compare per-channel counts (`channels_in`) against what the MCP scans surfaced; the Chat count especially (the MCP search truncates at ~100 returned; the puller does not); report any messages the scan missed in the Gaps section (one line); (2) **triage cross-check** — `matched` rows are deterministic, high-confidence signals; the ACTION types (`ramp_approval_request`, `legal_intake_awaiting_response`, `ticketing_reminder_awaiting_reply`) must each appear in the triage — flag any divergence; (3) **skillify nudge** — if `nudge_candidates` is non-empty, render at most ONE line: "shape X from {sender} seen on N days — candidate for an extractor (/skillify)"; (4) **per-channel failures** — `pull_errors` entries get a one-line note ("chat puller errored — model scan only for Chat"); a failing channel NEVER blocks anything (per-channel fallback is built into pull-all). See [ops/_extractors/README.md](../../ops/_extractors/README.md).

3. **Scope Pass 1 with the scan results:** any awaiting/task row whose source already lit up in the Pass 2 scan (fresh activity on its thread/space/person) is **confirmed-live** — record the activity, skip the re-read of its sources. Every row with NO scan hit is a verification **candidate** and gets the full Pass 1 treatment. Also skip rows already source-verified earlier the same day (a `/gm` or `/work` run) — carry their findings forward instead of re-reading.
4. **Fan out Pass 1 verification across parallel subagents** when candidates exceed ~15 rows: split the candidate rows into 2-4 batches (file order), one read-only agent per batch. Each agent reads every linked source per Steps A-C and returns per-row CLASSIFICATION + EVIDENCE (message IDs/timestamps) + RECOMMENDED UPDATE. **Agents never edit files.** The main session applies all file updates serially after results return (prevents concurrent-edit corruption of `_awaiting.md`/`_tasks.md`).
5. Main session: apply updates, propagate closures, archive, produce the report.

**Coverage caveat:** scoping skips *redundant reads*, never coverage. A row with no scan hit gets its full multi-source read regardless of age (the "don't time-box loop checks" rule is unchanged — a 1d scan window says nothing about a March loop that closed in April).

## Pass 1: Known Loop Resolution

1. Read `ops/_awaiting.md`, `ops/_tasks.md` (Critical/High/Medium), `ops/_contacts.md`, `ops/_index.md`. *(Batched in parallel with the Pass 2 scans — see Execution Order above.)*

2. For each active awaiting item AND open Critical/High task *(candidates only — confirmed-live rows per the Execution Order are recorded from the scan, not re-read)*:

   **Step A — Read every linked source (MANDATORY).** A loop can span multiple sources. The Source field may list one or many of: Gmail thread ID(s), Chat space + message ID, Slack channel/thread, Notion meeting/signal ID. Open every one and read the latest 1-2 messages.
   - Gmail: `mcp__google__gmail_get_message`
   - Google Chat: `chat_list_messages` on the space (filter by recency)
   - Slack: `slack_thread_replies` (Workspace 1: `mcp__slack-workspace-1__`, Workspace 2: `mcp__slack-workspace-2__`)
   - Notion: query Signals/Transcripts DB for the meeting/signal

   If ANY source shows resolution (inbound reply, outbound handoff, third-party closure, cross-tenant forward, meeting decision), mark CLOSED. Skip to next item.

   **Step B — If all sources inconclusive, broaden:**
   - Inbound: Gmail `from:{person}` (all mail, no read-state filter); Chat from that person; Slack from that person; Notion Signals/Transcripts mentioning topic or person.
   - Outbound: Gmail `from:me` (no time filter — loops may be older than 7d); Chat filtered by [YOUR NAME]'s user ID `[YOUR GOOGLE USER ID]`; Slack from [YOUR NAME] (Workspace 1 `[SLACK_WORKSPACE_1_BOT_ID]`, Workspace 2 `[SLACK_WORKSPACE_2_BOT_ID]`).

   **Step C — Classify:**
   - **CLOSED** — Any linked source shows resolution
   - **NUDGED** — [YOUR NAME] followed up, no resolution. Update Last Nudge.
   - **STALE** — 3+ days, all sources silent
   - **CRITICAL** — 5+ days, all sources silent, blocks other work
   - **NO TRACE** — Zero activity anywhere. May be offline.
   - **FRESH** — Within normal response window
   - **FORK** *(TRIAL — added 2026-06-08, revert per changelog if noisy)* — Not stale, not closeable: the loop carries an **unresolved fork**. Both must hold: (1) a linked source or the project `{project}.context.md` shows [YOUR NAME] named 2+ paths / left an explicit either/or unanswered; (2) DOCC cannot safely pick a default (a constraint/veto/guardrail makes one path outward-facing, org-sensitive, or genuinely [YOUR NAME]'s call per the `AskUserQuestion` "answer changes what I do next" bar). Mid-day especially: a fresh inbound can *open* a fork that wasn't there this morning — e.g., a reply that adds a second viable path. Render under **Needs Your Decision** with the open question + named paths, then ask via `AskUserQuestion` so the answer drives the next action (draft / redirect / park). Single-path or safe-default items are NOT forks — keep this rare.

   Never declare stale without reading every linked source. If an item has no source IDs, flag for cleanup.

## Pass 2: Context Discovery

0. **Verbatim email archive (recall layer) — OPTIONAL, background, window-matched.** Skip unless you have set up an email-ingestion helper (this template ships none — the scans below work without it). If you have one, ingest any not-yet-captured mail in the background:
   ```
   # Example, if you have one — adjust to your tool:
   # python tools/ingest_emails.py --after <YYYY/MM/DD = the {window} lookback, min 1 day>
   ```
   Run it with `run_in_background` — it only feeds the header's "Written (new)" count and must not block the scans. The `--after` date matches the scan window (`1d` run → 1 day back; `7d` → 7 days), not a fixed floor: dedup by message_id makes wider windows harmless but pointless when a recent run already ingested them; widen only when there's a known gap (post-OOO, missed days). Such a helper should write one verbatim file per thread (latest message, full quoted chain) to `raw/emails/`, skipping anything already on disk. It is the FULL-TEXT archive — independent of the triage below. Report "Written (new)" in the output.

All Pass 2 scans use the time window from $ARGUMENTS (default 1d / last 24 hours). `{window}` below = that value. **Steps 3-9 are mutually independent — issue them as one parallel batch (with the Pass 1 state-file reads), then do the matching/triage reasoning once everything is back.**

3. Gmail inbox (read + unread): `in:inbox newer_than:{window}`. Match against tracked items. Capture untracked.

4. Gmail outbox: `from:me newer_than:{window}`. Same matching.

5. Google Chat: Active spaces from `ops/_google-chat-spaces.md`. Same matching.

6. Slack Workspace 1: `[SLACK_WORKSPACE_1_BOT_ID] after:[{window} ago]` for mentions. Also scan recent activity in active channels for asks involving [YOUR NAME].

7. Slack Workspace 2: `[SLACK_WORKSPACE_2_BOT_ID] after:[{window} ago]` same.

8. Notion Signals: Query for new signals ({window}) — capture decisions, action items, contacts surfaced.

9. Notion Transcripts: Check for recent meetings ({window}). If a meeting touches an active project/awaiting topic, flag — meetings often close loops the email thread doesn't show.

## Context Capture

| What it looks like | Action |
|---|---|
| [YOUR NAME] asked someone for something | Add to `_awaiting.md` |
| Someone asked [YOUR NAME] for something | Add to `_tasks.md` |
| Person not in `_contacts.md` | Add with role/context |
| Thread relates to a project | Update `{project-name}.context.md` |
| Project-shaped but no context file | Flag for promotion |
| Decision or domain knowledge | Add to `ops/_kb/_inbox.md` (or scoped `_kb/{scope}/{topic}.md`) or project context |
| Pure FYI | Skip (note in summary count) |

## Output

Lead with what needs [YOUR NAME]'s attention NOW. Loop bookkeeping comes after.

```
## Follow-Up Report - [Date]
[Scope]

### Needs Your Response (blocking others)
- [From]: [Topic] — [What they need] — [Source]

### Needs Your Decision
- [Topic] — [Options] — [Source]
- [FORK items — open question + named paths. Ask via AskUserQuestion so the answer drives the next action. TRIAL 2026-06-08.]

### Critical (5+ days, blocking your work)
- [Person] — [What you asked] — [X days] — Blocks [what]
  Suggested action: [Escalate / different channel / ask someone else]

### Stale (needs nudge)
- [Person] — [What] — [X days] — All sources silent
  Suggested nudge: "[Draft in [YOUR NAME]'s voice]"

### Loops Closed (auto-resolved this run)
- [Person] re: [topic] — [How resolved] — [Source]

### Loops Nudged
- [Person] re: [topic] — Last Nudge: [date]

### Out-of-Band Activity (you did outside DOCC)
- [Channel sent to X re: Y — matches awaiting Z, updated Last Nudge]
- [Or: "No outbound detected"]

### New Context Captured
- New awaiting: [list]
- New tasks: [list]
- New contacts: [list]
- Project updates: [list]
- Knowledge captured: [list]
- Orphan threads: [list]

### No Trace
- [Person] — [What] — [X days] — Handled offline?

### Fresh
- [N] items within normal response window
```

Output ordering principle: action-required items at the top, loop bookkeeping in the middle, low-priority context at the bottom. [YOUR NAME] should see "what needs me now" in the first screen.

## File Updates (auto-save, don't ask)

- **Propagate every closure to `_tasks.md`.** A closed loop is often double-tracked as a task row. For each loop you close, grep `_tasks.md` for the same topic / person / ticket and strike the twin row with a matching DONE/CLOSED note. Mandatory — a closure recorded in only one file is drift. See `ops.md` → Closure Propagation.
- **Move closed/struck rows to `ops/_archive/`** (`awaiting-archive.md` / `tasks-archive.md`) in the same pass, under a `## Sweep YYYY-MM-DD` section. Hot files keep only open loops. See `ops.md` → Archive Routing.
- **Header narrative:** when rewriting a hot file's `**Last Updated:**` line, move the previous narrative to the matching archive file. One update deep, never chained.
- Update Last Nudge dates
- Add new awaiting/tasks/contacts
- Update relevant project context files
- Add knowledge entries to `ops/_kb/_inbox.md` (or directly to the scoped `_kb/{scope}/{topic}.md`) with source
- This run is not complete until `_awaiting.md` and `_tasks.md` agree on every item touched and closures are archived.

## Rules

- Lead with action items (Needs Response / Decision / Critical / Stale). Loop bookkeeping comes after.
- Read every linked source BEFORE keyword search. Source field is source of truth.
- A task can span multiple sources (e.g., email thread + chat space + meeting signal). Read all of them.
- Cover all 4 channel families: Gmail (in + out), Google Chat, Slack (Workspace 1 + Workspace 2), Notion (Signals + Transcripts).
- Search ALL mail for known loops. [YOUR NAME] archives outside DOCC.
- Don't time-box loop checks (Pass 1). A Mar 12 loop may have closed Apr 27. Time window applies only to Pass 2 discovery. (Scan-hit scoping per Execution Order skips redundant reads only — a no-hit row gets its full read regardless of age.)
- Verification subagents are READ-ONLY. All `_awaiting.md`/`_tasks.md`/archive edits happen in the main session, serially, after agent results return.
- When verifying a row, re-list the thread/space for its NEWEST messages — never re-read only the message ID stored in the row. Check delegate sends ([YOUR DIRECT REPORTS]), not just `from:me`.
- Inbox scan includes read messages. Inbox = unprocessed.
- Partial response is NOT a closed loop. Note it, keep loop open.
- Response waiting 2+ days from someone [YOUR NAME] owes → flag urgent in "Needs Your Response."
- Draft nudges in [YOUR NAME]'s voice (`ops/_kb/people-and-tone/voice.md`).
- Cross-tenant emails: [YOUR NAME] has multiple addresses ([EMAIL], [EMAIL]). Read the thread, not just the sender list.
- Orphan threads are the value of Pass 2. Surface them clearly.

## Cadence

- **Default / quick check:** `/followup` — 24h window (1d), leads with what needs you now. Pass 1 loop verification always runs in full regardless of window.
- **Weekly reconciliation:** `/followup 7d` — broader discovery sweep
- **Deep sweep:** `/followup 14d` — broadest discovery, useful after OOO or before `/weekly`
