"""
/kb-lint v1 — manifest regeneration + drift detection
Implements the steps in .claude/commands/kb-lint.md

Usage:
    python ops/_kb/_kb-lint.py
    python ops/_kb/_kb-lint.py --diff            # read-only: show what WOULD change, write nothing
    python ops/_kb/_kb-lint.py --frozen-timestamp "YYYY-MM-DD HH:MM TZ"

Flags:
    --diff             Compute the manifest and print a unified diff against the
                       existing one WITHOUT writing. Use during review.
    --frozen-timestamp Stamp a fixed timestamp instead of "now" (determinism tests).

Note: --check-references and --triage-inbox from the /kb-lint command contract are
command-layer behaviors (the agent performs the grep / inbox triage); this script
handles manifest regeneration, --diff, and --frozen-timestamp.

Regenerates the KB manifest (ops/_kb/_index.md) from the frontmatter of every
topic file under ops/_kb/{scope}/, and reports drift (orphans, broken related
links, missing frontmatter, stale files, mismatched id/scope, cross-scope
duplicate source IDs). Safe to run anytime; auto-runs during /weekly.
"""
import re
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

try:
    import yaml  # preferred: full YAML support if installed (pip install -r requirements.txt)
except ImportError:
    # Zero-dependency fallback so /kb-lint (and /weekly, which auto-runs it) works on a
    # fresh clone with stdlib only. Handles the simple frontmatter this KB uses:
    # scalars, "key: [a, b]" flow lists, and "key:" + indented "- item" block lists.
    class _MiniYAMLError(Exception):
        pass

    class _MiniYAML:
        YAMLError = _MiniYAMLError

        @staticmethod
        def safe_load(text):
            if text is None:
                return {}
            data, cur_key = {}, None
            for raw in str(text).splitlines():
                if not raw.strip() or raw.lstrip().startswith("#"):
                    continue
                indented = len(raw) - len(raw.lstrip())
                stripped = raw.strip()
                if stripped.startswith("- ") and cur_key is not None and indented > 0:
                    if not isinstance(data.get(cur_key), list):
                        data[cur_key] = []
                    data[cur_key].append(stripped[2:].strip().strip("\"'"))
                    continue
                if ":" in raw and indented == 0:
                    key, _, val = raw.partition(":")
                    key, val = key.strip(), val.strip()
                    if val == "":
                        data[key], cur_key = None, key
                    elif val.startswith("[") and val.endswith("]"):
                        inner = val[1:-1].strip()
                        data[key] = [v.strip().strip("\"'") for v in inner.split(",")] if inner else []
                        cur_key = None
                    else:
                        data[key], cur_key = val.strip("\"'"), None
            return data

    yaml = _MiniYAML()
    print("Note: PyYAML not installed — using built-in fallback parser. "
          "For full YAML support: pip install -r requirements.txt")

# ---- Configuration ----
KB_DIR = Path("ops/_kb")
MANIFEST_PATH = KB_DIR / "_index.md"
LINT_LOG_PATH = KB_DIR / "_lint-log.md"

# ---- UNVALIDATED PLACEHOLDERS ----
# These thresholds are not data-backed. They exist as configurable knobs to
# emit drift signals during early operation. Adjust based on observed usage,
# do not treat as authoritative defaults.
STALE_THRESHOLD_DAYS = 90  # PLACEHOLDER: no measurement basis. When real data
                            # accumulates (e.g., 3+ months of /weekly runs showing
                            # which files genuinely never resurface), retune.

# Removed: file-count growth-rate alarm (had no empirical basis).
# Removed: 600-line / 30-H3 file split trigger (extrapolated, not measured).
# These can be reintroduced when real usage data justifies a specific value.

# ---- Argument parsing ----
ARGS = sys.argv[1:]
DIFF_MODE = "--diff" in ARGS  # read-only: print a diff, write nothing

# Allow a frozen timestamp for determinism testing; otherwise stamp "now".
RUN_TIMESTAMP = None
if "--frozen-timestamp" in ARGS:
    _i = ARGS.index("--frozen-timestamp")
    if _i + 1 < len(ARGS):
        RUN_TIMESTAMP = ARGS[_i + 1]
