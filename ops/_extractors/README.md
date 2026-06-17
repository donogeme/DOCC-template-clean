---
title: Extractors — deterministic signal extraction for scans
type: note
---

# Extractors

A deterministic signal-extraction framework that "bottles" recurring email/message shapes so scans never silently miss them.

## The idea in plain English

By default, scans are entirely hand-carried: the model fetches the mail, reads every message fresh, and interprets it from scratch every run. That works, but hands occasionally fetch fewer messages than exist (Gmail/Chat APIs truncate) and interpret the same email slightly differently on different days.

Two fixes, both here:

1. **A machine does the fetching.** A deterministic puller pulls a time window of mail — pagination walked to exhaustion, same output for same input, exact counts. It can't get lazy or skip a mailbox.
2. **Recipes handle the regulars.** Most templated senders (billing tools, ticketing systems, digest services...) send the same shapes over and over. The first time the model hand-parses a shape correctly, you "bottle" what it did as a small pure function with a saved (redacted) example and a self-test. From then on the recipe extracts the facts instantly and identically, and the model spends its attention only on the genuinely new stuff (the "residue").

## Why (not token savings)

The wins are:
- **Completeness** — a script can't truncate or skip. The expensive failure mode is a missed loop, not a long run.
- **Loud failure** — if a vendor redesigns their emails, the recipe's test fails visibly instead of the signal silently matching nothing.
- **Concentrated judgment** — the model triages the residue, which is where judgment actually matters.

## Layout

```
ops/_extractors/
  README.md                  <- this file
  _residue-tally.jsonl       <- append-only log of unrecognized shapes (gitignored)
  _example-extractor/        <- copy this folder to start a new extractor
  <name>/
    EXTRACTOR.md             <- frontmatter: match rules, trusted flag, provenance + why
    extract.mjs              <- pure function: item in -> structured row | null
    extract.test.mjs         <- fixture test (shape + non-empty fields)
    fixtures/                <- redacted real examples (gitignored, never leave disk)
```

Run the pipeline:
```
node tools/pullers/pull-all.mjs --window 1d | node tools/extract.mjs
```
All channels, parallel, per-channel error isolation. Single channels: `pull-gmail.mjs --window 1d`, `pull-gchat.mjs --window 1d`, etc. All emit the same normalized envelope; `extract.mjs` accepts a single envelope or the combined document.

Run one extractor's tests:
```
node --test ops/_extractors/<name>/extract.test.mjs
```

## Iron rules

1. **Only bottle what demonstrably worked.** An extractor is synthesized from a message the model hand-parsed correctly in-session (provenance recorded in EXTRACTOR.md), or from a shape the residue tally proved recurring.
2. **Never guess.** Parse failure or low confidence → `extract()` returns `null` → the item goes to residue and the model reads it the old way. This is the never-make-up-information guardrail, in code.
3. **Every extractor ships with a fixture + test.** Shape AND non-empty key fields. Template drift = loud test failure.
4. **Fixtures are redacted at capture AND gitignored.** Two layers: names are replaced, token URLs scrubbed; the directory never enters git regardless.
5. **`trusted: false` until shadow mode proves it.** New extractors run alongside the normal model scan and get compared, not believed. Flipping to `trusted: true` is your call.
6. **Puller errors never block.** Non-zero exit → the scan falls back to the model-driven sweep, with a one-line note. Never block the whole workflow because one source is down.

## The recurrence tally (how the next extractor picks itself)

Every residue item appends `{day, sender, subject_shape, hash}` to `_residue-tally.jsonl` (subject shape = digits/ids normalized to `#`). When the same shape has appeared on **3+ distinct days**, the pipeline lists it in `nudge_candidates` and a follow-up scan may surface ONE suggestion line. House rule: "if you do something 3+ times, consider automating it," applied to the system itself.

## How to add an extractor

1. **Copy `_example-extractor/`** to `ops/_extractors/<your-name>/`.
2. **Fill in `EXTRACTOR.md` frontmatter:** `name`, `channel`, `version: 1`, `trusted: false`, `source`, a `match` block (`sender_includes` + optional `subject_regex`), and `provenance` (when/where it was synthesized, and the message it was hand-parsed from).
3. **Write `extract.mjs`** as a pure function: takes one normalized envelope, returns a structured row `{ type, fields, confidence, source_ref }` on a match, or `null` on anything it doesn't recognize. Never guess.
4. **Capture a redacted fixture** into `fixtures/` (replace names, scrub token URLs / ids / emails). The folder is gitignored too.
5. **Write `extract.test.mjs`** asserting the output shape AND that key fields are non-empty against the fixture.
6. **Register it** in the table below with `trusted: false`.
7. **Run shadow mode** alongside the normal scan, compare, and only then flip `trusted: true`.

## Current registry

| Extractor | Channel | Matches | Emits | Status |
|---|---|---|---|---|
| `example-approval` | gmail | `alerts@[acme-domain]` + approval subjects | `approval_request` (ACTION) | `trusted: false` — shadow |
| `example-billing` | gmail | `notifications@[vendor-domain]` | `billing_notice` (ACTION) | `trusted: false` — shadow |
| `example-ticketing` | gmail | `@[ticketing-domain]` | `ticket_reminder` (ACTION), `ticket_update` | `trusted: false` — shadow |
| `example-digest` | gmail | `@[digest-domain]` digests | `digest_conversations` (noise-classify) | `trusted: false` — shadow |
| `example-meeting-report` | gmail | `@[meeting-tool-domain]` | `meeting_report` (FYI) | `trusted: false` — shadow |

> The rows above are placeholders to illustrate the registry shape. Replace `[acme-domain]`, `[vendor-domain]`, `[ticketing-domain]`, `[digest-domain]`, and `[meeting-tool-domain]` with the real sender domains you build extractors for.

## What's deliberately NOT here yet (optional later phases)

- A command to auto-synthesize extractors from the residue tally (build them by hand until then, same rules)
- Drift detection wired into your weekly review
- A shared signal-type schema
- Full-channel history sweeps (pullers start with the mention/outbound queries the specs scan; widening is a judgment call)
