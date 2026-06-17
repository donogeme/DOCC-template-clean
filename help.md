---
title: DOCC Command Reference
type: note
---

# DOCC Command Reference

## Commands at a Glance

| Command | When to Use | Inputs / Sources | Output |
|---|---|---|---|
| `/gm` | Start of day. "What needs my attention?" | Gmail (inbox + sent), Google Chat (all spaces), Slack (Workspace 1 + Workspace 2), Notion Signals, Google Calendar, `_tasks.md`, `_awaiting.md`, `_goals.yaml`, `_contacts.md`, `_index.md`, `ops/router-engine/_routing.md` | Structured morning briefing: Action Required (with inline routing suggestions for ROUTE items), Loop Updates, Out-of-Band Activity, FYI, Calendar, Must Do Today, People Waiting on You, You're Waiting On, Gaps & Reconciliation, Time Block suggestions |
| `/followup` | "Who owes me something?" + mid-day inbox check (`/followup 1d`) | Gmail (ALL mail including archived + sent), Google Chat, Slack (Workspace 1 + Workspace 2), Notion Signals, `_awaiting.md`, `_tasks.md`, `_contacts.md`, `_index.md` | Follow-up report: Needs Response, Needs Decision, Critical, Stale (with draft nudges), Loops Closed, Loops Nudged, Out-of-Band Activity, New Context Captured. Auto-updates all ops files. |
| `/queue` | "What am I working on?" | Local files only: `_tasks.md`, `_index.md`, project context files. Zero network calls. | Prioritized task list by tier (Critical/High/Medium/Low/Deferred) with status badges (OVERDUE, DUE TODAY, BLOCKED, WAITING, READY, STALE). Summary counts. |
| `/sitrep` | [YOUR BOSS] wants an update, or you need to push info to your team. | `_index.md`, `_tasks.md`, `_goals.yaml`, `_awaiting.md`, project context files, `ops/_kb/people-and-tone/voice.md` | Drafted status report tailored to audience ([YOUR BOSS], team, project-specific, or full). Email draft presented for approval before sending. |
| `/work` | Execute Green tasks, prep Yellow tasks, or draft something. | `_tasks.md`, `_awaiting.md`, `_contacts.md`, `_index.md`, `ops/_kb/_index.md`, `ops/_kb/people-and-tone/voice.md`, live thread sources | Work report: Completed (Green), Ready for Review (Yellow drafts), Remaining (Red), Parked (Gray). Email drafts presented for approval; never auto-sends. Handles ad-hoc draft requests as well — for one-offs not tied to a tracked task, just ask conversationally. |
| `/route` | "Who handles X?" — single-topic routing lookup. | `ops/router-engine/_routing.md`, `_kb/_index.md`, `_contacts.md` | Recommended owner with confidence score (HIGH/MED/LOW), reasoning, fallback options. |
| `/council` | Big decision with real consequences. "Should we do X or Y?" | `_index.md`, `_goals.yaml`, relevant project context files, `_tasks.md`, web research (via researcher agent) | Strategy Council recommendation: Strategist's view, Critic's concerns, Evidence base, Alternatives considered, Decision framework, Confidence level. Decision logged to project context. |
| `/meetings` | After meetings get transcribed to Notion. | Notion Signals DB, Notion Transcripts DB (full body if needed), `_index.md`, `_contacts.md` | Processing report: Decisions extracted, Action items captured, New contacts added. Auto-updates `_tasks.md`, `_contacts.md`, project context files, Sources tables. |
| `/weekly` | Friday wrap-up or Monday planning. | Gmail (sent + inbound, full 7-day window), Notion Signals, Notion Transcripts, `_tasks.md`, `_awaiting.md`, `_goals.yaml`, `_index.md`, `_contacts.md`, all active project context files | Weekly review: OKR check, What Got Done, What Didn't, Stale items, Deferred review, Gmail reconciliation (untracked work captured), Systemic issues, Next Week Top 5, What I'm NOT Doing. Full task hygiene applied to all ops files. Auto-runs `/kb-lint`. |
| `/archive` | Inbox archive sweep. | Gmail inbox | Aggregated list of clearly-archivable threads (newsletters, automated notifications) for bulk approval. |
| `/inventory` | Hardware tracking questions. | Google Sheets (inventory spreadsheet: Dashboard, Parameters, Device Order Status tabs), `inventory-monitoring.context.md`, `device-procurement.context.md`, `_awaiting.md` | Inventory report: Network summary, per-site RED/YELLOW/GREEN status, pending orders, recommended actions. Alert email draft if any site is RED. Vendor order draft if requested. |
| `/kb-lint` | KB hygiene check. | `ops/_kb/` topic files, `_kb/_index.md` | Regenerates manifest. Reports orphans, broken refs, frontmatter issues, cross-scope duplicates, stale files. Real drift separated from expected migration drift. |
| `/close` | Done for the day. | Current conversation context (no re-reads), `_kb/_inbox.md`, `_contacts.md`, `_tasks.md`, `_awaiting.md`, `_index.md`, project context files | Session summary: list of files updated and what changed. Gap-fills anything auto-save missed. Ends with "All context persisted. Session safe to close." |

