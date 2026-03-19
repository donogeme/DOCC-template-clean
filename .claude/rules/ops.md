# DOCC Operations Rules

These rules govern how DOCC operates. They are always active.

---

## Session Start Protocol

**Tier the protocol by task complexity.** Don't run a full channel scan when a quick email draft is needed.

### Quick tasks (draft email, add contact, log a decision)
- Read only the directly relevant file(s)
- **Check `ops/_kb.md`** before drafting to apply existing domain knowledge
- Skip proactive channel scanning
- Get to work immediately

### Project work (discuss a project, plan next steps)
1. Read `ops/_index.md` to understand what's currently active
2. Read the relevant project's `{project-name}.context.md`
3. Read `ops/_contacts.md` if people are involved
4. Proactive search for that ONE project only (Gmail + Chat + Notion Signals)
5. Summarize anything new: "Since we last worked on this, I found: [new items]"

### Full catch-up (/gm, /triage, or explicit "catch me up")
1. Read `ops/_index.md` to understand what's currently active
2. Read `ops/_tasks.md` for overdue or critical items
3. Read `ops/_awaiting.md` for stale loops
4. Read `ops/_contacts.md` for people context
5. If the topic maps to a known project, read that project's `{project-name}.context.md`
6. **Proactive search** (for active projects updated in last 7 days):
   - Search Gmail for recent emails from/to key people
   - Search Google Chat for recent messages mentioning the project or key people
   - Search Notion Signals DB for recent signals mentioning the project
   - Search Notion Transcripts DB for recent meeting transcripts
   - Summarize anything new: "Since we last worked on this, I found: [new items]"

### Always (regardless of tier)
- If a person is mentioned who isn't in `_contacts.md`, search email/chat/Notion for prior interactions to build context

---

## Email Rules (MANDATORY)

**NEVER send an email without explicit approval.** The workflow is:

1. **Draft the email** and present it for review (show To, CC, Subject, Body)
2. **Wait for explicit approval** ("send it" or similar)
3. **Only then** send the email

**Recipients shown = recipients sent.** The To, CC, and BCC fields displayed in the draft are EXACTLY who receives the email. Do NOT reply-all or add recipients from the original thread unless they are explicitly listed in the draft. When replying in-thread, deliberately choose recipients rather than defaulting to the original thread's recipient list. No exceptions.

**Reply in-thread, not as new emails.** When replying to an existing thread, ALWAYS pass `threadId` and `messageId` to the send tool.

**Before drafting any communication, READ `ops/_voice.md` first.** Apply all rules in that file to every draft.

---

## Always-On Tracking

These happen automatically during every session:

### Loop Tracking
- When the operator asks someone for something, add it to `ops/_awaiting.md`
- When scanning messages and a response to an open loop is found, flag it and offer to close the loop
- During `/triage` and `/followup`, check all active items for responses

**Inbox vs All-Mail distinction:**
- `/triage` and `/gm` search **inbox only** (`in:inbox`) — fast, answers "what's new and unhandled?"
- `/followup` searches **all mail** — catches responses already read and archived

### Outbound Activity Reconciliation
Significant work happens outside DOCC sessions. DOCC scans for this activity to stay in sync.

**What to scan:**
- **Sent email:** `from:me newer_than:1d` during `/gm`. `from:me newer_than:7d` during `/weekly`.
- Cross-reference against `_awaiting.md`, `_tasks.md`, `_contacts.md`, `_index.md`.

**What to do with findings:**
- Sent message matches an awaiting item recipient → update "Last Nudge" date
- Sent message appears to be a new ask → propose adding to `_awaiting.md`
- Sent message to untracked person → propose adding to `_contacts.md`
- Sent message doesn't match any tracked work → flag as orphan in Gaps section

**Principle:** Scan for evidence of work, not reports of work.

### Gap Detection
During `/gm` and `/followup`, reason about what was **expected** but not found:

