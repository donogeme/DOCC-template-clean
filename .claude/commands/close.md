---
title: /close - Session Context Flush
type: note
---

# /close - Session Context Flush

Persist session learnings into context files. Work from session memory — don't re-read files already in context.

For each category, capture anything new. Skip silently if nothing changed.

### 1. Knowledge Base (`ops/_kb/_inbox.md` for new content; scoped files for direct edits)
- New domain knowledge (process rules, vendor info, system behavior, decision patterns)?
- Existing knowledge corrected or refined?
- Default: append to `ops/_kb/_inbox.md` (triaged weekly via `/kb-lint --triage-inbox`).
- If clearly belongs to one scoped file (e.g., new vendor pricing tier → `ops/_kb/procurement/acme.md`): edit directly with full source citation.

### 2. Contacts (`ops/_contacts.md`)
- New people mentioned?
- Existing contact role/project/context changed?

### 3. Tasks (`ops/_tasks.md`)
- New action items from emails, decisions, conversations?
- Existing tasks completed or changed?
- Capture owner, due date, project, source(s). A task can span multiple sources (Gmail + Chat + Slack + Notion) — list them all.

### 4. Awaiting (`ops/_awaiting.md`)
- Did [YOUR NAME] ask anyone for something (email, chat, verbal)?
- Anyone respond to an open loop?
- Add new, close resolved.
- **Always capture every linked source in the Source field.** A loop can span multiple: Gmail thread ID(s), Google Chat space + message ID, Slack channel/thread, Notion meeting/signal ID. List them all. Future `/followup`, `/gm`, `/weekly` runs need every source to verify state — missing one means a resolution may go undetected.
- **Closure propagation:** when you close a loop here, grep `_tasks.md` for the twin row (same topic / person / ticket) and strike it too — and vice versa when you complete a task. The two files track the same items from two sides and must agree. See `ops.md` → Closure Propagation.

### 5. Project Index (`ops/_index.md`)
- Any project status or urgency change?

### 6. Project Context (`ops/{project}/{project}.context.md`)
- New decisions → Key Decisions table with source
- State changes → Current State section
- New open questions
- New sources → Sources table

### 6.5 Raw Transcripts (`raw/transcripts/`)

If `/meetings` ran this session and wrote new or changed files under `raw/transcripts/`:

1. `git status --short raw/transcripts/` — list staged + unstaged changes in this directory only.
2. If nothing changed → skip silently.
3. If there are changes:
   - `git add raw/transcripts/`
   - Show [YOUR NAME] the staged file list and a proposed commit message:
     - 1 file: `Ingest transcript: <slug>`
     - 2–10 files: `Ingest <N> transcripts (<earliest date>..<latest date>)`
     - 10+ files (backfill): `Backfill <N> raw transcripts (<earliest date>..<latest date>)`
   - Wait for "yes" / "send it" / equivalent. Then `git commit` and `git push`.
   - Do NOT bundle other working-tree changes into this commit. Only `raw/transcripts/` paths.

### 7. Draft Feedback (Phase 2A — `ops/_traces/feedback/<YYYY-MM-DD>.jsonl`)

Only run this step if `/work` ran today AND any drafts were captured to `ops/_traces/work-drafts/<YYYY-MM-DD>.jsonl`. Otherwise skip silently.

**Prompt [YOUR NAME] ONCE at session end:**

```
Quick draft feedback check — anything you edited or that was off about today's drafts?

Today's drafts:
- <draft_id>: <subject>, to <recipient>
- ...

(Reply with notes, "nothing notable", or just press enter to skip.)
```

**Capture rules:**

- **[YOUR NAME] says "nothing notable" or skips:** append ONE summary record per draft from today's `work-drafts/`:
  ```json
  {"event_type": "session-end", "ts": "<ISO>", "draft_id": "<id>", "freeform_note": null, "skipped": true}
  ```
- **[YOUR NAME] provides feedback:** for each draft mentioned, append:
  ```json
  {"event_type": "session-end", "ts": "<ISO>", "draft_id": "<id>", "freeform_note": "<verbatim operator text>", "skipped": false, "implied_kb_target": "<best-guess scope/file or null>"}
  ```
- **Implied KB target:** Best-guess pointer to which `ops/_kb/people-and-tone/` file the feedback might update (`voice`, `audience-tone-boss`, `communication-patterns`, or null). Used by `/feedback-triage` later. NOT authoritative — [YOUR NAME] confirms during triage.
- One file per day. Append-only. `.gitignore`'d.
- This step happens AFTER all other `/close` steps so it doesn't block context persistence if [YOUR NAME] is in a hurry.

**If `/work` did not run today:** skip step 7 entirely. No prompt, no log entries.

## Output

```
## Session Saved

**Updated:**
- [file]: [what changed]

**No changes needed:**
- [categories with nothing new]

All context persisted. Session safe to close.
```

End every output with "All context persisted. Session safe to close." as the final line.
