---
title: /gm - Morning Briefing
type: note
---

# /gm - Morning Briefing

Run the morning briefing protocol.

## Steps

0. **Lookback window:**
   - Monday: `$LOOKBACK = newer_than:3d`, `$SLACK_AFTER = after:[last Friday's date]`. Note "Weekend catch-up mode" in header.
   - Other weekdays: `$LOOKBACK = newer_than:1d`, `$SLACK_AFTER = after:yesterday`.

0.5. **Verbatim email archive (recall layer) — OPTIONAL.** Skip this step unless you have set up an email-ingestion helper (a script that writes verbatim mail to `raw/emails/`) and, optionally, a deep-retrieval store. This template does not ship one — the briefing works fine without it, straight off the MCP scans below. If you DO have such a helper, run it in the background at the very start so it doesn't block the scans, using the same lookback as step 0:
   - Monday: `--after <YYYY/MM/DD = 3 days before today>` (weekend catch-up)
   - Other weekdays: `--after <YYYY/MM/DD = 1 day before today>`

   ```
   # Example, if you have one — adjust to your tool:
   # python tools/ingest_emails.py --after <YYYY/MM/DD per the rule above>
   ```

   Such a helper should write one verbatim file per thread to `raw/emails/`, skipping anything already ingested (dedup by message_id on disk), and feed only the header's "Written (new)" count. Matching step 0's window keeps the archive layer in lockstep with the triage scan; skip-existing makes any overlap cost-free. This is the full-text archive layer — independent of the summary-row triage below.

**Fetch in parallel (steps 1-3).** The state-file reads, inbound scans, and outbound scans below are mutually independent — none consumes another's output. Issue all of them as a single parallel batch of tool calls, then do the triage/cross-reference reasoning (steps 4+) once everything is back. Do not run them one at a time.

1. **Read state:** `ops/_index.md`, `ops/_tasks.md`, `ops/_awaiting.md`, `ops/_goals.yaml`, `ops/_contacts.md`, `ops/router-engine/_routing.md`.
   - **Mon + Fri only — Critical-count check:** Count the Critical tasks in `_tasks.md`. The target is 8 (soft, not a cap). If >8, add a **Critical Trim** block to the briefing: list the Critical items and recommend which to demote/complete/defer back toward 8 for focus — [YOUR NAME] decides. If ≤8, note "Critical at N — no trim needed." Never auto-demote or block a task. (Other weekdays: skip this check.)

2. **Scan inbound:**
   - Gmail: `in:inbox $LOOKBACK`
   - Chat: Recent messages in spaces from `ops/_google-chat-spaces.md`
   - Slack Workspace 1: `[SLACK_WORKSPACE_1_BOT_ID] $SLACK_AFTER`
   - Slack Workspace 2: `[SLACK_WORKSPACE_2_BOT_ID] $SLACK_AFTER`
   - Notion Signals: Recent within lookback
   - Calendar: Today's events

3. **Scan [YOUR NAME]'s outbound:**
   - Gmail sent: `from:me $LOOKBACK`
   - Chat: Filter each space by [YOUR NAME]'s user ID `[YOUR GOOGLE USER ID]`
   - Slack Workspace 1: `from:[SLACK_WORKSPACE_1_BOT_ID] $SLACK_AFTER`
   - Slack Workspace 2: `from:[SLACK_WORKSPACE_2_BOT_ID] $SLACK_AFTER`
   - For each, cross-reference against `_awaiting.md` (nudge / new ask), `_tasks.md` (progress), `_contacts.md` (new person), `_index.md` (project link)
   - Surface as **Out-of-Band Activity**

4. **Apply Message Triage Rules** (below). Classify each item into ACTION:[YOUR NAME] / ACTION:ROUTE / LOOP UPDATE / FYI / IGNORE. For every ACTION:ROUTE item ([YOUR NAME] is the relay, someone else has the answer), run the routing-table lookup inline (see Inline Routing Lookup section below) and surface the suggested recipient with confidence score alongside the action.

5. **Gap detection.** Only open linked sources for items that are actual flag *candidates* — an awaiting item or task with no fresh activity in the step-2/3 scan. Items that already lit up in the scan are confirmed-live; do not re-open their sources. For each candidate, READ every linked source before flagging it silent or stale (Source field can list one or many: Gmail thread, Chat space message, Slack thread, Notion signal/meeting). Open the candidate's sources in parallel:
   - Gmail: `mcp__google__gmail_get_message`
   - Chat: `chat_list_messages` on the space
   - Slack: `slack_thread_replies`
   - Notion: query Signals/Transcripts DB

   Then evaluate:
   - **Orphan sent messages:** Outbound that doesn't match a tracked item.
   - **Silent awaiting items:** 3+ days where ALL linked sources show no activity.
   - **Stale tasks:** In-progress tasks where all linked sources show no movement for 3+ days.
   - **Resolved-but-untracked:** If any source shows the loop already closed, mark CLOSED instead of flagging silent — close the twin row in the other tracking file (`_awaiting.md` <-> `_tasks.md`) in the same pass, then move the struck rows to `ops/_archive/`. See `ops.md` -> Closure Propagation + Archive Routing.
   - **Open forks:** If the source or project file shows [YOUR NAME] named 2+ paths and never committed to one, AND no safe default exists, surface it as a `FORK:` choice. See Open-Fork Detection under Loop Matching. (TRIAL — 2026-06-08.)
   - **Unconnected contact activity:** Messages from a contact not linked to any active project/awaiting.

