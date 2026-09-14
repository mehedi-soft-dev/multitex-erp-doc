# Feature: Cost Center wise Ledger Summary

```yaml
---
id: feat:acc-cost-center-wise-ledger-summary
module: accounting
category: reports
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Cost Center wise Ledger Summary (Accounting > Reports > Cost Center wise Ledger Summary) answers: for one Cost Center (or one Cost Center Group), how much hit each GL account over a date range? The inverse of Ledger wise Cost Center Summary.

Table: `ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` (read-only, no staging table).

The screen actually bundles two independent report variants: pick one Cost Center + date range, or pick one Cost Center Group (all cost centers under it) + date range. Both export as PDF or Excel, and each has its own dedicated server action, service method, and Oracle procedure — they just happen to share one Angular page.

## Fields

This report has no add/edit form — just filter criteria and printed output columns, split across two variants that share one screen.

### Filters (by variant)

| Variant | Filter | Groups by |
|---|---|---|
| Cost Center | From/To date, one Cost Center (autocomplete) | GL account (one row per account with activity) |
| Cost Center Group | From/To date, one Cost Center Group (dropdown) | Cost Center name + GL account together |

Both button rows sit inside one shared form, so the Export buttons for either variant only enable once *every* required field on the page — including the other variant's picker — has a value. A pure UX defect, not a data problem, but confusing if the two modes were meant to be used independently.

### Output columns

Account name, summed Dr/Cr per account (plus a computed Net/Balance column), company name/address in the header. No opening balance or running total — a flat sum over the date window, same as its sibling report.

## Relationships

Cost Center (or Cost Center Group) filters `ACC_VOUCHER_DETAIL`, grouped by GL account, resolving to Chart of Accounts (account name shown per row).

See Ledger wise Cost Center Summary for the full direction-contrast table between the two reports.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The Excel export button is broken for both variants on this screen: the server action always returns a PDF regardless of which format button was clicked — the requested format is silently ignored. (The sibling Ledger wise Cost Center Summary report does this correctly.)
- **Critical:** No "posted only" filter on either variant — only a date-range check, same gap as the sibling report.
- **Critical:** No company check on the cost-center/cost-center-group ID actually used: the report's company name/address in the header always comes from the logged-in user's own session, but the underlying query never verifies that the cost center or group ID requested actually belongs to that company. Editing the id in the request could pull another company's cost-center data in under the current user's own company header — a real cross-company data-exposure risk, not just a theoretical one, since these IDs are plain sequential integers passed directly in the request.
- **Warning:** The Cost Center autocomplete silently defaults to a non-existent ID if the user types a name that doesn't match a suggestion, rather than validating — the likely result is a silently empty report with no error shown.
- **Warning:** No opening/running balance and no fiscal-year handling — a period-only net movement, not a running ledger balance; worth being explicit about this in the report's own title/help text since "Ledger Summary" could be misread as showing account balances.

## Unused Columns

None identified — every column the underlying query selects is actually printed on the report; there's no distinct staging table for this screen.

## Routing (mvc:/api: — omitted, confirmed why)

No `mvc:`/`api:` added to front-matter. This screen (`costCenterLeger` state, `Client\app\config.accountingRoute.js:355-370`) renders into `data-ui-view="costCenterLeger"` inside `Views\AccountingReport\Index.cshtml:20` — the SAME shell page (`AccountingReportController.Index()`) also hosts `ledgerReport`, `legerCostCenter`, `receivePaymentReport` and ~9 other report states (`Index.cshtml:5-20`). It is a shared multi-report shell, not a per-screen MVC action, so `mvc: AccountingReportController.Index` would be misleading. The screen's own content/export actions — `_CostCenterLeger()` (partial view) and the two dedicated export actions `CostCenterLedgerReport(...)` / `CostCenterGroupLedgerReport(...)` (`AccountingReportController.cs:438-463`) — are plain conventional MVC actions; the controller has no `[RoutePrefix]`/`[Route]`/`[HttpX]` attribute anywhere, so there is no Web API route for `api:` either.