if RUN_TIMESTAMP:
    RUN_DATE = RUN_TIMESTAMP.split(" ")[0]
else:
    _now = datetime.now()
    RUN_TIMESTAMP = _now.strftime("%Y-%m-%d %H:%M")
    RUN_DATE = _now.strftime("%Y-%m-%d")

# Adapt these scope names to your own operating domains. Keep the list in sync
# with the subdirectories under ops/_kb/.
ALL_SCOPES = ["procurement", "devices", "provisioning", "workspace", "people-and-tone",
              "finance", "compliance", "partners", "docc-system", "areas"]

# ---- Cross-scope duplicate detection patterns ----
# Each pattern matches an externally-stable identifier that is unlikely to collide
# by chance. Two files in different scopes sharing one of these IDs likely cite
# the same source — used to detect either intentional duplication (fine) or
# unintentional drift (action required, when files don't list each other in `related:`).
DUPLICATE_ID_PATTERNS = {
    "gmail_thread": re.compile(r"\b1[0-9a-f]{14,16}\b"),
    # Notion page ID (UUID format with or without hyphens, 32 hex chars)
    "notion_page": re.compile(r"\b[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\b"),
    # Slack thread/message timestamp (e.g., p1234567890123456 — 16 digits after p)
    "slack_thread": re.compile(r"\bp[0-9]{16}\b"),
    # Drive doc/sheet ID (44-char alphanumeric with underscore/hyphen, starts with 1)
    "drive_doc": re.compile(r"\b1[A-Za-z0-9_-]{42,49}\b"),
}

# ---- Step 1: Discover topic files ----
topic_files = []
if KB_DIR.exists():
    for fp in sorted(KB_DIR.rglob("*.md")):
        if fp.name.startswith("_"):
            continue
        # Skip per-scope README scaffolds
        if fp.name.upper() == "README.MD":
            continue
        topic_files.append(fp)

# ---- Step 2: Parse frontmatter ----
parsed = []
drift = {
    "orphans": [],
    "broken_related": [],
    "missing_frontmatter": [],
    "stale_files": [],
    "mismatched_id": [],
    "mismatched_scope": [],
    "cross_scope_duplicates": [],
}

for fp in topic_files:
    content = fp.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not m:
        drift["missing_frontmatter"].append(str(fp))
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        drift["missing_frontmatter"].append(f"{fp} (YAML parse error: {e})")
        continue
    body = m.group(2)

    required = ["id", "scope", "last_updated", "summary"]
    missing = [r for r in required if r not in fm or fm[r] in (None, "")]
    if missing:
        drift["missing_frontmatter"].append(f"{fp} (missing: {', '.join(missing)})")
        continue

    if str(fm["id"]) != fp.stem:
        drift["mismatched_id"].append(f"{fp}: id={fm['id']} but stem={fp.stem}")
    if str(fm["scope"]) != fp.parent.name:
        drift["mismatched_scope"].append(f"{fp}: scope={fm['scope']} but parent={fp.parent.name}")

    fm.setdefault("related", [])
    fm.setdefault("projects", [])
    fm.setdefault("keywords", [])
    fm.setdefault("people", [])
    if not isinstance(fm["related"], list): fm["related"] = []
    if not isinstance(fm["projects"], list): fm["projects"] = []
    if not isinstance(fm["keywords"], list): fm["keywords"] = []
    if not isinstance(fm["people"], list): fm["people"] = []

    parsed.append((fp, fm, body))

# ---- Step 3: Build manifest data ----
all_ids = {fm["id"]: fp for fp, fm, _ in parsed}

referenced = set()
for fp, fm, _ in parsed:
    for r in fm["related"]:
        referenced.add(r)
for fp, fm, _ in parsed:
    if fm["id"] not in referenced:
        drift["orphans"].append(f"{fm['scope']}/{fm['id']}")

for fp, fm, _ in parsed:
    for r in fm["related"]:
        if r not in all_ids:
            drift["broken_related"].append(f"{fm['scope']}/{fm['id']} -> {r} (not found)")