---

## Detailed Breakdown

### `/gm` - Morning Briefing
The heaviest scan. Reads all ops state files, then scans every channel (Gmail inbox, Google Chat, both Slacks, Notion Signals, Calendar) for new activity since last session. On Mondays, uses a 3-day lookback to cover the weekend. Also scans [YOUR NAME]'s sent mail and chat messages to catch work done outside DOCC (nudges, new asks, decisions). Cross-references everything against tracked state. Runs gap detection for orphan messages, silent awaiting items, and stale tasks. For ACTION items where [YOUR NAME] is the relay (not the owner), runs the routing-table lookup inline so the suggested recipient appears alongside the action. Filters through [YOUR ORG UNIT] OKRs. Produces a "Touch Today" list (max 5 projects) and time block suggestions.

### `/followup` - Loop Lifecycle & Context Reconciliation
Two-pass system. **Pass 1:** Takes every active item in `_awaiting.md` and every open Critical/High task and reads every linked source (Gmail, Chat, Slack, Notion) to verify state. Classifies each as CLOSED, NUDGED, STALE, CRITICAL, NO TRACE, or FRESH. **Pass 2:** Scans inbox and outbox across all channels for untracked items — new asks, new tasks, new contacts, decisions made outside DOCC. Accepts optional scope: `/followup staffing`, `/followup [a direct report]`, `/followup 3d`. Use `/followup 1d` for a quick mid-day check, default 7d for weekly reconciliation, `/followup 14d` for a deep sweep (after OOO or before `/weekly`).

### `/queue` - What's On My Plate?
Zero network calls. Reads local files only (`_tasks.md`, `_index.md`, project context files). Shows the full prioritized task list with status badges. Accepts filters: `/queue staffing`, `/queue high`, `/queue [a direct report]`. Fastest command when you just need to orient yourself without waiting for channel scans.

### `/sitrep` - Status Report
Reads all ops state files and spawns the `ops--briefer` agent to draft a report tailored to the specified audience. For [YOUR BOSS]: 5-10 bullet points, headlines first, blockers with solutions. For team: task-oriented, specific, actionable. For a project: comprehensive with sources. Always presented as a draft for review. Never sent without approval.

### `/work` - Autonomous Task Execution
Pulls today's Critical/High tasks, verifies status by reading every linked source (drops anything already resolved), and classifies each by autonomy: 🟢 Green (DOCC executes end-to-end), 🟡 Yellow (DOCC preps, [YOUR NAME] reviews in <2 min), 🔴 Red ([YOUR NAME] only), ⚫ Gray (blocked). Executes Green, preps Yellow with full drafts and recommendations. Email drafts always wait for approval. Also handles ad-hoc draft requests when not tied to a tracked task — for one-offs you can just ask conversationally; voice/recipient/in-thread rules in `ops.md` are always-on.

### `/route` - Router Engine Lookup
Single-topic routing question. Matches against `ops/router-engine/_routing.md` and `_kb/_index.md`, returns the recommended owner with a confidence score (HIGH/MED/LOW) and reasoning. Use when you have one specific question and want to know who handles it.

### `/council` - Strategy Council
Spawns three agents in parallel:
- **Strategist** -- big picture, long-term implications, leverage points
- **Critic** -- challenges assumptions, finds risks, detects biases
- **Researcher** -- evidence, best practices, precedents

Then a **Synthesizer** combines their perspectives into a recommendation with confidence level and decision framework. The council debates; [YOUR NAME] decides. Decision gets logged to the relevant project context file.

### `/meetings` - Meeting Transcript Processing
Searches Notion Signals DB first (efficient, pre-indexed). Only reads full transcript bodies when signals need more context. Extracts decisions, action items, new contacts, and project updates. Routes each finding to the correct file. Flags items that don't match any active project for [YOUR NAME] to classify.