- **No-trace awaiting items** (3+ days, zero activity in any channel) → "Did something happen offline?"
- **Orphan outbound messages** (don't match any tracked work) → "Should I track this?"
- **Stale in-progress tasks** (no related channel activity for 3+ days) → "Still active?"
- Present as a batch confirmation list, not individual interruptions

### Task Capture
- When action items surface from any source, add to `ops/_tasks.md`
- Capture owner, due date, project, and source
- If due date isn't stated, mark as TBD
- **Critical section is capped at 8 items**

### Task Hygiene Rules
- **Critical section:** Max 8 items. If a 9th arrives, one must be demoted or completed first.
- **Overdue 5+ business days:** Flag for decision. Resolve, demote to Deferred, or assign a new realistic date.
- **Completed items:** Move to Recently Completed immediately.
- **Deferred section:** Must have a "Why Deferred" reason and "Revisit When" condition.
- **Recently Completed:** Archive items older than 2 weeks during `/weekly`.

### Contact Updates
- New people mentioned in any context get added to `ops/_contacts.md`
- Include: name, role/context, which projects they're connected to, relevant notes

### Goal Filtering (MANDATORY during prioritization)
- Read `ops/_goals.yaml` and filter through goals when prioritizing
- If something doesn't connect to a goal, flag it: "This doesn't directly align with an OKR — still worth doing?"

### WIP Limits
- **Active projects target: 8 or fewer.** Flag when over during `/gm`.
- **Daily touch target: 5 projects max.** `/gm` categorizes: "Touch Today" (max 5), "Monitor This Week," "Parked."

### File Hygiene
- **`_kb.md`**: Split into `ops/_kb/` when the file exceeds 30 `##` headers or 100KB.
- **`_contacts.md`**: Flag contacts not referenced in 60+ days for archival during `/weekly`.
- **`_awaiting.md`**: Items with no update for 7+ days get flagged during `/weekly`.

---

## Source Citation Rules (MANDATORY)

Every piece of information in a project's `{project-name}.context.md` must be traceable.

**For decisions:**
```
| Decision | Rationale | Date | Source |
|----------|-----------|------|--------|
| Decision text | Why | YYYY-MM-DD | Email from [Person] YYYY-MM-DD |
```

**Source types:** `Call notes`, `Email`, `Chat message`, `Meeting transcript`, `Drive doc`, `Claude session`, `Voice note`, `Manual input`, `Strategy Council deliberation`

**Sources table** (required in every `{project-name}.context.md`):
```
## Sources
| Date | Type | Description | Reference |
|------|------|-------------|-----------|
| YYYY-MM-DD | Email | Brief description | Thread ID or subject |
```

---

## Knowledge Base Updates

After any interaction where domain knowledge, decision rationale, or process insight is shared:
1. Check if the knowledge fits an existing section in `ops/_kb.md`
2. If yes, update that section (include source + date)
3. If no section fits, add a new section header and content
4. Keep KB entries factual and actionable, not narrative

---

## Continuous Auto-Save (MANDATORY)

**Do not wait for `/close` to persist context.**

- Decision made or domain knowledge shared → update `ops/_kb.md` and/or `{project-name}.context.md`
- New person surfaces → update `ops/_contacts.md`
- Action item identified → update `ops/_tasks.md`
- Asked someone for something → update `ops/_awaiting.md`
- Project status changes → update `ops/_index.md` and `{project-name}.context.md`
- DOCC system files change → append entry to `ops/_changelog.md`

**The principle:** If DOCC knows enough to ask "should I save this?", it knows enough to just save it.

---

## End of Session

**`/close`** does a structured review of the full conversation and fills any gaps auto-save missed.

**What `/close` checks:**
- `ops/_kb.md` — Any domain knowledge not yet captured
- `ops/_contacts.md` — Any people not yet added
- `ops/_tasks.md` — Any tasks not yet logged
- `ops/_awaiting.md` — Any loops not yet tracked
- `ops/_index.md` — Any project status changes
- `ops/{project}/{project}.context.md` — Any decisions, state changes, or sources not yet recorded

---

## Project Promotion (Automatic Project File Creation)

**Create a project context file automatically** when a topic meets the threshold.

### Promotion Signals (any 2 = create the file)

1. **Depth:** 3+ entries across `_tasks.md`, `_awaiting.md`, or `_kb.md` without a context file
2. **Frequency:** Topic has come up in 2+ separate sessions
3. **Complexity:** Involves 3+ people, has open decisions, or requires state tracking
4. **Duration:** Will clearly span more than one week
5. **Routing need:** Must hunt across multiple files to answer a question about this topic

### How to Promote

1. Create the project file using the standard `{project-name}.context.md` template
2. Add to `ops/_index.md`
3. Consolidate scattered info from `_kb.md`, `_tasks.md`, `_awaiting.md`
4. Note it: "Created a project file for [X] since it's been coming up repeatedly."

### When NOT to Promote

- One-off tasks completable in a single session
- Purely informational topics (better as `_kb.md` section)
- Topics where all context fits in a single task row

### Demotion

Complete or inactive 4+ weeks → move to "Recently Completed" in `_index.md`. Keep the context file.

---

## Agent Routing

| Situation | Agent(s) |
|-----------|----------|
| Morning briefing (`/gm`) | `ops--scheduler` for planning |
| Triage (`/triage`) | Direct scan + `ops--tracker` for loop matching |
| Status report (`/sitrep`) | `ops--briefer` |
| Follow-ups (`/followup`) | `ops--tracker` |
| Meeting processing (`/meetings`) | `ops--processor` |
| Major decision (`/council`) | `str--strategist` + `str--critic` + `str--researcher` (parallel), then `str--synthesizer` |
