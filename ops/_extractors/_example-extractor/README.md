---
title: Example extractor — template to copy
type: note
---

# _example-extractor (TEMPLATE — copy me)

This folder is a **template**, not a live extractor. To build a real one:

1. Copy this whole folder to `ops/_extractors/<your-name>/`.
2. Rename and fill in the files described below.
3. Register the new extractor in `ops/_extractors/README.md`.

An extractor "bottles" one recurring message shape from one sender into a deterministic
function, so a scan extracts its facts identically every run and never silently misses it.

---

## The contract

An extractor is a folder with four parts:

```
<name>/
  EXTRACTOR.md         <- frontmatter (match rules, trusted flag, provenance) + notes
  extract.mjs          <- pure function: one envelope in -> structured row | null
  extract.test.mjs     <- fixture test: asserts output shape + non-empty key fields
  fixtures/            <- one redacted real example (gitignored, never leaves disk)
    .gitkeep
```

### 1. `EXTRACTOR.md` frontmatter

```yaml
---
name: example-approval
channel: gmail                      # gmail | gchat | slack | notion
version: 1
trusted: false                      # false until shadow mode proves it
source: agent                       # who/what synthesized it
match:
  sender_includes: alerts@[acme-domain]
  subject_regex: "approval (needed|required)"
provenance:
  synthesized: YYYY-MM-DD
  session: "short note on where this came from"
  from_message: "<source-ref of the message it was hand-parsed from>"
---
```

### 2. What fields it pulls

This example matches an "approval needed" notification from `alerts@[acme-domain]`
and pulls these fields from the subject + body:

- `entity` — the org/account the request is for
- `requester` — who filed the request
- `request_subject` — what is being requested
- `reason` — the stated justification (may be truncated)
- `amounts` — any dollar figures found, as a list

### 3. Output shape

`extract.mjs` returns exactly this shape on a match, or `null` on anything it
doesn't recognize (never guess — unrecognized → residue → the model reads it the old way):

```json
{
  "type": "approval_request",
  "fields": {
    "entity": "Acme Holdings",
    "requester": "Riley Example",
    "request_subject": "Software Subscription",
    "reason": "Hit plan limits, need it for the summer term...",
    "amounts": ["$10,000.00 monthly", "$5,000.00 monthly"]
  },
  "confidence": 1.0,
  "source_ref": "gmail:<message-id>"
}
```

---

## Failure behavior (required)

- Unknown subject/sender shape → `extract()` returns `null` → item goes to residue.
  The extractor **never guesses**.
- Sender redesigns the template → `extract.test.mjs` fails against the stored fixture →
  surfaced as drift. Loud, not silent.

## Fixture policy (required)

- Capture ONE real example into `fixtures/`, redacted at capture time: replace real
  names, scrub token URLs / business ids / emails.
- `fixtures/` is gitignored on top of that (two layers). Real examples never enter git.

## Status lifecycle

`trusted: false` → run in shadow mode alongside the normal scan, compare outputs →
only flip to `trusted: true` (so its rows feed triage directly) after it proves out,
with explicit sign-off.
