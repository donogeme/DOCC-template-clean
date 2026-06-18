---
title: /work - Autonomous Task Execution
type: note
---

# /work - Autonomous Task Execution

Execute Green tasks and prep Yellow tasks. Follows `/gm` (or `/followup` / `/queue`).

## Phase 1: Classify

1. **Read state:** `ops/_tasks.md`, `ops/_awaiting.md`, `ops/_contacts.md`, `ops/_index.md`, `ops/_kb/_index.md` (KB manifest — read first to identify relevant scoped files via Lookup By Project / Lookup By Person), `ops/_kb/people-and-tone/voice.md`.

2. **Pull today's work:** Critical/High tasks that are due today, overdue, or actionable.

   **Verify status before classifying.** For each candidate, open every linked source in the Source field (a task may span multiple: Gmail thread, Chat space, Slack thread, Notion signal). Read the latest 1-2 messages in each.
   - Gmail: `mcp__google__gmail_get_message`
   - Chat: `chat_list_messages`
   - Slack: `slack_thread_replies`
   - Notion: query Signals/Transcripts DB

   If any source shows the task is already done (handoff, third party resolved, [YOUR NAME] replied outside DOCC, meeting decided), mark complete in `_tasks.md` and drop from the queue BEFORE classifying.

3. **Classify by autonomy:**

| Tag | Criteria |
|---|---|
| 🟢 Green | DOCC does the work end-to-end. No decisions, approvals, or personal judgment needed. Emails ALWAYS get [YOUR NAME]'s approval before send. |
| 🟡 Yellow | DOCC does 80%. [YOUR NAME] reviews/decides in <2 min. |
| 🔴 Red | Personal call, strategic decision, relationship judgment, physical presence. |
| ⚫ Gray | Blocked / missing info / wrong timing. |

4. **Present and wait for "go":**

```
## Work Queue

### 🟢 Green (handle now)
1. [Task] - [What I'll do]

### 🟡 Yellow (prep, you finish)
1. [Task] - [What I'll prep] → [What you decide]

### 🔴 Red (you only)
1. [Task] - [Why]

### ⚫ Gray (parked)
1. [Task] - [Blocker]

Say "go" to start, or adjust classifications first.
```

## Phase 2: Execute Green 🟢

For each Green task, complete fully and immediately.

- **Email routing/forwarding:** Draft with brief context. Present for approval. NEVER send directly. Mark complete after send.
- **Tracking file updates:** Update files directly. No approval needed.
- **Research:** Search Gmail/Chat/Drive/Notion. Write findings to project context file or present inline. Mark complete.
- **Factual replies:** Borderline Green/Yellow. Draft for review. NEVER send directly. If any doubt, treat as Yellow.

After each Green: mark complete in `_tasks.md`, update related files (including the twin loop in `_awaiting.md` if the item is double-tracked — see `ops.md` -> Closure Propagation), log in work report.

## Phase 3: Prep Yellow 🟡

For each Yellow, do everything possible without [YOUR NAME]'s input.

- **Email drafts:** Read `ops/_kb/people-and-tone/voice.md` and the relevant scoped KB files (consult `ops/_kb/_index.md` Lookup tables). Read latest 3-5 messages in target thread. Draft full email (To, CC, Subject, Body). Mark what [YOUR NAME] needs to decide. **BEFORE presenting the draft to [YOUR NAME], capture it for the Phase 2A feedback loop (see Draft Capture below).** Then present inline.
- **Research + recommendation:** Do research. Present 2-3 options with tradeoffs. Recommend one with reason.
- **Document prep:** Build the doc. Use `[OPERATOR: ...]` placeholders. Present for review.

Format:
```
### 🟡 [Task]
**What I did:** [summary]
**What you need to do:** [specific 1-2 min action]
**Draft / Options / Document:** [deliverable]
**Recommendation:** [if applicable]
```

### Draft Capture (Phase 2A instrumentation)

For every Yellow **email draft** (only — research/document outputs are not captured in this phase), append one JSON line to `ops/_traces/work-drafts/<YYYY-MM-DD>.jsonl` BEFORE presenting the draft. Capture happens whether or not [YOUR NAME] ultimately approves/edits/rejects it.

Append a single line with this schema:

```json
{"ts": "<ISO 8601 with timezone>", "draft_id": "<YYYYMMDD-HHMMSS-NN>", "task_ref": "<source line/section in _tasks.md or 'ad-hoc' if untracked>", "task_text": "<verbatim task description>", "kb_files_loaded": ["ops/_kb/people-and-tone/voice.md", "..."], "source_threads_read": ["gmail:<thread_id>", "chat:<space_id>"], "recipients": {"to": ["<email>"], "cc": ["<email>"]}, "subject": "<draft subject>", "body": "<full draft body>", "operator_decision_points": ["<what was flagged for the operator>"]}
```

