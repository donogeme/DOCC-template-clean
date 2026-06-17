---
title: /inventory - Device Inventory Monitor
type: note
---

# /inventory - Device Inventory Monitor

Check laptop inventory levels against thresholds. Generate alerts if needed.

$ARGUMENTS: `status` (quick view, no alerts), `order` (draft device-vendor order), or blank (full check).

## Steps

1. **Read inventory data.** Spreadsheet ID: `[INVENTORY_SHEET_ID]`
   - `Dashboard!A1:M40` — per-site status
   - `Parameters!A1:B40` — thresholds and config
   - `Device Order Status!A1:L20` — pending orders

   **Fallback (if Dashboard/Parameters missing):**
   - `Current inventory (asset-tracker)!A1:T15` — device counts by site
   - `List of Sites!B2:AC30` — enrollment by site by grade
   - Default thresholds: GREEN ≥15%, YELLOW ≥8%, RED <8% spare ratio. Network reorder point: 30.

2. **Read DOCC context:** `ops/inventory-monitoring/inventory-monitoring.context.md`, `ops/laptop-procurement/laptop-procurement.context.md`, `ops/_awaiting.md` (pending device-vendor responses).

3. **Per-site evaluation** (sites with enrollment > 0):
   - Laptop-eligible students = sum of grades 3-12 enrollment
   - Laptops on hand = owned laptops + Chromebooks + leased laptops (mapped by site)
   - Spares = Laptops - Eligible
   - Spare ratio = Spares / Eligible
   - Status: GREEN ≥0.15, YELLOW ≥0.08, RED <0.08
   - Also flag if absolute spares <3 (safety floor)

4. **Network-wide:**
   - Total unallocated = sum of site spares + hub inventory (Operations hub, Transit)
   - GREEN ≥30, YELLOW 15-29, RED <15

5. **Pending orders:** Scan Device Order Status for Status ≠ "Delivered". Note qty, ETA, destination. Factor into recommendations.

6. **Data freshness:** If Parameters tab exists, read "Last Export Date". If >14 days old, warn: "Inventory data may be stale (last updated: [date]). Consider refreshing from the asset tracker."

7. **Generate report:**

```
## Device Inventory Status - [Date]

### Data Freshness
- Asset tracker export: [date]
- Enrollment data: [date]
[Stale warning if applicable]

### Network Summary
- Total Laptops on Hand: [N] across [N] sites
- Laptop-Eligible Students: [N]
- Network Spare Ratio: [X%]
- Unallocated Pool: [N] (hub + transit)
- Network Status: [GREEN/YELLOW/RED]

### Sites Needing Attention

#### RED ZONE
| Site | City | Students | Laptops | Spares | Ratio | Issue |
|---|---|---|---|---|---|---|

#### YELLOW ZONE
| Site | City | Students | Laptops | Spares | Ratio |
|---|---|---|---|---|---|

#### GREEN ZONE
[N] sites. [List names; details only in "status" mode]

### Pending Orders
| Order ID | Qty | Item | Destination | ETA | Status |
|---|---|---|---|---|---|

### Recommended Actions
[Based on threshold evaluation]
```

8. **Alert logic** (skip if `$ARGUMENTS = "status"`):

   **Any site RED:**
   - Draft alert email to [EMAIL]
   - CC [EMAIL] if any site has negative spares
   - Subject: `[INVENTORY ALERT] [N] site(s) in RED zone`
   - Include: sites, counts, what's needed, helpful pending orders
   - Present as draft. NEVER send without "send it."

   **Network YELLOW or RED:**
   - Quantity needed = max(30 - current unallocated, 0) + buffer
   - Round up to preferred batch (50) or minimum (25)
   - Draft reorder recommendation: qty, model, est. cost, ship-to, expected delivery (~30d)
   - Ask: "Want me to draft the device-vendor order email to the vendor rep?"

   **All GREEN:** Report "All clear" with summary. No email.

9. **If `$ARGUMENTS = "order"` or "draft device order":**
   - To: [EMAIL]
   - CC: [EMAIL]
   - Subject: `New Laptop Order - [Qty] [Device Model] | [Organization]`
   - Use `ops/_kb/people-and-tone/voice.md`
   - Include: qty, model, ship-to, bill-to, timeline
   - Present draft. NEVER send without explicit approval.

10. **Update tracking:**
    - Write timestamp to Dashboard "Last DOCC Check" cell (if exists)
    - Note threshold breaches in output
    - If [YOUR NAME] orders, add to `_awaiting.md`

## Rules

- Standalone with `/inventory` or runs in `/gm`.
- NEVER send device-vendor emails without "send it" approval.
- Factor in pending orders before recommending new ones.
- Device-vendor lead time ~30 days. Ground shipping only (lithium battery regs).
- Laptops counted: owned laptops, Chromebooks, leased laptops, MacBooks (high school).
- Tablets not monitored in Phase 1.
- Data sources unavailable → report what you can, flag gaps.