6. **Produce the briefing:**

```
## Good Morning, [YOUR NAME] - [Date]

### Action Required (You Decide / Act)
- [ACTION:[YOUR NAME] items — From, subject, why action, project link]

### Action Required (Route to Owner)
- [ACTION:ROUTE items — From, subject, what they need]
  -> ROUTE TO: [Name] ([email]) — [reason] (Confidence: HIGH/MED/LOW)
  [If hard-block]: "Requires your direct review — [reason]"
  [If routing entry stale (>30d)]: "Routing entry last verified [date] — confirm"

### Loop Updates
- [LOOP UPDATE items — flag which loop is closing]

### Out-of-Band Activity
- [What you did outside DOCC]
- [Or: "No outbound activity detected"]

### FYI / Awareness
- [FYI items — skim only]

### Today's Calendar
- [Time]: [Event]
- [Available blocks for deep work]

### Must Do Today (Classified by Autonomy)
**🟢 Green:** [task] — [est time] — [what DOCC will do]
**🟡 Yellow:** [task] — [est time] — [DOCC preps] — [[YOUR NAME] decides]
**🔴 Red:** [task] — [est time] — [why only [YOUR NAME]]
**⚫ Gray:** [task] — [blocker]

### People Waiting on You
- [Person]: [What] — [How long]

### You're Waiting On
- [Person]: [What] — [Days] — [fresh/stale/critical]

### Critical Trim (Mon + Fri only, show only if Critical > 8)
- Critical at [N]. Suggest trimming to ~8 for focus:
  - Demote/defer: [item] — [why it can wait]
  - [Or "Critical at N — no trim needed" when ≤ 8]

### Gaps & Reconciliation
- [Orphans, silent items, stale tasks — or "All clear"]

### This Week's Priorities (Goal-Aligned)
- [OBJ-X]: [What advances this]

### Suggested Time Blocks
- [Time range]: [Activity]
```

After classification, remind: "Run `/work` to execute Green and prep Yellow tasks."

---

## Task Autonomy Classification

| Tag | Criteria | Examples |
|---|---|---|
| 🟢 Green | DOCC does the work end-to-end. No decisions/approvals/personal judgment needed. Emails ALWAYS get [YOUR NAME]'s approval before send. | Routing, tracking updates, pre-approved follow-ups, factual research, factual replies |
| 🟡 Yellow | DOCC does 80%. [YOUR NAME] reviews/decides in <2 min. | Drafts needing tone/judgment, options for [YOUR NAME] to pick, research-then-decide |
| 🔴 Red | Personal call, strategic decision, relationship judgment, physical presence. | Meetings, hiring decisions, hard conversations, large spend approvals |
| ⚫ Gray | Not actionable today. Blocked/waiting/parked. | Waiting on reply, missing data, depends on another task |

Heuristics:
- Draft+send autonomously → 🟢 only for routine routing/tracking/factual replies
- Draft for review → 🟡
- [YOUR NAME]'s judgment/relationships/presence → 🔴
- Dependency unmet → ⚫
- When in doubt between Green and Yellow, pick Yellow.
- NEVER Green for substantive emails. Routing/forwarding only.

---

## Message Triage Rules

### Sender Priority

- **Tier 1 (always surface):** [YOUR BOSS]; [YOUR DIRECT REPORTS]; contacts on active HIGH-urgency projects
- **Tier 2 (surface if action signal):** Anyone in `_contacts.md`; anyone on an active project
- **Tier 3 (FYI count only):** Automated/system/newsletter; not in contacts and not project-linked

### Action Signals

**Strong (→ ACTION):**
- Direct questions to [YOUR NAME] (@[YOUR NAME], "[YOUR NAME], can you...")
- Explicit requests ("need your approval", "can you review", "waiting on you")
- Deadlines ("by EOD", "ASAP", "blocker")
- Decisions ("should we", "go/no-go", "approve")
- Someone blocked, [YOUR NAME] unblocks

**Moderate (→ ACTION if Tier 1-2, else FYI):**
- Status updates implying next steps
- Meeting follow-ups with [YOUR NAME] action items
- Replies in threads [YOUR NAME] started

**None (→ FYI):**
- Broadcasts, company-wide
- CC'd status where [YOUR NAME] isn't owner
- Group chat without mention
- Automated notifications

### Loop Matching

For each inbound message, check if sender appears in `_awaiting.md` Active. If yes → **LOOP UPDATE**, flag which item, include the original ask.

When deciding whether to flag an awaiting item as silent (3+ days), open every linked source and read the latest message. Don't rely on inbox sender match alone — handoffs, third-party replies, chat resolutions, and meeting-decided closures may have resolved it without producing an inbox match.

