# Routing Table

Maps domains/topics to the people who own them. Used by `/route` and `/classify` commands.

**How to use:**
- Run `/route [topic or question]` — DOCC matches against this table and returns the best owner with confidence
- Run `/classify` — DOCC uses this table to suggest routing for ACTION:ROUTE inbox items
- Update this table when routing corrections happen or new owners are identified

**Confidence levels:**
- **HIGH** — clear domain ownership, used this route before
- **MEDIUM** — best guess, may need validation
- **LOW** — uncertain, flag to operator

---

## Routing Table

| Domain / Topic | Primary Owner | Backup | Confidence | Notes |
|---------------|---------------|--------|------------|-------|
| [Domain 1, e.g. "HR / Hiring"] | [Person Name] | [Backup Person] | HIGH | [Any context] |
| [Domain 2, e.g. "Finance approvals"] | [Person Name] | — | MEDIUM | [Any context] |
| [Domain 3, e.g. "IT / Infrastructure"] | [Person Name] | [Backup Person] | HIGH | [Any context] |

---

## Correction Log

When a routing recommendation is wrong, log it here so the table can be updated.

| Date | Query | Routed To | Should Have Been | Fix Applied |
|------|-------|-----------|-----------------|-------------|
| YYYY-MM-DD | [Query] | [Wrong person] | [Right person] | [Yes/No] |

---

## Classification Labels

When `/classify` runs on the inbox, each item gets one of these labels:

| Label | Meaning |
|-------|---------|
| **IGNORE** | No action needed, no useful signal |
| **FYI** | Read for awareness, no response required |
| **ACTION:ME** | Requires the operator to personally respond or decide |
| **ACTION:ROUTE** | Should be forwarded or delegated — see routing table for owner |
