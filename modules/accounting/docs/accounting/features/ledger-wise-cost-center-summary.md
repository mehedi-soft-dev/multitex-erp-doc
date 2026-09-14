# Feature: Ledger wise Cost Center Summary

```yaml
---
id: feat:acc-ledger-wise-cost-center-summary
module: accounting
category: reports
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Ledger wise Cost Center Summary (Accounting > Reports > Ledger wise Cost Center Summary) answers: for one specific GL account, how much Debit/Credit did each Cost Center contribute over a date range? The user picks a single GL account and a date range, then exports as PDF or Excel. The report groups every voucher line posted against that account within the range by Cost Center, sums Dr/Cr per cost center, and prints one row per cost center that had activity (no zero-amount rows).

Table: `ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` (read-only, no staging table).

This is the mirror image of Cost Center wise Ledger Summary — that one fixes a cost center and subtotals by account; this one fixes an account and subtotals by cost center.

## Fields

This report has no add/edit form — just filter criteria and printed output columns.

### Filters

| Filter | Meaning |
|---|---|
| From / To Date | Posting-date window. |
| Account Head | Single GL account, picked via autocomplete. Matched by a concatenated code string, not the account's numeric ID — see Known Issues. |

There is no Cost Center filter and no Company filter on the screen — only date range and account actually vary the result. Two additional filter parameters (single cost-center-name, single company) exist and work inside the underlying query, but nothing on this screen ever supplies them — dead capability.

### Output columns

| Output column | Meaning |
|---|---|
| Cost Center Name | Grouping key — one row per cost center with activity. |
| Dr / Cr / Net Amount | Summed debit/credit for that cost center against the chosen account, plus the computed difference. |

No opening balance, no running total, no fiscal-year carry-forward — this is a flat sum over the date window only.

## Relationships

Chart of Accounts (account picked via autocomplete) is matched by concatenated code string against `ACC_VOUCHER_DETAIL`, which is grouped by Cost Center, resolving to Cost Center.

Shares its Angular controller with the plain Ledger report. Its sibling report, Cost Center wise Ledger Summary, has the identical missing-filter defects described below — strongly suggesting a shared copy-paste lineage between the two.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** No company scoping at all: the company code is passed to the underlying query but never actually used to filter it. Since GL account codes are only unique within a company, the same code string could exist under more than one company's Chart of Accounts — if it does, this report silently pulls in and sums amounts from every company that reuses that code, not just the logged-in user's. The report header only ever shows one company's name, so a cross-company leak would look like a completely normal single-company report.
- **Critical:** No "posted only" filter: unlike most other ledger-style reports in this system, this one has no check excluding un-finalized vouchers — only a date-range check. Cost-center subtotals can include amounts from vouchers that have been saved but not yet posted, overstating activity versus a posted-only ledger.
- **Warning:** The identical pair of bugs above (no company filter, no posted-only filter) also exists in the sibling Cost Center wise Ledger Summary report — looks like shared lineage rather than two independent defects, worth fixing together.
- **Warning:** Two real filter parameters (single cost center, single company) are supported by the underlying query but never wired up anywhere in the UI or the calling code — permanently unreachable capability.
- **Minor:** The join between voucher lines and cost centers is written as an outer join but is functionally forced back into an inner join by an extra condition elsewhere in the same query — in practice this rarely matters, but a voucher line with a broken cost-center reference would silently vanish from the report rather than showing up as "Unknown."

## Unused Columns

Not applicable — this report has no distinct staging table of its own; it's a single ad-hoc query streamed straight into the printed report, and every column it selects is actually printed.

## Routing (mvc:/api: — omitted, confirmed why)

No `mvc:`/`api:` added to front-matter. This screen (`legerCostCenter` state, `Client\app\config.accountingRoute.js:339-353`) renders into `data-ui-view="legerCostCenter"` inside `Views\AccountingReport\Index.cshtml:18` — the SAME shell page (`AccountingReportController.Index()`) also hosts `ledgerReport`, `controlLedgerReport`, `costCenterLeger`, `receivePaymentReport` and ~9 other report states (`Index.cshtml:5-20`). It is a shared multi-report shell, not a per-screen MVC action, so recording `mvc: AccountingReportController.Index` here would be misleading. The screen's own content and export actions — `_LegerCostCenter()` (partial view) and `LedgerCostCenterReport(...)` (the actual export, `AccountingReportController.cs:417-429`) — are plain conventional MVC actions; the controller has no `[RoutePrefix]`/`[Route]`/`[HttpX]` attribute anywhere, so there is no Web API route to put in `api:` either.
