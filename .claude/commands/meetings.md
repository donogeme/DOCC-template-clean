---
title: /meetings - Meeting Transcript Processing
type: note
---

# /meetings - Meeting Transcript Processing

Process recent Notion meeting transcripts into decisions, action items, and contacts. Also writes verbatim raw transcripts to `raw/transcripts/` for gbrain ingestion.

$ARGUMENTS:
- (none) — default: last 7 days, full mode (raw + extraction + recap drafts)
- `<date range>` or `<meeting name>` — narrow the window
- `raw-only` — write raw transcripts only, skip extraction
- `backfill` — walk entire Notion Transcripts DB, raw-only, idempotent (safe to re-run)
- `no-recap` — full extraction but skip the recap-email draft step
- `test <Notion page id or title fragment>` — process exactly ONE transcript end-to-end. Writes the file but pauses BEFORE writing so [YOUR NAME] can review the slug + frontmatter + first lines. Use this for the first-run dry test.

## Steps

1. **Read state:** `ops/_index.md`, `ops/_contacts.md` (skip in `backfill` and `raw-only` modes — extraction isn't running).

2. **Pick the agent mode based on $ARGUMENTS:**
   - `backfill` → `mode: backfill`
   - `raw-only` → `mode: raw-only`
   - `test <id>` → `mode: full`, scope to one transcript, and PAUSE before writing the raw file to show [YOUR NAME] the proposed slug + frontmatter + first 30 lines of body. [YOUR NAME] confirms before write proceeds.
   - default → `mode: full`

3. **Spawn `ops--processor`:**
   - In `mode: full`: search Notion Signals DB, identify unprocessed meetings, write raw files (Step 3.5), extract decisions/actions/contacts, route to project files.
   - In `mode: raw-only`: write raw files only.
   - In `mode: backfill`: walk full Transcripts DB, write raw files only, checkpoint every 50.
   - The agent does NOT git-add, commit, or push. It only writes files and reports the manifest at the end.

4. **Present (skip in `raw-only` and `backfill` modes — agent's manifest is the output):**

```
## Meeting Processing Report - [Date]

### Meetings Processed
1. [Meeting] - [Date] - [Participants]
   - Decisions: [N]
   - Action items: [N]
   - New contacts: [N]

### Decisions Extracted
| Decision | Who Decided | Meeting | Filed To |
|---|---|---|---|

### Action Items
| Action | Owner | Deadline | Meeting | Filed To |
|---|---|---|---|---|

### New Contacts
| Person | Role | Context | From Meeting |
|---|---|---|---|

### Unmatched Items
[Items not mapping to known projects]

### Recap Email Drafts
[One block per qualifying meeting — see Step 4.5. Omit this section in `no-recap` mode.]

**[Meeting] - [Date]**
- **To:** [verified participant emails]
- **Subject:** Recap - [meeting topic] - [date]
- **Body:**
  > Quick recap from today's meeting so we're all aligned.
  >
  > Decisions made:
  > - [bullets]
  >
  > Action items and owners:
  > - [name + deadline per item]
  >
  > Open questions:
  > - [anything unresolved]
  >
  > Flag anything that looks off and I'll update.
- **Needs verification:** [participants still unresolved after the 4-source pass — listed, never guessed into To]
- **Contacts to add/update:** [recap participants not yet in `_contacts.md` — name, role-or-TBD, resolved email OR "Email not in source"]

### Files Updated
- [List]
```

4.5. **Build recap email drafts (full mode only; skip in `no-recap`, `raw-only`, `backfill`):**

   The Meeting Recap Email Habit (`concepts/meeting-recap-email`, personal-brain): send a curated recap after every meeting that involves a decision, commitment, handoff, or deadline. Locks in your version of events, makes silence = agreement, builds a paper trail.

   - **Read [`ops/_kb/people-and-tone/voice.md`](../../ops/_kb/people-and-tone/voice.md) FIRST** (required, not optional). Apply every rule: no em dashes, no "happy to get on a call" closers, direct and clear.
   - **Qualify a meeting** when BOTH hold:
     1. [YOUR NAME] was an **active participant** (named as attendee/speaker — e.g. appears in `top_talkers` or the participant list), and
     2. it has at least one **decision, commitment, handoff, or deadline** (i.e. at least one extracted decision OR action item OR open question). If there's genuinely nothing to recap, skip it.
   - **Do NOT check meeting-transcription-tool overlap.** Draft the recap regardless of whether the meeting-transcription tool already auto-sent one.
   - **Resolve recipients — per participant, walk this source order and STOP at the first verified hit. NEVER fabricate an address or extrapolate from a domain pattern** (see `ops.md` Email Rules + memory):
     1. `_contacts.md` — grep the participant's name (and phonetically-similar known names — ASR misrecognitions are common).
     2. The meeting's **calendar event attendees** (`calendar_list_events` / `calendar_get_event` around the meeting date) — attendee emails are authoritative. This is the highest-yield source for meeting-transcription-tool meetings where the transcript only has display names.
     3. **Notion People DB** record for that person.
     4. **Gmail** From/To headers on a real prior thread with that person (`gmail_search_threads`).
     A participant still unresolved after all four goes under **Needs verification**, NOT into the To line. If two sources give different addresses, ask [YOUR NAME].
   - **Write resolved + new participants back to `_contacts.md`** (this is what shrinks the verification list over time). For each recap participant not already a row:
     - **Email found** in steps 2-4 → add the row with the verified address and cite the source (e.g. "verified via calendar invite, [date]"), matching the existing format.
     - **Email NOT found** → still add/propose the row with **"Email not in source"** in Notes (never a guess), role "TBD" if unknown, context "Participant in [meeting], [date]". Tracking the person now means a future meeting resolves them faster.
     - This merges with the existing New Contacts extraction (Step 6) — don't double-add; reconcile against rows the processor already proposed.
   - **Body** follows the habit template exactly (Decisions made / Action items and owners / Open questions / "Flag anything that looks off and I'll update."), populated from THIS meeting's extracted items. Every line traces to the transcript — no invented decisions or owners.
   - These are **new emails to participants**, not replies to the meeting-transcription tool report thread (no `threadId`).
   - **The recap and the tracking files come from ONE extraction.** The decisions, action items, and open questions you pull for the recap body are the SAME set Step 6 routes into `_tasks.md`, `_awaiting.md`, and project files. Extract once, use for both, so the recap a participant receives and DOCC's internal tracking never diverge. Do not send a recap whose commitments aren't also being written to the files.

5. **For unmatched items (full mode only):** "These don't match any active project. Create a new project, or file specifically?"

6. **Update files (full mode only) — route the Step 4.5 extraction (decisions / action items / open questions) into the tracking files. This runs for every qualifying meeting, recap or not:**
   - **Decisions** → relevant `{project-name}.context.md` Key Decisions table + Sources entry. If the meeting meets the promotion threshold in `ops.md` (Project Promotion) and no project file exists, CREATE one; otherwise UPDATE the existing file. Respect the WIP limit — if creating would push active projects over target, file under the closest existing project and flag it instead.
   - **Action items** → `_tasks.md`, in the correct priority tier, with owner + due date (TBD if unstated) + source meeting. Reconcile against existing rows so a commitment isn't double-logged.
   - **Open asks / loops** → `_awaiting.md`. Any recap action item or open question where [YOUR NAME] is waiting on someone (including an attendee's own commitment back to [YOUR NAME]) becomes a loop. New asks [YOUR NAME] made in the meeting go to Fresh.
   - **New contacts** → `_contacts.md` (includes recap participants resolved/proposed in Step 4.5 — reconcile so a person is added once, with the verified email if the resolution pass found one)
   - **Processed transcripts** → Sources tables
   - **Closure propagation:** if a meeting resolves or supersedes an open item, close it in BOTH `_tasks.md` and `_awaiting.md` — grep the other file for the twin row and strike it with a matching note. A meeting that decides something often closes a loop the email thread never showed. See `ops.md` -> Closure Propagation.

7. **Recap approval (full mode only, if any recap drafts were built):** Recaps are presented inline only. **Nothing is sent or written to Gmail until [YOUR NAME] approves each one.**
   - Per recap, [YOUR NAME] says **"send it"** → `gmail_send_message` to the verified To list (recipients shown = recipients sent; no additions), or **"draft it"** → `gmail_create_draft` (unsent, lands in Gmail drafts).
   - A recap with unresolved recipients under **Needs verification** is NOT sendable as-is. Get the verified address from [YOUR NAME] first, or send only to the verified subset he confirms.
   - Never batch-send. One explicit approval per recap.

## Rules

- Search Signals DB first (efficient). Only read full transcripts when needed.
- Every extracted item cites the source meeting.
- Don't assume action item deadlines if not stated.
- Unclear role → add contact with "TBD" role.
- Flag topics that look important but don't connect to [YOUR ORG UNIT] goals.
- **Recap drafts: draft-only, never auto-send.** Resolve recipients from `_contacts.md`; never fabricate or domain-extrapolate an address. Apply voice (no em dashes, no call-offer closers). Body traces to the transcript — no invented decisions/owners. See Step 4.5.
