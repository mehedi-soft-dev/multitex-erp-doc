# Feature: Checker Maker

```yaml
---
id: feat:acc-checker-maker
module: accounting
category: master-data
http: POST .../checker-makers/update-vocher-master-post-id | POST .../checker-makers/update-bill-reconciliation
mvc: CheckerMakerController.Index
api: [POST api/accounting/checker-makers/update-vocher-master-post-id -> CheckerMakersController.UpdateCheckerMaker, POST api/accounting/checker-makers/update-bill-reconciliation -> CheckerMakersController.UpdateBillReconciliation]
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Checker Maker (Accounting > Master Data > Checker Maker) has no table of its own — it repairs
`ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` directly.

Despite the name, this is not a maker-checker (four-eyes approval) configuration screen. There is
no "who must approve whose entries" setup anywhere in the code — confirmed: no
`ACC_MAKER%`/`ACC_CHECKER%`/approval-role table or package exists in either repo.

It is actually a one-off data-repair utility with two hidden actions:

1. Find `ACC_VOUCHER_MASTER` rows that share a duplicate `POST_ID` and reassign a fresh one to
   all but the newest.
2. Recompute the `BILL_KEY` / `BILL_DETAIL_ID` housekeeping columns on `ACC_VOUCHER_DETAIL` that
   the Duplicate Bill Payment Report depends on.

Both actions are unreachable from the UI. The two buttons that would trigger them are commented
out of the view, so the screen renders an empty portlet titled "CHECKER MAKER" with nothing on
it. The Angular controller, service, and both API endpoints are still fully wired up and callable
directly — they're just orphaned from any visible control.

## Fields

There is no Add/Edit form and no List/search grid. The two operations the (commented-out)
buttons would have triggered:

| Would-be label | Endpoint | What it does | Columns touched |
|---|---|---|---|
| "Update VPI" (Update Voucher Master Post ID) | `POST .../checker-makers/update-vocher-master-post-id` | Finds duplicate `POST_ID` values across `ACC_VOUCHER_MASTER` (scoped by company code), and for each duplicate group, generates a fresh `POST_ID` for the row with the highest `VOUCHER_MASTER_ID`. | `ACC_VOUCHER_MASTER.POST_ID`, `.COMP_CODE`, `.VOUCHER_MASTER_ID` |
| "Update BILL" (Update Bill Reconciliation) | `POST .../checker-makers/update-bill-reconciliation` | Backfills `BILL_DETAIL_ID` and rebuilds the derived `BILL_KEY` string on `ACC_VOUCHER_DETAIL` for bill-type vouchers, then propagates any resulting `BILL_DETAIL_ID` to sibling rows sharing the same key. | `ACC_VOUCHER_DETAIL.BILL_KEY`, `.BILL_DETAIL_ID`, `.BILL_NO`, `.BILL_REF_ID`, `.AC_CODE`, `.MAIN_CODE`, `.SUB_CODE` |

Both endpoints take no request parameters and return an affected-row count. There is no
confirmation dialog, no preview of what will change — and since the buttons are commented out,
no way to reach either action except by calling the API URL directly.

## Relationships

Checker Maker isn't a lookup table with dependents — it's a repair job reaching directly into
two live transactional tables.

Checker Maker (no table — repair job) → dedupes → `ACC_VOUCHER_MASTER.POST_ID`

Checker Maker (no table — repair job) → rebuilds → `ACC_VOUCHER_DETAIL.BILL_KEY` / `BILL_DETAIL_ID`

Why `POST_ID` / `BILL_KEY` integrity matters:

- Voucher / Draft Voucher search-by-POST_ID lookups
- Day Book Report
- Duplicate Bill Payment Report (groups by BILL_KEY)
- "Available Same Bill" lookup (relies on BILL_DETAIL_ID)

## Known Issues

- **Critical:** The screen is completely non-functional in the UI: both action buttons are
  commented out of the view. A user who navigates here sees an empty portlet and can do nothing.
- **Critical:** The repair endpoints are still live and callable directly, with no confirmation
  and no audit trail, and no feature-specific auth check — both mutate live transactional data
  with a bare POST and no parameters.
- **Critical:** The bill-reconciliation repair ignores the company code it's given: the parameter
  is passed in but never used in any of its UPDATE statements — in a multi-company database this
  would rewrite bill keys for every company's vouchers, not just the caller's.
- **Warning:** The "current company" for both repairs is resolved via an app-wide hardcoded
  constant ("001"), not the logged-in user's actual company — the same pattern used throughout
  this module, but here it makes the "per-company" scoping illusory.
- **Warning:** Raw string-concatenated SQL throughout both repair queries — a
  SQL-injection-shaped pattern, even though today's inputs aren't attacker-controlled.
- **Warning:** The duplicate-POST_ID repair re-derives a new POST_ID via an old MAX(POST_ID)+1
  read-then-write approach that the Oracle package has since replaced with a real sequence
  elsewhere — the repair tool still uses the race-condition-prone approach, and could itself
  generate a fresh collision while fixing an old one.
- **Minor:** Typo'd filename shipped to the client (missing a letter) — cosmetic, but confirms
  this screen has had essentially no maintenance attention since it was written.
- **Minor:** Misleading naming end-to-end: the screen is titled "Checker Maker," which
  conventionally means maker-checker approval configuration in accounting software. Nothing here
  defines approvers, roles, or workflow.
- **Minor:** No feedback on what was actually fixed: even if re-enabled, the callback shows a
  generic success toast regardless of how many rows were rewritten.

## Unused Columns

Checker Maker has no table of its own. Every column its two repair operations touch (`POST_ID`,
`VOUCHER_MASTER_ID`, `BILL_DETAIL_ID`, `BILL_NO`, `BILL_REF_ID`, `AC_CODE`, `MAIN_CODE`,
`SUB_CODE`) is actively used elsewhere in the app — nothing to flag as dead.

One caveat: `BILL_KEY` is read in only two places across the whole codebase — one report's
grouping query (Duplicate Bill Payment Report) and this repair job's own follow-up query. It's
not unused, but it's thin enough that if that one report were ever removed, `BILL_KEY` would
become fully unused while still being silently maintained by this repair job.
