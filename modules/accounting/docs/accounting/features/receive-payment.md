# Feature: Receive Payment

```yaml
---
id: feat:acc-receive-payment
module: accounting
category: reports
tables: [ACC_REPORT_RECEIVEPAYMENT, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Receive Payment (Accounting > Reports > Receive Payment) is not what the name suggests. This is not a list of individual receipt/payment transactions, and it has no relationship to Payment Mode or to the Bill-settlement sub-flow documented on the Voucher page. It is a Cash & Bank ledger movement summary.

Table: `ACC_REPORT_RECEIVEPAYMENT` (shared staging table).

A date-ranged export showing the net movement of every Cash & Bank GL account between a From and To date, split into two columns: Received (opening balance of Cash & Bank, plus any account whose balance fell over the period) and Payment (any account whose balance rose over the period, plus the closing balance). Each account appears once, in whichever side its *net* movement falls on — not a transaction-by-transaction list.

## Fields

This report has no add/edit form — just filter criteria and printed output columns.

### Filters

Only two filters exist: From Date and To Date. There is no company selector (moot — see Known Issues), no account filter, and no way to scope to a specific Cash/Bank account.

### Output columns

| Output column | Meaning |
|---|---|
| Account name | The specific Cash/Bank sub-ledger account. |
| Amount | Net Dr−Cr for that account over the period, shown positive, bucketed to Received or Payment by the sign of the net movement. |
| Group heading | Account-class grouping (e.g. "Cash in Hand", "Bank Balance"). |
| Opening / Closing Balance rows | Total Cash & Bank position as of the day before the period starts / as of the period's end date. |

## Relationships

`ACC_VOUCHER_DETAIL` (Cash & Bank class accounts only) writes into a shared staging table, `ACC_REPORT_RECEIVEPAYMENT`, which is read back with no filter at all to produce the printed report.

Confirmed: no Payment Mode column and no Bill-settlement column is referenced anywhere in the underlying query — despite the similar name, this is unrelated to those flows.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The result set has no filter at all — not by user, not by company. Combined with a cleanup step that only ever clears one hardcoded user id (not the actual caller), every run of this report accumulates rows in a shared physical table and returns everything ever inserted by every user, in every company, since the app was last cleaned — not just the requested date range. In practice this can surface other companies' Cash & Bank figures alongside the real result.
- **Critical:** The company used is a hardcoded constant, not the logged-in user's actual company — every export of this report, for every user in every company, queries the same fixed company only. (This same constant is reused by nearly every action in the reports controller, so it's a systemic issue, not unique to this report — but it directly breaks multi-company use here.)
- **Critical:** No isolation between concurrent runs: because the staging table is one shared physical table rather than a per-session scratch area, two people running this report at the same time can have their writes interleave and corrupt each other's results, independent of the two bugs above.
- **Warning:** "Received" vs "Payment" is a net bucket per account for the whole period, not a transaction list — an account with heavy receipts and heavy payments during the period nets out to one figure in one bucket, which can be misleading despite the report's name implying an itemized receipts-and-payments statement.
- **Warning:** Opening/Closing balance rows are unconditionally bucketed to a fixed side regardless of sign — an overdrawn Cash & Bank position would still display under "Opening Balance" on the Received side with whatever raw sign the calculation produced, with no normalization.
- **Warning:** No server-side validation of the date range at all — an end date before the start date is not rejected before hitting the database.
- **Minor:** Typo in the on-screen caption ("Receive Paymenet").

## Unused Columns

Of the 15 columns in the report dataset, 3 are fetched every run but never actually displayed: a user-id column (exists only to scope the staging table, and that scoping is itself broken — see Known Issues), a company-code column (only the company name is shown, looked up separately), and the company's address (fetched every run, never printed anywhere on the report).

## Routing (mvc:/api: — omitted, confirmed why)

No `mvc:`/`api:` added to front-matter. This screen (`receivePaymentReport` state, `Client\app\config.accountingRoute.js:454-467`) renders into `data-ui-view="receivePaymentReport"` inside `Views\AccountingReport\Index.cshtml:16` — the SAME shell page (`AccountingReportController.Index()`) also hosts `ledgerReport`, `legerCostCenter`, `costCenterLeger` and ~9 other report states (`Index.cshtml:5-20`). It is a shared multi-report shell, not a per-screen MVC action, so `mvc: AccountingReportController.Index` would be misleading. The screen's own content/export actions — `_ReceivePayment()` (partial view) and `ReceivePaymentReport(...)` (the actual export, `AccountingReportController.cs:248-270`) — are plain conventional MVC actions; the controller has no `[RoutePrefix]`/`[Route]`/`[HttpX]` attribute anywhere, so there is no Web API route for `api:` either.