`/gm` only checks inbox. For archived responses, run `/followup`.

#### Open-Fork Detection (TRIAL — added 2026-06-08, revert per changelog if noisy)

A loop is "closeable" only one way, but some loops carry an **unresolved fork**: a point where [YOUR NAME] (or the source) offered or considered 2+ paths and never committed to one. These don't read as "stale" (there may be recent activity) and they don't read as "closeable" (the decision is still open) — so default Loop Matching misses them. Surface them as a **choice**, not a status line.

A loop has an open fork when BOTH hold:
1. The linked source or the project `{project}.context.md` shows [YOUR NAME] named multiple paths ("we could do X or tell them to do Y", "case-by-case OR route to Z"), or left an explicit either/or unanswered.
2. DOCC cannot safely pick a default — a project constraint, veto, or guardrail makes one path outward-facing (drafts/sends), org-sensitive, or genuinely [YOUR NAME]'s call (per the Clarification Protocol and the `AskUserQuestion` "answer changes what I do next" bar).

When both hold, in the **Loop Updates** section render it as `FORK:` with the open question and the named paths, then ask via `AskUserQuestion` so the answer drives the next action (draft, redirect, or park). If only one path exists, or a default is safe, do NOT use a fork — handle it as a normal action/loop item. Keep this rare: a fork is for genuine un-pickable decisions, not for every multi-step item.

### Project Relevance

- HIGH-urgency project mention → boost one tier
- No project/OKR connection → deprioritize, note "not aligned to a [YOUR ORG UNIT] OKR"

### TO vs CC

- **TO:** Full action signal detection
- **CC:** Default FYI unless strong signals in body

### ACTION:[YOUR NAME] vs ACTION:ROUTE

- **ACTION:[YOUR NAME]** — [YOUR NAME] unblocks with his own knowledge/decision. Decisions, approvals, SME questions, people management, anything from [YOUR BOSS], hard-block topics.
- **ACTION:ROUTE** — [YOUR NAME] unblocks by routing. Information-seeking ("Do we have...", "Where can I find...", "Who handles..."), data/artifacts in systems [YOUR NAME] doesn't own, intros/connections, vendor/team questions where [YOUR NAME] knows the owner.
- **Ambiguous:** Default to ACTION:[YOUR NAME].

### Hard Blocks (always reclassify ACTION:[YOUR NAME], no routing suggestion)

- Requests from [YOUR BOSS] or above
- Legal/compliance (FERPA, contracts, litigation)
- Personnel/HR (performance, comp, hiring decisions)
- Financial approvals (spend, insurance binding)
- Cross-BU organizational boundary
- Recently departed employees with unclear ownership

---

## Inline Routing Lookup (for ACTION:ROUTE items)

For every item classified ACTION:ROUTE, run the routing lookup:

1. **Match** `ops/router-engine/_routing.md` by keyword/topic.
2. **Check sensitivity** and Last Verified date (flag if >30 days).
3. **Score confidence:**
   - Exact routing match: +40
   - Multiple keyword signals same domain: +20
   - Contact role matches topic: +15
   - KB has relevant guidance: +15
   - Verified <30 days: +10
   - Multiple confirming sources: +10
   - Domain overlap (multiple owners): -25
   - Sensitive area (legal, finance, personnel): -15
   - Owner recently changed roles: -20
   - Ambiguous or multi-part: -15
4. **Cross-reference Notion Signals** for the topic. If a recent meeting (last 14 days) discussed it, surface inline: "FYI: discussed in [meeting] [date] — context may inform the routing."
5. **Surface inline** in the Action Required (Route to Owner) section with:
   - **HIGH (85%+):** "Route to [Person] ([email]) because [reason]."
   - **MEDIUM (60-84%):** "Options: [A] (X%) or [B] (Y%). Recommendation: [A] because [reason]."
   - **LOW (<60%):** "No confident match. Topic: [X]. Who should handle this?"
6. **Log routing:** When [YOUR NAME] confirms or corrects, append to Correction Log in `ops/router-engine/_routing.md`: date, topic, suggested route, actual route (if corrected), reason. If corrected, update the routing table entry immediately.

---

## Triage Output Format

**ACTION REQUIRED (You Decide / Act)** — ACTION:[YOUR NAME] items. Sender, subject, why action, project link.

**ACTION REQUIRED (Route to Owner)** — ACTION:ROUTE items. Sender, subject, what they need, suggested recipient with confidence (HIGH/MED/LOW), reasoning. Hard-block items get reclassified to ACTION:[YOUR NAME] with note.

**LOOP UPDATES** — Who responded, original ask, response, can it close?

**FYI** — Aggregate count ("12 FYI: 3 announcements, 4 chat mentions, 5 automated"). List individual only for Tier 1.

**IGNORE** — Aggregate count only ("8 automated, 3 newsletters, 2 calendar reminders").

---

## Notes

- 2-minute scannable briefing. Lead with immediate action.
- Flag anything blocking other people first.
- Overloaded calendar → say so explicitly.
- When in doubt, classify as ACTION.
- Ambiguous? Include with note: "Unclear if this needs action — [reason]"
