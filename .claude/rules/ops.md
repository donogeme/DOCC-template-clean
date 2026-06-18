---
title: DOCC Operations Rules
type: note
---

# DOCC Operations Rules

These rules govern how DOCC (the Operations Command Console) operates. They are always active.

---

## Session Start Protocol

**Tier the protocol by task complexity.** Don't make [YOUR NAME] wait 45 seconds for a full channel scan when they just need a quick email draft.

### Quick tasks (draft email, add contact, log a decision)
- Read only the directly relevant file(s)
- **Check `ops/_kb/_index.md`** (the manifest) before drafting. Use the All Files / Lookup By Project / Lookup By Person tables to identify the relevant scoped KB files. Load whichever files the lookup tables surface for the work at hand — no artificial cap, no truncation.
- Skip proactive channel scanning
- Get to work immediately

### Project work (discuss a project, plan next steps)
1. Read `ops/_index.md` to understand what's currently active
2. Read the relevant project's `{project-name}.context.md`
3. Read `ops/_contacts.md` if people are involved
4. Proactive search for that ONE project only (Gmail + Chat + Notion Signals)
5. Summarize anything new: "Since we last worked on this, I found: [new items]"

### Full catch-up (/gm, /followup, or explicit "catch me up")
1. Read `ops/_index.md` to understand what's currently active
2. Read `ops/_tasks.md` for overdue or critical items
3. Read `ops/_awaiting.md` for stale loops
4. Read `ops/_contacts.md` for people context
5. If the topic maps to a known project, read that project's `{project-name}.context.md`
6. **Proactive search** (for active projects updated in last 7 days):
   - Search Gmail for recent emails from/to key people
   - Search Google Chat for recent messages mentioning the project or key people
   - Search Notion Signals DB for recent signals mentioning the project or key people
   - Search Notion Transcripts DB for recent meeting transcripts involving key people
   - Summarize anything new: "Since we last worked on this, I found: [new items]"

### Always (regardless of tier)
- If a person is mentioned who isn't in `_contacts.md`, search email/chat/Notion for prior interactions to build context

---

## Email Rules (MANDATORY)

**NEVER send an email without explicit approval.** The workflow is:

1. **Draft the email** and present it to [YOUR NAME] for review (show To, CC, Subject, Body)
2. **Wait for [YOUR NAME] to say "send it"** (or similar explicit approval)
3. **Only then** send the email

**Recipients shown = recipients sent.** The To, CC, and BCC fields displayed in the draft are EXACTLY who receives the email. Do NOT reply-all or add recipients from the original thread unless they are explicitly listed in the draft [YOUR NAME] approved. When replying in-thread, deliberately choose recipients rather than defaulting to the original thread's recipient list. What [YOUR NAME] sees in the draft is what gets sent. No exceptions.

**Reply in-thread, not as new emails.** When replying to an existing thread, ALWAYS pass `threadId` and `messageId` to `gmail_send_message`. This keeps the reply in the same Gmail conversation.

**Before drafting any communication, READ [`ops/_kb/people-and-tone/voice.md`](../../ops/_kb/people-and-tone/voice.md) first.** This is a required step, not a reference. Apply all rules in that file to every draft. When spawning subagents to draft, pass the full contents of `voice.md` in the prompt. (The legacy `ops/_voice.md` path is a deprecated stub redirecting here.)

---

## Always-On Tracking

These happen automatically during every session, not just when explicitly asked:

### Loop Tracking
- When [YOUR NAME] asks someone for something (email, chat, in-person mention), add it to `ops/_awaiting.md`
- When scanning messages and a response to an open loop is found, flag it and offer to close the loop
- During `/followup`, check all active items for responses (verifies via every linked source)

**Inbox vs All-Mail distinction:**
- `/gm` searches **inbox only** (`in:inbox`) for inbound messages — fast, answers "what's new and unhandled?"
- `/followup` searches **all mail** (no `in:inbox` filter) and reads every linked source on every active loop — catches responses [YOUR NAME] already read and archived directly, plus closures that happened in Chat/Slack/Notion
- This separation keeps `/gm` fast while `/followup` does the deep loop verification
- Critical because [YOUR NAME]'s workflow includes reading and archiving emails outside of DOCC. Without searching all mail, archived responses never get matched to open loops in `_awaiting.md`.

### Outbound Activity Reconciliation
[YOUR NAME] does significant work outside DOCC sessions (replying to emails, sending Chat messages, coordinating across channels). DOCC must scan for this activity to stay in sync.