**Rules:**
- One file per day, append-only. Create the file if it doesn't exist.
- `draft_id` is `<YYYYMMDD>-<HHMMSS>-<sequence>` where sequence increments within the same second (use `01`, `02` for multiple drafts in one second).
- Capture happens BEFORE the draft is shown to [YOUR NAME]. Even if [YOUR NAME] rejects it outright, the draft is logged.
- Do NOT log research/recommendation outputs or document prep — only email drafts.
- This file is `.gitignore`'d (local-only). Trace content stays on this machine.

### Inline Revision Capture (Phase 2A instrumentation)

After presenting a Yellow draft, [YOUR NAME] may give feedback to revise it. Detect and capture every revision iteration.

**Detection heuristic — treat the next message as a revision request when ALL of these hold:**
1. A Yellow email draft was presented in the immediately previous turn
2. [YOUR NAME] has not yet approved that draft (no "send it", "looks good", "approved", "ship it")
3. [YOUR NAME]'s message contains revision signals: imperatives about the draft (rewrite, tighten, expand, swap, drop, fix, change, make X), tone/audience hints ("too formal", "too long", "this is to a direct report not [YOUR BOSS]"), or specific recipient/subject changes

**If detection is wrong** ([YOUR NAME] pivoting topics, asking a question, etc.): proceed with the new request normally. Do NOT log a phantom revision.

**When a revision is detected:**
1. Produce a revised draft incorporating the feedback. Re-read `voice.md` and any KB files relevant to the feedback.
2. Append one JSON line to `ops/_traces/feedback/<YYYY-MM-DD>.jsonl` with `event_type: "inline-revision"` (schema below).
3. Present the revised draft to [YOUR NAME]. The cycle can repeat — each revision increments `iteration` and gets its own JSONL line.

**When [YOUR NAME] approves a draft** (any iteration, including the original v1):
1. Append one JSON line with `event_type: "final-approved"` capturing the final body and edit distance from v1.
2. If the draft is then sent ([YOUR NAME] says "send it"), Gmail send proceeds normally with the approved body.

**Schema — inline-revision event:**
```json
{"event_type": "inline-revision", "ts": "<ISO 8601>", "draft_id": "<from work-drafts>", "iteration": <int starting at 1>, "feedback_text": "<verbatim operator message>", "feedback_signals": ["tighten", "audience-mismatch", ...], "revised_recipients": {"to": [...], "cc": [...]}, "revised_subject": "<...>", "revised_body": "<full revised body>", "kb_files_reread": ["ops/_kb/..."]}
```

**Schema — final-approved event:**
```json
{"event_type": "final-approved", "ts": "<ISO 8601>", "draft_id": "<from work-drafts>", "final_iteration": <int — 0 if approved as-is on v1, 1+ if revisions occurred>, "final_recipients": {"to": [...], "cc": [...]}, "final_subject": "<...>", "final_body": "<...>", "edit_distance_from_v1": <Levenshtein int, computed against the original body in work-drafts/>, "approval_phrase": "<verbatim operator approval, e.g. 'send it'>"}
```

**Rules:**
- One feedback file per day at `ops/_traces/feedback/<YYYY-MM-DD>.jsonl`. Append-only. Create if missing.
- `draft_id` MUST match the `draft_id` from `ops/_traces/work-drafts/<date>.jsonl` so iterations link to original.
- `iteration` starts at 1 for the first revision (not 0; 0 is reserved for "approved as-is on v1" in final-approved events).
- Edit distance: compute Levenshtein on raw body text between original draft (from `work-drafts/`) and final body. Report in characters.
- This file is `.gitignore`'d (local-only).

## Phase 4: Red/Gray Summary

```
### 🔴 Still needs you
- [Task]: [context + suggested time block]

### ⚫ Parked
- [Task]: [Blocker + when it might unblock]
```

## Phase 5: Work Report

```
## Work Report

### Completed (🟢)
- [Task] - [What] - [Files updated]

### Ready for Review (🟡)
- [Task] - [Prep] - [What the operator does]

### Remaining (🔴)
- [Task] - [Context]

### Parked (⚫)
- [Task] - [Blocker]

### Files Modified
- [List]
```

## Rules

1. NEVER send emails without explicit approval. Even Green. File updates excepted.
2. Read `ops/_kb/people-and-tone/voice.md` before drafting. No exceptions.
3. Read `ops/_kb/_index.md` before drafting; load relevant scoped files via lookup tables. Apply existing knowledge.
4. Read every linked source (latest 2-3 messages each) before drafting any reply. A task can span Gmail + Chat + Slack + Notion; the live sources are the source of truth, not tracking files.
5. Update tracking as you go. Don't batch.
6. Green needing judgment → reclassify Yellow.
7. Use subagents for parallel independent work (e.g., multiple research lookups).
8. Cite sources. Every fact traces to email/chat/document.
9. Time-box Yellow at 10 min. If longer, flag and ask before proceeding.

## Integration

- `/gm` → classifies → suggests `/work`
- `/work` → executes Green, preps Yellow → [YOUR NAME] handles Red
- `/close` → captures `/work` output
- `/followup` → feeds new tasks into next `/work`