### `/weekly` - Weekly Review & Planning
The broadest sweep and the only mechanism for moving items to Deferred. Starts with an OKR check (mandatory, comes first). Scans full 7-day window of sent mail to catch everything `/gm` missed (archived threads, days without DOCC sessions, timing gaps). Enforces task hygiene: moves completed items, flags overdue 5+ days, caps Critical at 8, archives old completed items, reviews Deferred conditions. Auto-runs `/kb-lint` for KB hygiene. Produces next week's Top 5 Priorities and an explicit "What I'm NOT Doing" list.

### `/archive` - Inbox Archive Sweep
Aggregates clearly-archivable inbox items (newsletters, automated notifications, marketing) for bulk approval. Hygiene only — does not surface action items.

### `/inventory` - Device Inventory Monitor
Reads from Google Sheets (inventory spreadsheet with Dashboard, Parameters, and Device Order Status tabs). Calculates per-site spare ratios against thresholds (GREEN >= 15%, YELLOW >= 8%, RED < 8%). Checks pending vendor orders before recommending new ones. Drafts alert emails if any site is RED. Can draft vendor order emails with `/inventory order`.

### `/kb-lint` - KB Manifest Regenerator + Drift Detector
Regenerates `ops/_kb/_index.md` from frontmatter across all scoped KB files. Detects orphans, broken `related:` links, missing frontmatter, mismatched id/scope, cross-scope duplicates, and stale files. Separates real drift (action required) from expected migration-phase drift. Auto-runs during `/weekly`; can be invoked manually anytime. Use `--triage-inbox` to triage entries in `_kb/_inbox.md` into scoped files.

### `/close` - Session Context Flush
Reviews the full conversation and gap-fills anything auto-save missed. Checks KB inbox, contacts, tasks, awaiting, project index, and all touched project context files. Doesn't re-read files already in context. Outputs a summary of what was updated and confirms "All context persisted. Session safe to close."

---

## How Commands Relate

```
Start of day:     /gm (full scan + plan, includes routing suggestions inline)
                     |
During the day:   /followup 1d (quick mid-day inbox check)
                  /queue (what am I working on?)
                  /work (execute Green / prep Yellow / draft something)
                  /route (who handles X?)
                  /council (big decision)
                  /meetings (process transcripts)
                     |
Check on others:  /followup (who owes me?)
                     |
Reporting:        /sitrep (status update)
                     |
End of week:      /weekly (review + plan next week, auto-runs /kb-lint)
                     |
End of session:   /close (persist everything)
```

---

## Speed vs Depth

| Need | Command | Speed |
|------|---------|-------|
| Just show me my tasks | `/queue` | Instant (local files only) |
| Quick inbox check | `/followup 1d` | Fast (last 24h scan) |
| Who owes me something? | `/followup` | Medium (searches all mail) |
| Full morning picture | `/gm` | Slow (scans everything) |
| Full week review | `/weekly` | Slowest (7-day sweep + hygiene) |

---

## Recommended Workflows

### Catching up after working outside DOCC

If you've been handling emails, chats, and tasks directly (outside DOCC), run these in separate sessions:

```
Session 1:  /followup  →  sweeps all mail + chat, closes loops, updates ops files  →  /close
Session 2:  /gm        →  prioritizes what's left, now aware of what you already handled
```

Why two sessions: `/followup` searches all mail for every awaiting item and fills the context window. Running `/gm` in a fresh session means it reads the updated ops files and gives you an accurate picture of what actually needs attention.

### Other common patterns

```
Quick orient:          /queue                          (instant, local files only)
Mid-day check:         /followup 1d                    (last 24h scan, fast)
Full morning start:    /gm                             (everything, slow)
After a busy day:      /followup → /close → /gm        (two sessions, as above)
End of week:           /weekly                         (broadest sweep)
```

---

## Tips

- **Don't run `/gm` for quick tasks.** If you just need to draft an email or check a task, jump straight to `/work` or `/queue`. `/gm` is for when you want the full picture.
- **`/followup` catches archived replies.** It searches all mail (not just inbox) and reads every linked source on every active loop. This matters because you read and archive emails outside of DOCC.
- **`/council` is for big decisions only.** It spawns multiple agents and takes time. For tactical questions, just ask directly.
- **Auto-save runs continuously.** `/close` is a safety net, not a requirement. But it's good insurance after complex sessions.
- **Everything drafts first, sends never.** No command will send an email or message without your explicit approval. Recipients shown = recipients sent.
- **Commands accept arguments.** `/followup [a direct report]`, `/queue staffing high`, `/sitrep [YOUR BOSS]`, `/inventory order` all narrow scope and save time.
</content>
