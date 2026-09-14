# Feature: Bank Reconciliation

```yaml
---
id: feat:acc-bank-reconciliation
module: accounting
category: transaction
mvc: BankReconcilationController.Index
api: [GET api/accounting/voucher-masters/get-bank-reconcile-vouchers -> VoucherMastersController.GetBankReconsileVouchers, PUT api/accounting/voucher-masters/update-bank-date -> VoucherMastersController.UpdateBankDate]
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Bank Reconciliation is not a separate document type — it is a filtered, mostly read-only view over
the same `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL` tables that the Voucher screen writes to,
narrowed to **posted** vouchers whose lines touch one bank ledger account, plus a single-column
update action (`BANK_DATE`) per voucher. There is no dedicated reconciliation table, no separate
detail rows, and no new voucher type — it is a query plus one `UPDATE ... SET BANK_DATE=...`
statement against the existing voucher tables.

Screen path: Accounting > Transaction > Bank Reconciliation.

Workflow: pick a Company, a From/To date range, a single Bank (a GL account head, via typeahead),
and a Cleared/Pending status filter. **Show** loads posted vouchers hitting that bank account
within the date window, together with a running Book Balance, Bank Balance, and the difference
between them ("Amount Not Reflect In Bank"). For each row the user types a Bank Date (when it
actually cleared on the bank statement) and clicks Update, or Bulk Update to push every row with a
date typed in.

Reconciled = has a `BANK_DATE`, nothing more. There is no separate reconciliation record, batch,
or statement entity anywhere in the schema.

## Fields

There is no add/edit form in the usual sense — a filter bar plus a results grid where one column
(Bank Date) is directly editable per row.

| Filter | Meaning |
|---|---|
| Company | Which company's vouchers to reconcile (already scoped to the logged-in user's assigned companies). |
| From / To | Reconciliation date window. |
| Bank | The single GL bank account being reconciled, picked via typeahead. Only one bank at a time. |
| Status | Cleared (has a BANK_DATE in range) vs Pending (doesn't yet). |

| Grid column | DB Column | Editable? | Meaning |
|---|---|---|---|
| Voucher No / Cheque No / Type / Date | `VOUCHER_NO` / `CHQ_NO` / type name / `POST_DATE` | No | Same voucher shown on the Voucher screen. |
| Dr / Cr | Summed `ACC_VOUCHER_DETAIL.DR_AMT`/`CR_AMT` for lines matching the selected bank | No | The amount this voucher moved against the chosen bank account. |
| **Bank Date** | `ACC_VOUCHER_MASTER.BANK_DATE` | **Yes** | The date this transaction actually cleared the bank statement. This is the entire "reconciliation" action. |

Totals row: Book Balance, Bank Balance, and their difference — all computed server-side per
request, not stored. Only posted vouchers (`IS_POSTED='Y'`) are reconcilable at all.

Several fields the underlying query fetches (POST_ID, DESCRIPTION, CHQ_DATE, the bank account's
display name, the company name) are shipped to the browser but never actually bound to anything
on screen — pure bandwidth overhead, the same over-fetching pattern seen elsewhere in this
codebase.

## Relationships

`ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` are the same tables used by the Voucher screen;
`BANK_DATE` is read and written here.

Also connects to:
- Chart of Accounts (bank account picked via typeahead)
- Bank Book (Currency) report — the one confirmed downstream reader of BANK_DATE, showing
  "Cleared" once set
- A separate print/export report package (drifts independently from the on-screen grid's query)

The plain (non-currency) Bank Book report does NOT read BANK_DATE at all — only the currency
variant reflects reconciliation status. Payment Mode is not read by this screen at all, even
though bank-type vouchers are exactly the ones that would have a payment mode set on entry.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The bank-date update has no company/ownership scoping whatsoever: the stored procedure accepts a company-code parameter but never references it in its UPDATE statement, and the C# repository does not even pass one. Any authenticated user who can guess/enumerate a voucher ID can set or overwrite the bank-clearing date of any voucher in any company, not just their own.
- **Critical:** Reconciling is one-way and destructive, with no audit trail: the update simply overwrites BANK_DATE with no history table and no "reconciled by / reconciled date" columns. Once set (or accidentally cleared, since an empty value can be sent), there is no record of who reconciled it, when, or what the previous value was, and no UI affordance to intentionally un-reconcile.
- **Critical:** No transaction/atomicity across Bulk Update: it loops over every row with a date typed in and fires one independent request per row, with no batch endpoint and no aggregated success/failure summary. If one row fails partway through, earlier rows are already committed and removed from the grid while later ones keep firing — there is no single place to see which ones actually saved.
- **Warning:** The client-side "don't backdate before the voucher date" guard is enforced nowhere on the server — combined with the missing company scope above, this is entirely bypassable via a direct API call.
- **Warning:** No optimistic-concurrency check between loading the grid and updating a row: two users (or one user with two tabs) reconciling overlapping date ranges can silently overwrite each other's bank date for the same voucher with no conflict warning.
- **Warning:** Only one bank account can be reconciled at a time, with no multi-select — the accountant must repeat Show/reconcile/Show per bank account.
- **Warning:** Two divergent stored-procedure sources feed the on-screen grid vs. the printed export — a future change to one filter/join will not automatically propagate to the other, so the printed report can show different rows than what is currently on screen.
- **Minor:** A dead alternate print/report code path exists (an older report action no longer wired to any button) — the same "leftover duplicate implementation" pattern already seen on the Voucher and Draft Voucher screens.
- **Minor:** The bank date is sent to the server as a pre-formatted display string rather than an unambiguous ISO date — works today but is a fragile, locale-dependent format.
- **Minor:** Leftover copy-pasted demo boilerplate sits unused in the controller's view-model — harmless, but confusing dead state.

## Unused Columns

This screen does not introduce or touch any column beyond what is already audited on the
Voucher page. `BANK_DATE` itself is **not** unused — it is the one column this entire screen
exists to write, and it has a confirmed downstream reader (the Bank Book Currency report's
"Cleared" status label), so it does not qualify as write-only/dead the way some other Voucher
columns do.

The only screen-specific waste is payload over-fetching (several fields selected by the query but
never bound to anything in the view) — recorded under Known Issues rather than here, since these
are call-site inefficiencies, not genuinely dead schema columns.
