---
title: /route - Router Engine Lookup
type: note
---

# /route - Router Engine Lookup

Route a request to the right person.

$ARGUMENTS is the topic, question, or pasted forwarded message.

## Steps

1. **Read** `ops/router-engine/_routing.md`.

2. **Classify (ROJI):**
   - **Route** — Someone else owns this. Continue.
   - **Own** — [YOUR NAME] is the source of truth. Say so. Stop.
   - **Judge** — Needs [YOUR NAME]'s judgment to route. Present options. Stop.
   - **Ignore** — Not actionable. Say so. Stop.

3. **Match against routing table:** Search by keyword, topic, context. Check sensitivity. Check Last Verified (flag if >30 days). Rank multi-matches by relevance.

4. **If no routing match, search KB:** `ops/_kb.md`, `ops/_contacts.md`, relevant `ops/{project}/{project}.context.md`.

5. **Score confidence:**
   - Exact routing table match: +40
   - Multiple keyword signals same domain: +20
   - Contact role matches topic: +15
   - KB has relevant guidance: +15
   - Verified <30 days: +10
   - Multiple confirming sources: +10
   - Domain overlap (multiple owners): -25
   - Sensitive area (legal, finance, personnel): -15
   - Owner recently changed roles: -20
   - Ambiguous or multi-part: -15

6. **Present:**

   **HIGH (85%+):**
   ```
   ROUTE TO: [Name] ([email])
   Confidence: HIGH (X%)
   Domain: [matched domain]
   Reason: [one line]
   Last Verified: [date]
   Sensitivity: [standard/elevated/restricted]
   ```

   **MEDIUM (60-84%):**
   ```
   OPTIONS:
   1. [Name] ([email]) -- [reason] (X%)
   2. [Name] ([email]) -- [reason] (Y%)

   Recommendation: Option [N] because [reason].
   ```

   **LOW (<60%):**
   ```
   NO CONFIDENT MATCH
   Topic: [what request is about]
   Closest matches: [partial matches with uncertainty reasons]
   What I know: [relevant KB context]

   Who should handle this?
   ```

   **RESTRICTED:** Always add: "This domain is RESTRICTED. Routing requires your direct review."

   **Stale (>30 days):** Always add: "Last verified [date] (N days ago). Confirm still accurate."

7. **Log:** When [YOUR NAME] confirms or corrects, append to Correction Log in `ops/router-engine/_routing.md`: date, topic, suggested route, actual route, reason. If corrected, update the routing entry immediately.

## Hard Blocks (never route, always escalate)

- Requests from [YOUR BOSS] or above
- Legal/compliance (FERPA, contracts, litigation)
- Personnel/HR (performance, comp, hiring decisions)
- Financial approvals (spend, insurance binding)
- Cross-BU organizational boundary
- Recently departed employees with unclear ownership

## Examples

**Clean:**
```
/route who handles device repairs?

ROUTE TO: [A direct report] ([EMAIL])
Confidence: HIGH (90%)
Domain: device repairs
Reason: A direct report took over device repair from a prior owner. ~30 devices in backlog. Self-serve model per site.
Last Verified: 2026-02-27
Sensitivity: standard
```

**Ambiguous:**
```
/route student account not working in the learning platform

OPTIONS:
1. EDU Support ([EMAIL]) -- Standard ticket for account issues (65%)
2. A platform owner ([EMAIL]) -- learning-platform system-level (55%)
3. An integration owner ([EMAIL]) -- platform/integration interface (45%)

Recommendation: Option 1 for student-facing. Option 2 for system/integration.
```

**Restricted:**
```
/route can the registrar team support virtual enrollment?

ROUTE TO: A registrar lead ([EMAIL])
Confidence: HIGH (90%)
Domain: Registrar scope / future structure
Sensitivity: RESTRICTED -- requires your direct review.
Reason: Active org discussion about registrar scope for virtual programs. You have a position. Review underway, no timeline.
Last Verified: 2026-02-26
```