cutoff = datetime.fromisoformat(RUN_DATE) - timedelta(days=STALE_THRESHOLD_DAYS)
for fp, fm, _ in parsed:
    try:
        d = fm["last_updated"] if isinstance(fm["last_updated"], str) else str(fm["last_updated"])
        last = datetime.fromisoformat(d)
        if last < cutoff:
            drift["stale_files"].append(f"{fm['scope']}/{fm['id']} (last_updated: {d}, threshold: {STALE_THRESHOLD_DAYS}d)")
    except (ValueError, TypeError):
        pass

# Cross-scope duplicate detection — checks all stable-identifier patterns
# (Gmail thread IDs, Notion page IDs, Slack thread timestamps, Drive doc IDs)
file_to_ids = {}  # key: scope/id, value: dict of pattern_name -> set of matched ids
for fp, fm, body in parsed:
    key = f"{fm['scope']}/{fm['id']}"
    file_to_ids[key] = {
        name: set(pat.findall(body))
        for name, pat in DUPLICATE_ID_PATTERNS.items()
    }

keys = list(file_to_ids.keys())
for i, k1 in enumerate(keys):
    s1 = k1.split("/")[0]
    fm1 = next(fm for fp, fm, _ in parsed if f"{fm['scope']}/{fm['id']}" == k1)
    for k2 in keys[i+1:]:
        s2 = k2.split("/")[0]
        if s1 == s2: continue  # same scope is fine
        # Aggregate shared IDs across all patterns
        shared_by_type = {}
        for pattern_name in DUPLICATE_ID_PATTERNS:
            overlap = file_to_ids[k1][pattern_name] & file_to_ids[k2][pattern_name]
            if overlap:
                shared_by_type[pattern_name] = overlap
        if shared_by_type:
            fm2 = next(fm for fp, fm, _ in parsed if f"{fm['scope']}/{fm['id']}" == k2)
            id1, id2 = fm1["id"], fm2["id"]
            if id2 in fm1["related"] or id1 in fm2["related"]:
                continue  # explicitly related, fine
            # Format detail: show pattern types and a sample of shared IDs
            detail = "; ".join(
                f"{pname}: {sorted(ids)[:2]}"
                for pname, ids in sorted(shared_by_type.items())
            )
            drift["cross_scope_duplicates"].append(f"{k1} <-> {k2}: {detail}")

# ---- Step 5: Compose manifest ----
def join_or_dash(lst):
    if not lst: return "—"
    return ", ".join(sorted(str(x) for x in lst))

scope_files = {}
for fp, fm, _ in parsed:
    scope_files.setdefault(fm["scope"], []).append(fm)

quick_map_rows = []
for scope in ALL_SCOPES:
    files = sorted(scope_files.get(scope, []), key=lambda x: x["id"])
    if files:
        purpose = "; ".join(f["summary"].split(".")[0][:60].strip() for f in files[:3])
        if len(files) > 3:
            purpose += f" ... (+{len(files) - 3} more)"
    else:
        purpose = "(no files yet)"
    quick_map_rows.append(f"| {scope} | {len(files)} | {purpose} |")

sorted_parsed = sorted(parsed, key=lambda x: (x[1]["scope"], x[1]["id"]))
all_files_rows = []
for fp, fm, _ in sorted_parsed:
    row = (f"| {fm['id']} | {fm['scope']} | {fm['summary']} | "
           f"{join_or_dash(fm['keywords'])} | {fm['last_updated']} | "
           f"{join_or_dash(fm['related'])} |")
    all_files_rows.append(row)

project_to_ids = {}
for fp, fm, _ in parsed:
    for proj in fm["projects"]:
        project_to_ids.setdefault(proj, set()).add(fm["id"])
project_rows = []
for proj in sorted(project_to_ids.keys()):
    ids = sorted(project_to_ids[proj])
    project_rows.append(f"| {proj} | {', '.join(ids)} |")

person_to_ids = {}
for fp, fm, _ in parsed:
    for p in fm["people"]:
        person_to_ids.setdefault(p, set()).add(fm["id"])
person_rows = []
for p in sorted(person_to_ids.keys()):
    ids = sorted(person_to_ids[p])
    person_rows.append(f"| {p} | {', '.join(ids)} |")

