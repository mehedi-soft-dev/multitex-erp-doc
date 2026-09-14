# Feature: Stock Closing

```yaml
---
id: feat:acc-stock-closing
module: accounting
category: transaction
models: [ACC_STOCK_CLOSING]
mvc: StockClosingController.Index
api: [GET api/accounting/stock-closings/get-stock-closings -> StockClosingsController.GetMonthlyStockClosing, POST api/accounting/stock-closings/save-stock-closing -> StockClosingsController.SaveMonthlyStockClosing, POST api/accounting/stock-closings/save-monthly-stock-ledger -> StockClosingsController.SaveMonthlyStockClosingToAccounts]
tables: [ACC_STOCK_HISTORY, ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

A month-end process bundling two actions into one screen: (1) record the closing stock value for
a company/year/month, one row per "stock" GL account, and (2) post it to the ledger, generating a
**closing voucher** (dated the last day of the month) and a companion **opening voucher** (dated
the first day of the next month).

The set of "stock" accounts isn't owned by this screen — it's every Chart-of-Accounts GL account
whose Main Class rolls up to a configurable "stock" category, driven by a system parameter. There
is no inventory/warehouse module link at all, despite the name: this is purely a GL-value entry
screen (one number per stock-related account per month), not a feed from a physical stock
subsystem.

**Naming mismatch:** the C# model class is called `ACC_STOCK_CLOSING` and even uses a sequence
named `ACC_STOCK_CLOSING_SEQ` — but there is no `ACC_STOCK_CLOSING` table. The actual table is
`ACC_STOCK_HISTORY`, confirmed as the real, heavily-used table by four separate financial reports
(Balance Sheet, Trial Balance, opening-balance, and Profit & Loss procedures).

**The "Finalize"/Post button is currently commented out of the UI.** The JS handler, API route,
BLL method, and both posting stored procedures remain fully wired and reachable directly — there
is just no way to trigger posting from the visible screen today. Whether this is deliberate or a
regression isn't determinable from the code alone.

**Screen path:** Accounting > Transaction > Stock Closing

## Fields

| Filter | Meaning |
|---|---|
| Company | Which company's stock history to view. |
| Year / Month | Calendar year/month — not tied to the Fiscal Year table at all. |

| Grid column (one row per stock GL account) | Editable? | Meaning |
|---|---|---|
| Code / Particular | No | The 3-part Chart-of-Accounts code and account name. |
| **Closing** | **Yes** — the only genuinely editable field | The month-end stock value the accountant enters. |
| Total (footer) | Computed client-side only | Sum of all Closing values currently on screen — not re-validated against the database. |

Several fields round-trip on the model but are always zero and never shown (Opening, Dr, Cr,
Balance, Net Amt) — they look like leftovers from a richer stock-ledger view that was never
finished. A "finalized" flag exists on the data and is even read back by the app, but nothing in
the UI displays it — there's no visual indicator of which months are already posted.

When the (currently unreachable) posting action runs, it writes a closing voucher and an opening
voucher into the same tables the Voucher screen uses: voucher number prefixed `STC-`/`STO-`, both
hardcoded to voucher type 5, cost center forced to the "N/A" sentinel, and payment mode always
defaulting to a blank/zero value (see Known Issues — despite an existing cross-reference elsewhere
describing this as "passing the payment mode through," it does not).

## Relationships

The Chart of Accounts (accounts flagged as "stock" via a system parameter) populates the grid on
this screen, whose entries live in `ACC_STOCK_HISTORY`. Posting (currently unreachable from the
UI) generates records in `ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` (closing + opening voucher).

`ACC_STOCK_HISTORY` is read by:
- Balance Sheet report
- Trial Balance report
- Opening-balance procedure
- Profit & Loss calculation

Every generated voucher line hardcodes the Cost Center to the "N/A" sentinel — this screen never
lets the user pick a real cost center. Payment Mode is not genuinely used despite an existing note
elsewhere describing it as passed through (see Known Issues).

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The month-end posting voucher is always written against a hardcoded company constant, never the company actually selected on screen. In any multi-company deployment where that constant isn't the active company, this either silently posts into the wrong company's ledger or fails outright.
- **Critical:** No company/ownership enforcement on Save at all — the line that would set the company code from the trusted server-side context is commented out, so the company code persisted is whatever the client sends. A direct API call bypassing the UI can write a stock-history row for any company/account combination.
- **Critical:** SQL-injection-shaped raw string formatting on Save: the insert/update statement is built by directly interpolating client-supplied values (including the account codes and the company code) into the SQL text, with no bind parameters at all — and unlike some other instances of this pattern elsewhere in the codebase, none of these interpolated values are numeric-only.
- **Critical:** Inconsistent company key between the read side and the post side: the screen's data source joins by one company identifier, but the posting procedures (and every downstream financial report) filter by a different one. Values entered under one key can become invisible to, or get silently wiped by, logic keyed off the other.
- **Warning:** The read query has no company-code scoping whatsoever, relying solely on the other company identifier, which compounds the inconsistent-key issue above.
- **Warning:** A session value is read with no null check on every load of this screen — a missing/expired session throws an unhandled exception rather than a clean auth error.
- **Warning:** The "stock accounts" lookup function is named as if it supports a list of main-class categories, but the query that consumes it does a plain equality check, not a set membership check — if ever configured with more than one category, this would silently exclude stock accounts from the screen rather than including all of them.
- **Minor:** The Finalize button is commented out of the UI, but the entire posting pipeline behind it remains reachable via direct API call — not evidenced whether this is deliberate or a regression.
- **Minor:** The closing and opening vouchers this screen generates share the same numbering sequence space as manually-entered vouchers, and are both tagged with the same voucher type — they're only distinguishable from each other by their number prefix, not by type.
- **Minor:** The internal "row id" used by this screen isn't a real database key at all — it's overwritten client-side with a simple loop counter used only for keyboard-focus handling, and must never be treated as a real identifier by any future code.

## Unused Columns

| Field | Verdict |
|---|---|
| Opening / Dr / Cr / Balance / Net Amt (view-model fields) | Unused / always zero — hardcoded to 0 by the read query, never displayed by the screen. |
| Row id (view-model field) | Not a real identifier anywhere — overwritten client-side with a loop index, used only as a DOM anchor. |
| "Finalized" flag | Read but never displayed — the screen has no visual indicator of which periods are already posted. |
| Company code (view-model field) | Present on the model but never populated server-side on Save (the assignment is commented out) — whatever the client sends is what gets persisted. |
| `ACC_STOCK_HISTORY.HR_COMPANY_ID` | Write-only from the posting path's perspective — neither posting procedure filters or reads it; only the entry screen's own read query uses it. |
| `ACC_STOCK_HISTORY.IS_FINALIZE` | Set by the app/procedures but never read back into any UI element — state that's invisible to the end user. |