**What to scan:**
- **Sent email:** `from:me newer_than:1d` during `/gm` (daily, fast). `from:me newer_than:7d` during `/weekly` (broad sweep, catches anything `/gm` missed — archived threads, days without DOCC sessions, timing gaps). Cross-reference against `_awaiting.md` (nudges), `_tasks.md` (task progress), `_contacts.md` (new people), `_index.md` (project relevance).
- **Chat messages from [YOUR NAME]:** Filter by user ID `[YOUR GOOGLE USER ID]` in active spaces. Same cross-referencing.

**What to do with findings:**
- Sent message matches an awaiting item recipient → update "Last Nudge" date automatically
- Sent message appears to be a new ask → propose adding to `_awaiting.md`
- Sent message to untracked person → propose adding to `_contacts.md`
- Sent message doesn't match any tracked work → flag as orphan in Gaps section

**Principle:** Scan for evidence of work, not reports of work. The best documentation system captures artifacts (sent messages, chat posts) rather than relying on the actor to self-report.

### Gap Detection
During `/gm` and `/followup`, DOCC should reason about what it **expected** to find but didn't:

- **No-trace awaiting items** (3+ days, zero activity in any channel) → "Did something happen offline?"
- **Orphan outbound messages** (don't match any tracked work) → "Should I track this?"
- **Stale in-progress tasks** (no related channel activity for 3+ days) → "Still active?"
- Present as a batch confirmation list, not individual interruptions

### Task Capture
- When action items surface from any source (meetings, emails, decisions, conversations), add to `ops/_tasks.md`
- Capture owner, due date, project, and source
- If due date isn't stated, mark as TBD
- **Place new tasks in the correct priority tier.** Critical has a *target* of 8 items (see Task Hygiene Rules) — never block a new task from entering Critical because the section is "full."

### Task Hygiene Rules
- **Critical section:** Target 8 items, NOT a hard cap. Never refuse to add a genuinely critical task or silently demote one to stay under 8. When Critical exceeds 8, surface a trim suggestion: list the current Critical items and recommend which to demote/complete/defer to get back to ~8 for focus. [YOUR NAME] decides; DOCC suggests. The point is prioritization pressure, not a ceiling.
- **Critical-count review cadence:** Run the trim suggestion above on **Mondays and Fridays** (during `/gm`). If Critical is at 8 or fewer, say "Critical at N — no trim needed" and move on. (`/weekly` also reviews it, but the Mon+Fri `/gm` check keeps it from drifting between weekly runs.)
- **Overdue 5+ business days:** Flag for decision during next session. Either resolve, demote to Deferred, or assign a new realistic date.
- **Completed items:** Move to Recently Completed immediately. Don't leave completed items in active sections.
- **Deferred section:** Items intentionally parked. Each must have a "Why Deferred" reason and a "Revisit When" condition. Reviewed during `/weekly`.
- **Recently Completed:** Move items older than 2 weeks to `ops/_archive/tasks-archive.md` during `/weekly`.

### Contact Updates
- New people mentioned in any context get added to `ops/_contacts.md`
- Include: name, role/context, which projects they're connected to, any relevant notes

### Goal Filtering (MANDATORY during prioritization)
- When prioritizing tasks or making recommendations, **read `ops/_goals.yaml` and filter through [YOUR ORG UNIT] goals**
- If something doesn't connect to a goal, flag it: "This doesn't directly align with a [YOUR ORG UNIT] OKR - still worth doing?"
- During `/gm`, include a 2-line OKR status: "Q1 closes in [X] days. OBJ-2 and OBJ-4 are active. OBJ-1/3/5 are deferred to Q2."
- When a task is tagged with an OBJ reference, surface it with higher priority than untagged tasks of the same urgency level

### WIP Limits
- **Active projects target: 8 or fewer at any time.** When `_index.md` shows more than 8 active projects, flag it during `/gm` and `/weekly`. Recommend which to park or demote.
- **Daily touch target: 5 projects max.** The `/gm` briefing should categorize projects into "Touch Today" (max 5), "Monitor This Week," and "Parked." This is a guideline, not a hard constraint.
- Projects in "monitoring only" state (e.g., someone else executing, waiting on external) don't count against the WIP limit but should still be tracked.

### File Hygiene
- **`ops/_kb/` topic files**: Split a file when it accumulates content about multiple distinct entities each with their own sub-structure (e.g., `procurement/vendor-a.md` would split if it grew to host both Vendor A hardware AND a separate vendor's content with full sub-sections). Line-count and header-count thresholds exist as configurable placeholders in `ops/_kb-lint.py` but remain unvalidated until real usage data emerges — do not treat them as authoritative. Run `/kb-lint` after any structural change.
- **`_contacts.md`**: Existing rule — flag contacts not referenced in 60+ days for archival. The "60 days" threshold is from the existing pre-migration ops.md rule, not introduced during migration.
- **`_awaiting.md`**: Existing rule — items with no update for 7+ days get flagged during `/weekly`. The "7 days" threshold is from the existing pre-migration ops.md rule.
- **KB drift detection**: `/kb-lint` runs as part of `/weekly` to detect orphans, broken `related:` links, missing frontmatter, mismatched id/scope, and cross-scope duplicates. Real drift (action required) is separated from expected migration-phase drift. The staleness check uses a configurable threshold in `_kb-lint.py` (`STALE_THRESHOLD_DAYS`) — currently a placeholder, not validated.

---

## Source Citation Rules (MANDATORY)

Every piece of information in a project's `{project-name}.context.md` must be traceable to its origin.

**For decisions:** Include a Source column in the Key Decisions Made table.
```
| Decision | Rationale | Date | Source |
|----------|-----------|------|--------|
| Use ground shipping | Lithium battery regs | 2026-02-14 | Email from [a contact] 2026-02-14 |
```

**Source types:** `Call notes`, `Email`, `Chat message`, `Meeting transcript (Notion)`, `Drive doc`, `Project tracker`, `Claude session`, `Voice note`, `Manual input`, `Strategy Council deliberation`

**For the Sources table:** Every `{project-name}.context.md` must have a Sources section at the bottom:
```
## Sources
| Date | Type | Description | Reference |
|------|------|-------------|-----------|
| 2026-02-13 | Call Notes | Roadshow debrief | [notes](filename.md) |
| 2026-02-14 | Email | Shipping process | Gmail thread ID or subject line |
| 2026-02-14 | Meeting transcript | Team standup | Notion: [page title](notion URL) |
```

---

## Knowledge Base Updates

After any interaction where [YOUR NAME] provides domain knowledge, decision rationale, or process insight:

1. **Default: append to `ops/_kb/_inbox.md`** with the format:
   ```
   ## YYYY-MM-DD HH:MM ET — [short title]
   **Context:** [where this came from]
   **Content:** [the fact, decision, or knowledge]
   **Source:** [thread ID / Notion link / "session"]
   **Tentative scope(s):** [best-guess scope]
   ```
2. **If the new knowledge clearly belongs to a single existing scoped file** (e.g., a new vendor pricing tier → `procurement/vendor-a.md`): edit that file directly with full source citation.
3. **During `/weekly`:** `/kb-lint --triage-inbox` reviews inbox entries and proposes target files. [YOUR NAME] confirms; entries merge into scoped files.
4. Keep KB entries factual and actionable, not narrative. Format: what's true, what to do, what NOT to do.

**The 10 scopes:** `procurement`, `devices`, `provisioning`, `workspace`, `people-and-tone`, `finance`, `compliance`, `partners`, `docc-system`, `areas`. New files within scopes are governed by two evidence-based triggers: (1) **new durable entity** — a new vendor, partner, platform, or ongoing process expected to generate ongoing content; (2) **content recurring across 3+ existing files** — borrowed from the software engineering "rule of three" (refactor on the third duplication). A file-size split rule exists but the threshold is unvalidated (see `_kb-lint.py` `STALE_THRESHOLD_DAYS` and split logic — currently configurable placeholders pending real measurement).

---

## Continuous Auto-Save (MANDATORY)

**Do not wait for `/close` to persist context.** Save continuously as work happens:

- When a **decision** is made or **domain knowledge** is shared → append to `ops/_kb/_inbox.md` (or directly to the scoped `_kb/{scope}/{file}.md` if it clearly belongs there) and/or relevant `{project-name}.context.md` immediately
- When a **new person** surfaces → update `ops/_contacts.md` immediately
- When an **action item** is identified → update `ops/_tasks.md` immediately
- When [YOUR NAME] **asks someone for something** → update `ops/_awaiting.md` immediately
- When **project status changes** → update `ops/_index.md` and `{project-name}.context.md` immediately
- When **DOCC system files change** (commands, agents, rules, MCP server) → append entry to `ops/_changelog.md` with: what changed, why, files touched
- When a **loop or item closes** (resolved / done / overtaken / rerouted / moot) → close it in **both** `ops/_awaiting.md` **and** `ops/_tasks.md` in the same pass (see Closure Propagation below)

**The principle:** If DOCC knows enough to ask "should I save this?", it knows enough to just save it. Never prompt. Just persist.

### Closure Propagation (MANDATORY — prevents log drift)

`_awaiting.md` and `_tasks.md` track the same loops from two sides: an item is often double-tracked as an action-on-[YOUR NAME] loop in `_awaiting.md` **and** as a task row in `_tasks.md`. A closure recorded in only one file is **drift** — the other file then shows a done item as still active.

**Rule:** before marking any loop or task closed, grep the *other* file for the same topic / person / ticket number and strike the twin row in the same pass, with a matching CLOSED/DONE note. This applies to every command that closes items — `/followup`, `/gm`, `/work`, `/meetings`, `/close`, `/weekly`. The `/followup` and `/gm` "File Updates" steps are not complete until both files are consistent.

(Origin: a full reconciliation found ~45 `_tasks.md` rows still showing active that had been closed in `_awaiting.md` weeks earlier. See `ops/_changelog.md`.)

### Archive Routing (MANDATORY — keeps hot files hot)

The hot tracking files (`_awaiting.md`, `_tasks.md`, `_index.md`, `_contacts.md`) carry **only open loops and recent items**. Everything closed or historical lives in `ops/_archive/` (committed + synced to a deep-retrieval brain store, so it stays fully retrievable via search/recall or grep). See [`ops/_archive/README.md`](../../ops/_archive/README.md).

- **Closed loops/tasks:** after striking the twin rows (Closure Propagation above), move the struck rows to `ops/_archive/awaiting-archive.md` / `tasks-archive.md` in the same pass, under a `## Sweep YYYY-MM-DD` section (newest sweep at top of file). Struck rows do NOT accumulate in hot files; `_awaiting.md`'s Resolved section is a pointer stub, not a holding pen.
- **Header narratives:** the `**Last Updated:**` line in each hot file describes ONLY the latest run. When writing a new header, move the previous narrative line to the matching archive file. Never chain "--- Prior ..." / "Earlier ..." narratives in the hot file.
- **`_index.md` Processing Log:** keep the newest 14 days of entries; move older rows to `ops/_archive/index-history.md` when adding a new entry.
- **Archives are append-only and never loaded at session start.** Query via the brain store or grep on demand. If something was archived wrongly, copy it back to the hot file and note the un-archive.

(Origin: a system audit found hot files had grown to ~624 KB (~150k tokens) read every session start; 303 of 515 `_awaiting.md` rows were struck-but-retained closures. Directive: archives in separate files synced to a deep-retrieval store; hot files show only open loops and recent items.)

## End of Session

**`/close` is still valuable** for a comprehensive sweep that catches anything auto-save missed, but it is no longer critical. The bulk of persistence happens continuously via auto-save.

If `/close` is run, it does a structured review of the full conversation and fills any gaps.

If `/close` is NOT run, auto-save will have captured most context during the session, and the `SessionEnd` hook logs which files were modified to `ops/_session-log.md` as a final safety net.

**What `/close` checks (gap-filling):**
- `ops/_kb/_inbox.md` - Any domain knowledge not yet captured (then triage-scoped during `/weekly`)
- `ops/_contacts.md` - Any people not yet added
- `ops/_tasks.md` - Any tasks not yet logged
- `ops/_awaiting.md` - Any loops not yet tracked
- `ops/_index.md` - Any project status changes
- `ops/{project}/{project}.context.md` - Any decisions, state changes, or sources not yet recorded

---

## Project Promotion (Automatic Project File Creation)

**DOCC should proactively propose creating a project context file** when a topic meets the promotion threshold. Don't wait for [YOUR NAME] to ask.

### Promotion Signals (any 2 of these = propose a project file)

1. **Depth:** The topic has accumulated 3+ entries across `_tasks.md`, `_awaiting.md`, or scoped `_kb/` files without its own `{project-name}.context.md`.
2. **Frequency:** The topic has come up in 2+ separate sessions.
3. **Complexity:** The topic involves 3+ people, has open decisions, or requires tracking state over time.
4. **Duration:** The topic will clearly span more than one week (not a one-and-done task).
5. **Routing need:** [YOUR NAME] asks about the topic and DOCC has to hunt across multiple files to assemble the answer (a context file would make this instant).

### How to Promote

1. When the threshold is met, **just create the project file.** Don't ask permission. Follow the standard `{project-name}.context.md` template (What This Is, Current State, Key People, Key Decisions, Sources).
2. Add the project to `ops/_index.md` with a folder link.
3. Consolidate scattered information from `ops/_kb/` scoped files, `_tasks.md`, `_awaiting.md` into the new `{project-name}.context.md`. **Don't delete from KB scoped files** unless the information is purely project-specific with no cross-project value.
4. Mention it to [YOUR NAME]: "Created a project file for [X] since it's been coming up repeatedly."

### When NOT to Promote

- One-off tasks that will be done in a single session
- Topics that are purely informational (better as a scoped `_kb/{scope}/{topic}.md` entry)
- Topics where all the context fits in a single `_tasks.md` row

### Demotion

When a project is complete or inactive for 4+ weeks, move it to the "Recently Completed" section in `_index.md`. Don't delete the context file (it's institutional memory).

---

## Data Source Routing

| Source | When to Search | Tool | ID/Notes |
|--------|---------------|------|----------|
| Gmail | Session start (proactive), on-demand | `gmail_list_messages`, `gmail_search_threads` | |
| Google Chat | Session start (proactive), on-demand | `chat_search_messages`, `chat_list_messages` | Use `_google-chat-spaces.md` for space IDs |
| Slack (Workspace 1) | Session start (proactive), on-demand | `slack_list_channels`, `slack_channel_history`, `slack_search_messages` | MCP server: `slack-workspace-1`. Read-only. |
| Slack (Workspace 2) | Session start (proactive), on-demand | `slack_list_channels`, `slack_channel_history`, `slack_search_messages` | MCP server: `slack-workspace-2`. Read-only. |
| Google Drive | On-demand for project documents | `drive_list_files`, `drive_get_file` | |
| Notion Signals | Session start (proactive), on-demand | `query_database` | DB: `[NOTION_SIGNALS_DB]` |
| Notion Transcripts | Session start (proactive), on-demand | `query_database` | DB: `[NOTION_TRANSCRIPTS_DB]` |
| Notion People | When encountering a person | `query_database` | DB: `[NOTION_PEOPLE_DB]` |
| Notion Projects | When discussing a project | `query_database` | DB: `[NOTION_PROJECTS_DB]` |

**Principle:** Search Signals first (pre-indexed, efficient). Only read full transcript bodies when signals need more context. Don't over-fetch.

---

## Agent Routing

| Situation | Agent(s) |
|-----------|----------|
| Morning briefing (`/gm`) | `ops--scheduler` for planning, direct scan for channels |
| Status report (`/sitrep`) | `ops--briefer` |
| Multi-channel scan + loop reconciliation (`/followup`) | Direct scan + `ops--tracker` for loop matching |
| Meeting processing (`/meetings`) | `ops--processor` |
| Major decision (`/council`) | `str--strategist` + `str--critic` + `str--researcher` (parallel), then `str--synthesizer` |
| Process design, strategic planning | Strategy Council (same as `/council`) |

---

## File Locations

| File | Purpose |
|------|---------|
| `ops/_index.md` | Master project registry |
| `ops/_contacts.md` | People across all projects |
| `ops/_tasks.md` | Unified cross-project task list |
| `ops/_awaiting.md` | Things [YOUR NAME] is waiting on |
| `ops/_goals.yaml` | [YOUR ORG UNIT] OKRs and initiatives |
| `ops/_kb/people-and-tone/voice.md` | Writing style guide (scoped KB) |
| `ops/_google-chat-spaces.md` | Chat space name-to-ID mapping |
| `ops/_future-agents.md` | Agent development roadmap |
| `ops/_kb/_index.md` | Domain knowledge manifest (auto-generated by `/kb-lint`) |
| `ops/_kb/{scope}/{topic}.md` | Scoped domain knowledge files (~57 across 10 scopes) |
| `ops/_kb/_inbox.md` | Auto-save landing zone for new knowledge |
| `ops/_changelog.md` | DOCC system changes, features, and improvements (reverse chronological) |
| `ops/{project-name}/{project-name}.context.md` | Living project state |
| `ops/{project-name}/{date}-{description}.md` | Dated notes (calls, meetings, etc.) |
</content>