drift_total = sum(len(v) for v in drift.values())
drift_status = "clean" if drift_total == 0 else f"{drift_total} issues"

def drift_line(name, items):
    if not items: return f"- **{name}:** none"
    head = f"- **{name}:** {len(items)}"
    bullets = "\n  - " + "\n  - ".join(items[:10])
    return head + bullets

newline = "\n"
manifest = f"""# KB Manifest

> **Auto-generated by `/kb-lint`. Do not edit by hand.**
> Last regen: {RUN_TIMESTAMP}
> Topic files: {len(parsed)} | Scopes covered: {len(scope_files)}/{len(ALL_SCOPES)} | Drift: {drift_status}

## Quick Map

| Scope | Files | Purpose |
|-------|-------|---------|
{newline.join(quick_map_rows)}

## All Files

| ID | Scope | Summary | Keywords | Updated | Related |
|----|-------|---------|----------|---------|---------|
{newline.join(all_files_rows) if all_files_rows else "| (no files yet) | | | | | |"}

## Lookup By Project

| Project | Relevant KB Files |
|---------|-------------------|
{newline.join(project_rows) if project_rows else "| (none yet) | |"}

## Lookup By Person

| Person | Mentioned In |
|--------|--------------|
{newline.join(person_rows) if person_rows else "| (none yet) | |"}

## Drift Report

### Real drift (action required)

{drift_line("Orphans", drift["orphans"])}
{drift_line("Broken related links", drift["broken_related"])}
{drift_line("Missing frontmatter", drift["missing_frontmatter"])}
{drift_line(f"Stale files (>{STALE_THRESHOLD_DAYS}d)", drift["stale_files"])}
{drift_line("Mismatched id/filename", drift["mismatched_id"])}
{drift_line("Mismatched scope/directory", drift["mismatched_scope"])}
{drift_line("Cross-scope duplicates (unrelated files sharing source IDs)", drift["cross_scope_duplicates"])}

For full history, see [`_lint-log.md`](_lint-log.md).
"""

if DIFF_MODE:
    import difflib
    existing = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else ""
    if existing == manifest:
        print(f"--diff: {MANIFEST_PATH} already up to date (no changes; {len(parsed)} topic files).")
    else:
        sys.stdout.writelines(difflib.unified_diff(
            existing.splitlines(keepends=True),
            manifest.splitlines(keepends=True),
            fromfile=f"{MANIFEST_PATH} (current)",
            tofile=f"{MANIFEST_PATH} (regenerated)",
        ))
        print(f"\n--diff: {MANIFEST_PATH} would change (NOT written). Re-run without --diff to apply.")
else:
    MANIFEST_PATH.write_text(manifest, encoding="utf-8", newline="\n")
    # Append a run entry to the lint log so the history link in the manifest resolves.
    log_entry = (
        f"## {RUN_TIMESTAMP}\n"
        f"- Topic files: {len(parsed)} | Scopes: {len(scope_files)}/{len(ALL_SCOPES)} | Drift: {drift_status}\n\n"
    )
    if LINT_LOG_PATH.exists():
        LINT_LOG_PATH.write_text(
            log_entry + LINT_LOG_PATH.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
        )
    else:
        LINT_LOG_PATH.write_text(
            "# KB Lint Log\n\nRun history (newest first). Auto-appended by /kb-lint.\n\n" + log_entry,
            encoding="utf-8", newline="\n",
        )
    print(f"Wrote manifest: {MANIFEST_PATH}")
    print(f"Appended lint log: {LINT_LOG_PATH}")

print(f"  Size: {len(manifest)} bytes")
print(f"  Lines: {manifest.count(chr(10)) + 1}")
print(f"  Topic files indexed: {len(parsed)}")
print(f"  Scopes covered: {len(scope_files)}/{len(ALL_SCOPES)}")
print(f"  Drift: {drift_status}")
print(f"  Projects: {len(project_to_ids)}")
print(f"  People: {len(person_to_ids)}")
print()
print(f"Drift breakdown:")
for k, v in drift.items():
    print(f"  {k}: {len(v)}")
