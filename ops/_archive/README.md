---
title: Ops Archive
type: note
tags: [archive, ops, docc]
---

# Ops Archive

Cold storage for the hot tracking files. The rule: **hot files carry only open loops and recent items; everything closed or historical moves here.** These files are committed to the repo (and can optionally be synced to a deep-retrieval store — a search/recall layer over the whole repo — so nothing is lost). Archived content stays fully retrievable via that store or a local grep, and is **never loaded at session start**.

| File | Receives |
|------|----------|
| [awaiting-archive.md](awaiting-archive.md) | Closed/resolved loops from `ops/_awaiting.md` |
| [tasks-archive.md](tasks-archive.md) | Completed/struck task rows from `ops/_tasks.md` |
| [index-history.md](index-history.md) | Header update narratives, Processing Log rows older than 14 days, superseded sections from `ops/_index.md` |
| [contacts-history.md](contacts-history.md) | Header update narratives (and archived contacts) from `ops/_contacts.md` |

## Rules (for commands writing here)

1. **Closures move, they don't accumulate.** When a loop/task closes, strike it in the hot file during the run that closes it, then move the struck row to the matching archive file in the same pass (closure propagation still applies to BOTH hot files first).
2. **Header narratives stay one update deep.** The `**Last Updated:**` line in a hot file describes only the latest run. The previous narrative moves to the archive file's newest sweep section.
3. **Append under a dated `## Sweep YYYY-MM-DD` section** (newest at top). Create the day's section if it doesn't exist.
4. **Never edit archived content.** Append-only. If something was archived wrongly, copy it back to the hot file and note the un-archive.
5. **Retrieval:** use the optional deep-retrieval store for deep recall; grep these files for quick lookups. Don't re-load archives into session-start reads.

## Optional: deep-retrieval store

If you wire up a search/recall index over this repo (any vector/semantic store), commit + sync these archive files into it so closed loops, completed tasks, and historical context stay queryable on demand without bloating the hot files. This is optional — grep works fine for a single-operator setup.

Created at template release.
