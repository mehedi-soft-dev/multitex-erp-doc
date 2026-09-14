# Feature: Fiscal Year Close

```yaml
---
id: feat:acc-fiscal-year-close
module: accounting
category: transaction
mvc: AccntController.FYClose
api: [GET api/accounting/AccFy/get-acc-fy-list -> FyController.GetAccFyList, GET api/accounting/AccFy/get-trail-balance4fy_close -> FyController.GetTrailBalance4FyClose, GET api/accounting/AccFy/get-trail-balance_dtl4fy_close -> FyController.GetTrailBalanceDtl4FyClose, POST api/accounting/AccFy/fy-closing-process -> FyController.FyClosingProcess]
tables: [ACC_FISCAL_YEAR, ACC_OPENING_BALANCE, ACC_REPORT_TRIAL_BALANCE]
status: verified
---
```

## Overview

Fiscal Year Close is the year-end closing process in the Accounting module (screen path: Accounting > Transaction > Fiscal Year Close).

A user picks a company and a fiscal year period (drawn from the same `ACC_FISCAL_YEAR` table documented on the Fiscal Year master-data page), reviews a trial balance for that period, and clicks "Closing Process". This action snapshots the closing trial balance into `ACC_OPENING_BALANCE` (becoming the next year's opening figures) and flips that fiscal year's `IS_CLOSED` flag to `Y`, locking it from further voucher postings.

This is the **only** place fiscal years can be modified through the app at all — there is no Add/Edit/Delete screen for `ACC_FISCAL_YEAR` itself (see the Fiscal Year master-data page). This screen's Period dropdown is read-only against whatever rows already exist in the table.

## Fields

| Label | Bound to | Meaning |
|---|---|---|
| Company | `HR_COMPANY_ID` | Filters which fiscal years show in the Period dropdown. |
| Period (dropdown) | `ACC_FISCAL_YEAR_ID`, displays `FY_NAME_EN` + `REMARKS` | Which fiscal year to review/close. Selecting one auto-fills the From/To search dates from `FY_START_DATE`/`FY_END_DATE`. |
| Trial balance grid | populated via a report call, not a stored table | Shows the account-by-account trial balance for the selected period before closing. |
| "Closing Process" button | posts `HR_COMPANY_ID` + `ACC_FISCAL_YEAR_ID` | Triggers the actual close — irreversible through the UI. |

The dropdown's "closed" filter is always hard-coded to request open (`N`) years from the client — see Known Issues for why that filter doesn't even work as intended server-side.

## Relationships

Selecting a period from `ACC_FISCAL_YEAR` and running the Closing Process snapshots data into `ACC_OPENING_BALANCE`, which becomes the next year's opening figures.

The screen also touches `ACC_REPORT_TRIAL_BALANCE`, a shared staging table keyed by user id, and interacts with the voucher save path, which blocks new postings once a fiscal year's `IS_CLOSED` flag is `'Y'`.

See the Fiscal Year master-data page for the full picture of how (weakly) vouchers relate to fiscal years — there's no real foreign key, only a date-range comparison at save time.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The trial-balance-fetch API action has a copy/paste bug: it computes a value via one report call, discards it, and returns a second, unrelated call's result instead. That second call reads from a shared staging table (`ACC_REPORT_TRIAL_BALANCE`) filtered only by user ID — no date-range or company filter of its own. If the first call's population step ever fails or is skipped, this screen silently shows stale data left over from a previous screen/date-range the same user viewed; two browser tabs for the same user against different companies can cross-contaminate each other's trial balance.
- **Critical:** The fiscal-year list's "closed" filter parameter doesn't actually filter by the value passed in — the SQL only checks whether the parameter is null, not what it equals. Requesting closed years still returns only open ones.
- **Warning:** Two independent, divergent "close a fiscal year" implementations exist in the database layer, and this screen only wires up the one with fewer safety checks. The one this screen does NOT call would have checked for existing opening balances and unposted vouchers before proceeding — the live path has no such guard.
- **Warning:** The closing procedure accepts an option parameter that is never actually checked in its body — the closing logic runs unconditionally, unlike other multi-purpose procedures in the same package that properly branch on their option parameter.
- **Warning:** No explicit COMMIT in the closing procedure — only a ROLLBACK in the exception handler. Whether a "successful" closing is actually persisted depends entirely on database connection autocommit settings.
- **Warning:** No overlap/gap validation exists between fiscal years anywhere in the system — if two years for the same company ever have overlapping date ranges, the voucher-date validation lookup becomes ambiguous. That ambiguity is swallowed by a blanket exception handler that silently disables the closed-year check entirely rather than surfacing an error to anyone.
- **Minor:** The API controller reads a session value eagerly in its constructor for every action, including the plain list read that doesn't use it — a null/expired session throws before any action method runs, even the harmless one.

## Unused Columns

See the Fiscal Year master-data page's Unused Columns section — this screen reads the same `ACC_FISCAL_YEAR` row set and doesn't introduce any new column usage of its own beyond `FY_START_DATE`/`FY_END_DATE`/`IS_CLOSED`/`ACC_FISCAL_YEAR_ID`/`HR_COMPANY_ID`, all of which are already confirmed actively used.
