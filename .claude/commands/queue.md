---
title: "/queue - What's On My Plate?"
type: note
---

# /queue - What's On My Plate?

Prioritized view of [YOUR NAME]'s task list. No broad channel scanning.

$ARGUMENTS optionally filters:
- Project: `/queue staffing`
- Priority: `/queue high`
- Owner: `/queue [direct-report]`
- Combine: `/queue staffing high`

## Steps

1. **Read:** `ops/_tasks.md`, `ops/_index.md`. If filtering by project, also that project's `{project-name}.context.md`.

2. **Apply filters** (project / priority / owner). No filter = everything by priority.

3. **Annotate each task:**
   - **OVERDUE** — past due
   - **DUE TODAY**
   - **BLOCKED** — status mentions a blocker
   - **WAITING** — depends on someone (cross-ref `_awaiting.md`)
   - **READY** — no blockers, actionable
   - **STALE** — in-progress 5+ days, no update

   **Before flagging STALE or WAITING, read every linked source** in the Source field. A task may span multiple sources (Gmail thread, Chat space, Slack thread, Notion signal). Tools: Gmail `mcp__google__gmail_get_message`, Chat `chat_list_messages`, Slack `slack_thread_replies`, Notion DB query. If any source shows recent movement (handoff, third-party reply, [YOUR NAME]'s outbound, meeting decision), reclassify and update the task notes.

4. **Classify READY tasks by autonomy** (same as `/gm`): 🟢 Green / 🟡 Yellow / 🔴 Red. BLOCKED/WAITING/STALE are implicitly ⚫ Gray.

5. **Produce the queue:**

```
## Your Queue - [Date]
[Showing: filter or "All tasks"]

### Critical ([N])
- [STATUS] [🟢/🟡/🔴] [Task] - [Project] - Due [date] - [Next action]

### High ([N])
...

### Medium ([N])
...

### Low ([N])
...

### Deferred ([N] - parked)
- [Task] - [Why] - [Revisit when]

---
Summary: [N] total | [N] overdue | [N] ready | [N] blocked/waiting
Workable: [N] 🟢 | [N] 🟡 | [N] 🔴
Run `/work` to execute.
```

6. **Close with:** "Reprioritize? Mark complete? Drill into a task? Or `/work`?"

## What This Does

- Targeted reads of every linked source on each Critical/High task (Gmail thread, Chat, Slack, Notion) to verify status. NOT a broad inbox/outbox scan.

## What This Doesn't Do

- Broad channel scanning (`/gm`, `/followup`)
- New task discovery from channels
- Outbound reconciliation (`/followup`, `/weekly`)
- OKR check (`/gm`, `/weekly`)

## Output Rules

- One line per task: status badge, name, project, due, next action
- Skip empty sections
- Deferred collapsed by default (count + "/queue deferred to expand"); expand if filtered
- Recently Completed never shown
- Empty filter result: "No [filter] tasks found."
- Status badges in caps: [OVERDUE], [DUE TODAY], [BLOCKED], [WAITING], [READY], [STALE]
