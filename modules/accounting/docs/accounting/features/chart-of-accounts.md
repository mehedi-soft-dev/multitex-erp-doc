# Feature: Chart of Accounts

```yaml
---
id: feat:acc-chart-of-accounts
module: accounting
category: master-data
service: UnilayerChartofAccountService
procedure: PKG_ACCOUNTING.acc_gl_account_head_filter | acc_ac_class_insert | acc_map_class_select
mvc: UnilayerChartOfAccountController.Index
api: [GET api/accounting/unilayer-chart-of-accounts/get-chart-of-accounts -> UnilayerChartOfAccountsController.GetChartOfAccounts, GET api/accounting/unilayer-chart-of-accounts/get-control-chart-of-accounts -> UnilayerChartOfAccountsController.GetThreeLayerChartOfAccounts, POST api/accounting/unilayer-chart-of-accounts/save-chart-of-accounts -> UnilayerChartOfAccountsController.SaveChartOfAccounts, PUT api/accounting/unilayer-chart-of-accounts/update-chart-of-accounts -> UnilayerChartOfAccountsController.UpdateChartOfAccounts, GET api/accounting/unilayer-chart-of-accounts/get-account-heads -> UnilayerChartOfAccountsController.GetAccountHeards, GET api/accounting/unilayer-chart-of-accounts/get-account-main-heads -> UnilayerChartOfAccountsController.GetMainClassHeads, GET api/accounting/unilayer-chart-of-accounts/get-cash-account-heads -> UnilayerChartOfAccountsController.GetCashGlHeads, GET api/accounting/unilayer-chart-of-accounts/get-bank-account-heads -> UnilayerChartOfAccountsController.GetBankGlHeads, GET api/accounting/unilayer-chart-of-accounts/get-bank-account-heads-auto -> UnilayerChartOfAccountsController.GetBankGlHeadsAuto, GET api/accounting/unilayer-chart-of-accounts/check-gl-transaction -> UnilayerChartOfAccountsController.CheckGlTransactionExist, DELETE api/accounting/unilayer-chart-of-accounts/delete-gl-account -> UnilayerChartOfAccountsController.DeleteGlAccount, GET api/accounting/unilayer-chart-of-accounts/get-acc-main-class -> UnilayerChartOfAccountsController.GetAccMainClass, GET api/accounting/unilayer-chart-of-accounts/get-acc-map-class4change-grp -> UnilayerChartOfAccountsController.GetAccMapClass4ChangeGrpList, POST api/accounting/unilayer-chart-of-accounts/save-acc-map-class4change-grp -> UnilayerChartOfAccountsController.SaveAccMapClass4ChangeGrp]
tables: [ACC_AC_PARENT_CLASS, ACC_AC_CLASS, ACC_MAIN_CLASS, ACC_MAP_CLASS, ACC_SUB_CLASS, ACC_VOUCHER_DETAIL, ACC_DRAFT_VOUCHER_DETAIL]
models: [ACC_MAIN_CLASSModel]
status: verified
---
```

## Overview

Chart of Accounts (Accounting > Chart of Account) is the accountant's master list of every GL
(General Ledger) account — e.g. "Cash in Hand", "Bank - City Bank", "Salary Expense". Every
voucher/transaction picks one of these accounts. It's organized as a 5-level tree (see Fields),
shown as an expandable tree on screen, starting from the 5 fixed top-level groups (Assets,
Liabilities, Income, Expenditure, Equity) down to the actual account you post transactions
against.

**Two versions of this screen exist in the code.** `UnilayerChartOfAccount*` is active — the
real screen, with full create/edit/delete, a check that an account has transactions before
allowing delete, and export to PDF/Excel. `ChartOfAccount*` is dead/abandoned — the form still
renders, but Save/Update do nothing (server-side code commented out) and Delete just shows a
placeholder popup. Confusingly, the dead `ChartOfAccountService`/`ChartOfAccountRepository` is
still used internally by the active screen for one feature ("Change Parent Group") — so it can't
be deleted outright even though it looks unused. See Known Issues.

## Fields

### The 5-level hierarchy

Each level narrows down to the next, ending in the actual GL account used on a voucher.

| Level | Code | Table | What it represents | Real example (from `mtexdev`, company `001`) | Editable from the UI? |
|---|---|---|---|---|---|
| 1. Parent Class | `T` | `ACC_AC_PARENT_CLASS` | The 5 fixed top-level groups | **ASSETS** *(others: LIABILITIES, INCOME, EXPENDITURE, EQUITY)* | No (view only) |
| 2. Account Class | `A` | `ACC_AC_CLASS` | Sub-category within a Parent Class | **CURRENT ASSET** (code `102`) *(siblings under Assets: NON CURRENT ASSET `101`)* | No (view only — the save procedure for this level has a bug, see Known Issues) |
| 3. Main Class | `M` | `ACC_MAIN_CLASS` | Broad group under an Account Class | **Accounts Receivables** (code `10203`) | Yes |
| 4. Map Class | `N` | `ACC_MAP_CLASS` | Sub-group under a Main Class | **Accounts Receivable-Garments** (code `0001`) | Yes |
| 5. Sub Class (GL Account) | `G` | `ACC_SUB_CLASS` | The actual account posted to on a voucher | **Styletex Limited** (code `102030009`) | Yes (only level with a real "is this account in use?" check before delete) |

So a real full chain looks like: **ASSETS → CURRENT ASSET → Accounts Receivables → Accounts
Receivable-Garments → Styletex Limited**.

The GL account code (`SUB_CODE`) is built from the chain itself: `102030009` = `MAIN_CODE`
(`10203`) + a 4-digit running number (`0009`) — this is why every level down to Main Class
carries a short numeric code that the leaf account code is built on top of.

Data-quality note found while checking this: a few `ACC_SUB_CLASS` rows have `COMP_CODE` as
`NULL` (e.g. accounts "Surma Garments Limited.", "TEDDY S.P.A") instead of `001` — worth a look
since `COMP_CODE` is supposed to scope every record to a company.

`T`/`A`/`M`/`N`/`G` are the internal codes the app uses to know which tree level a node/form
belongs to — you'll see them in the code as `controlCode`.

### Add/Edit form (on the tree screen)

| Frontend Label (raw) | Bound To | Input Type | Required? | Meaning |
|---|---|---|---|---|
| Parent | `vm.chartOfAccount.parentCode` | Text (read-only) | — | Shows which node you're adding under. Set automatically, not typed. |
| Code | `vm.chartOfAccount.code` | Text (read-only) | — | Auto-generated account code. |
| Name | `vm.chartOfAccount.text` | Text | Yes | The name of this Main Class / Map Class / GL Account. |
| " Vouchar For Type" *(typo in source, extra leading space)* | `vm.chartOfAccount.LK_VOUCHER_FOR_TYPE_ID` | Dropdown | No | Only shown for Map Class / GL Account levels. Links this account to a voucher-for category. |

Buttons: Add, Update, Clear, Delete (disabled if the account has existing transactions), Change
Parent (only for GL Account level — moves an account under a different Map Class), and an export
menu (Pdf / Excel).

### Columns actually used per table (List / Add / Edit)

Only the columns the app's code actually reads or writes — not every column that exists in the
table.

**`ACC_AC_PARENT_CLASS`** — read-only, no Add/Edit in the UI.
| Column | Used for |
|---|---|
| `ACC_AC_PARENT_CLASS_ID` | Identifies the row |
| `NAME` | Display name (e.g. "ASSETS") |
| `PARENT_CODE` | Sort/grouping code |
| `COMP_CODE` | Company scope |

**`ACC_AC_CLASS`** — read-only in the UI (Save exists in the stored procedure but has a bug — not usable).
| Column | Used for |
|---|---|
| `ACC_AC_CLASS_ID` | Identifies the row |
| `ACC_AC_PARENT_CLASS_ID` | Which Parent Class this belongs to |
| `AC_CODE` | Short numeric code (e.g. `102`) |
| `CLASS_NAME` | Display name (e.g. "CURRENT ASSET") |
| `AC_GROUP` | Grouping code |
| `COMP_CODE` | Company scope |

**`ACC_MAIN_CLASS`** — Add/Edit/Delete all work.
| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `ACC_MAIN_CLASS_ID` | ✅ | (auto) | ✅ (key) | |
| `ACC_AC_CLASS_ID` | ✅ | ✅ | — | which Account Class this sits under |
| `AC_CODE` | ✅ | ✅ | — | inherited from the Account Class |
| `MAIN_CODE` | ✅ | (auto-generated) | — | e.g. `10203` |
| `MAIN_NAME` | ✅ | ✅ | ✅ | the only field the user actually types |
| `COMP_CODE` | ✅ | ✅ | — | company scope |

**`ACC_MAP_CLASS`** — Add/Edit/Delete all work; also updated by "Change Parent Group".
| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `ACC_MAP_CLASS_ID` | ✅ | (auto) | ✅ (key) | |
| `ACC_MAIN_CLASS_ID` | ✅ | ✅ | — | which Main Class this sits under |
| `MAP_CODE` | ✅ | (auto-generated) | — | e.g. `0001` |
| `MAP_NAME` | ✅ | ✅ | ✅ | the only field the user actually types |
| `PRNT_CODE` | ✅ | ✅ | — | parent's code, copied down |
| `AC_CODE`, `MAIN_CODE` | ✅ | ✅ | — | inherited from parent levels |
| `COMP_CODE` | ✅ | ✅ | — | company scope |

**`ACC_SUB_CLASS`** — the actual GL account; Add/Edit/Delete work, plus a real in-use check before delete.
| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `ACC_SUB_CLASS_ID` | ✅ | (auto) | ✅ (key) | |
| `ACC_MAP_CLASS_ID` | ✅ | ✅ | — (changed only via "Change Parent Group") | which Map Class this sits under |
| `SUB_CODE` | ✅ | (auto-generated) | — | e.g. `102030009` |
| `SUB_NAME` | ✅ | ✅ | ✅ | the account name — the only field the user actually types |
| `AC_CODE`, `MAIN_CODE`, `MAP_CODE`, `MCODE`, `SL` | ✅ | ✅ | — | inherited/derived codes from parent levels |
| `IS_DUMMY` | ✅ | ✅ | ✅ | marks a placeholder/non-postable account |
| `IS_CHECK_BAL` | — | — | — | drives whether the account's running balance is shown (used in reports/autocomplete, not this form) |
| `IS_EXCLUDE4AUDIT` | — | — | — | excludes the account from audit reports |
| `LK_NATURE_ID` | ✅ (join) | — | — | links to a "nature" lookup, used to scope GL search by company via `HR_COMPANY` |
| `COMP_CODE` | ✅ | ✅ | — | company scope — sometimes NULL, see Known Issues |

## Relationships

The 5 levels feed into each other top-down, and the bottom level (the actual GL Account) is what
every voucher and every accounting report ultimately points to:
Parent Class → Account Class → Main Class → Map Class → GL Account (Sub Class), which then feeds
the Voucher entry screen (Account Head picker), the Draft Voucher entry screen, the Ledger
Report, and the Accounting Reports (cash book, bank book, trial balance...).

| Related Table / Module | Relationship | Where it's used | Why |
|---|---|---|---|
| Voucher entry screen | GL Account picked via autocomplete | Voucher line entry | User selects which account a transaction line hits. |
| Draft Voucher entry screen | Same GL Account picker | Draft voucher line entry | Same as above, before the voucher is finalized. |
| Ledger Report | GL Account filter | Report screen | User picks an account to see its transaction history. |
| Accounting Reports (cash book, bank book, etc.) | Joined through all 5 levels | Report generation | Reports group/subtotal transactions by Main Class / Map Class, so they trace back through the whole hierarchy. |

Technical reference (file : line): Voucher entry (Account Head autocomplete)
`Client\app\controllers\voucherMastersController.js:7-8,625-663` — calls `GetAccountHeards`;
Draft voucher entry `Client\app\controllers\draftVouchersController.js:476,506`; Ledger report
`Client\app\controllers\ledgerReportController.js:28`; Accounting report
`Client\app\controllers\accReportController.js:79` → `accRptDataService.js:7-12`; Account Head
API `Api\UnilayerChartOfAccountsController.cs` → `get-account-heads` →
`UnilayerChartofAccountService.GetAccountHeards`; GL account head search (stored proc)
`PKG_ACCOUNTING.acc_gl_account_head_filter`, `PKG_ACCOUNTING.sql:1529-1570`; Delete-guard (does
this account have transactions?) `ERP.Data\VoucherMasterRepository.cs:500-508` — checks
`ACC_VOUCHER_DETAIL` / `ACC_DRAFT_VOUCHER_DETAIL` by `SUB_CODE`; Reports joining all 5 levels
`PKG_ACCOUNTING.sql` lines ~907-939, 967-994, 1115-1289.

## Known Issues

- **Delete-guard ignores company scoping**: `VoucherMasterRepository.CheckGlTransactionExist`
  (the check that blocks deleting a GL account still in use) filters only by `SUB_CODE` — the
  `compCode` parameter is passed in but never actually used in the SQL. Since account codes
  aren't guaranteed unique across companies, this can wrongly block a delete (false match in
  another company) or, in principle, miss a real usage. (Source:
  `ERP.Data\VoucherMasterRepository.cs:500-508`.)
- **Chart of Accounts Class-level save has a column mix-up (stored procedure bug)**:
  `acc_ac_class_insert` inserts the new sequence ID into the `COMP_CODE` column and the caller's
  ID into the `ACC_AC_CLASS_ID` column — the values are shifted by one position. `pCOMP_CODE` is
  never actually used. Currently dormant — no C# code calls this procedure (the corresponding
  `Save()` method throws `NotImplementedException`) — but it's a live trap if someone wires it up
  later. (Source: `PKG_ACCOUNTING.sql:2123-2147`.)
- **GL account search not scoped by company**: `acc_gl_account_head_filter` option 3000 (the
  default path) has no company filter at all, unlike its sibling option 3001 which correctly
  joins `HR_COMPANY`. Same for `acc_map_class_select` option 3000. (Source:
  `PKG_ACCOUNTING.sql:1535-1549`, `4455-4465`.)
- **Deleting a Main Class or Map Class can orphan its children**: `MainClassRepository.Delete`
  and `MapClassRepository.Delete` both run a raw `DELETE ... WHERE <id>=...` with no check for
  existing child rows (a Main Class's Map Classes, or a Map Class's GL Accounts) and no company
  filter. Only the leaf-level GL Account delete has a real "is this in use?" check.
- **Confusing duplicate feature**: the old `ChartOfAccount*` MVC/API/Angular screen is dead
  (Save/Update commented out, Delete is a stub popup), but its backing service/repository is
  still quietly used by the active screen's "Change Parent Group" feature — so a future cleanup
  could break a live feature by deleting what looks like dead code.
- **SQL built by string concatenation**: several class-repository methods
  (`AccountClassRepository.GetAll`, `MainClassRepository.IsMainClassExist`,
  `MapClassRepository.IsMapClassExist`, `SubClassRepositroy.IsSubClassExist`/`Delete`) build SQL
  by directly inserting values into the query text rather than using parameters — a
  SQL-injection-shaped pattern, even though today's inputs come from internal validated fields.
- **Not implemented**: `UnilayerChartofAccountService.GetMainClassHeads` throws
  `NotImplementedException` — its API route (`get-account-main-heads`) would fail with a server
  error if ever called (nothing currently calls it).
- **Minor UI text issues**: the "Vouchar For Type" label has a typo and a stray leading space;
  the "Change Parent Group" popup's dropdown placeholder says "-- Select Floor --" even though
  it's picking an accounting group, not a floor — looks like copy-pasted text from an unrelated
  HR screen.
- **Data quality: some GL accounts have a NULL `COMP_CODE`** — confirmed by querying
  `ACC_SUB_CLASS` on `mtexdev` (company `001`): rows like "Surma Garments Limited.", "TEDDY
  S.P.A" have `COMP_CODE = NULL` instead of `001`, even though every other row in the same Map
  Class correctly has `001`. Since `COMP_CODE` is meant to scope every record to its company, any
  code that filters strictly by `COMP_CODE='001'` will silently skip these rows.

## Unused Columns

How this was checked: every column of the 5 tables was grepped (whole word, case-insensitive)
across both repos — this app and the Oracle package source
(`MultitechERP/src/ERPSolution/oracle/packages`) — looking for any real read/write beyond the
column's own declaration. No `CREATE TABLE` DDL exists in either repo; column lists are
reconstructed from the fullest `INSERT`/`SELECT` statements plus the C# model classes.

**`ACC_AC_PARENT_CLASS`** — no unused columns. All 4 columns
(`ACC_AC_PARENT_CLASS_ID`, `COMP_CODE`, `NAME`, `PARENT_CODE`) are used, including in Balance
Sheet / Income Statement report rollups. Confidence: medium (read-only table, no INSERT to
cross-check against — can't fully rule out a column with zero footprint anywhere).

**`ACC_AC_CLASS`** — no unused columns. All 6 columns used, including `AC_GROUP` which drives
Balance Sheet/Income Statement report grouping (`rptBalanceSheet.rdlc`,
`rptIncomeStatementDetail.rdlc`). Confidence: high.

**`ACC_MAIN_CLASS`** — no unused columns. All 6 real columns used. Note: `CTRL_GRP` and
`DISP_MAIN_NAME` appear as properties on `ACC_MAIN_CLASSModel.cs`, but they are not real
persisted columns — they only ever show up as computed literal/expression aliases inside one
report query (`'M' as CTRL_GRP`, `mc.MAIN_NAME||' << '||ac.CLASS_NAME as DISP_MAIN_NAME`, the
GL-account-search autocomplete `acc_gl_account_head_filter`). They're never part of any
`INSERT`/`UPDATE` into `ACC_MAIN_CLASS`.

**`ACC_MAP_CLASS`**

| Column | Verdict | Confidence |
|---|---|---|
| `PRNT_CODE` | Write-only / effectively unused. Written on insert and round-tripped through `MapClassRepository.cs`, but the only place that ever assigned it a real value is commented out (`ERP.BLL/UnilayerChartofAccountService.cs:248` → `//PRNT_CODE = "0000",`). No Angular/JS view reads or binds it. Always inserted as `NULL` in practice. | Medium-High |
| `CTRL_GRP` | Same situation as on `ACC_MAIN_CLASS` — a computed literal (`'N' as CTRL_GRP`) in the GL-account autocomplete report, not a real inserted/updated column. Not a genuine dead-column case. | — |

All other columns (`ACC_MAP_CLASS_ID`, `ACC_MAIN_CLASS_ID`, `MAP_CODE`, `MAP_NAME`, `AC_CODE`,
`MAIN_CODE`, `COMP_CODE`) are actively used.

**`ACC_SUB_CLASS`**

| Column | Verdict | Confidence |
|---|---|---|
| `MCODE` | Write-only / effectively unused. Inserted (`pMCODE`) and round-tripped through `SubClassRepositroy.cs`, but zero other reference exists anywhere in either repo — no WHERE clause, no report, no other stored procedure, no Angular/JS view. | High |
| `SL` | Write-only / effectively unused. Same pattern as `MCODE` — inserted, round-tripped, never read for any real purpose. (Unrelated `SL` hits found elsewhere in the codebase are `ROWNUM as SL` aliases in dye/production reports — a different feature, not this column — and a Cost Center Group grid column labeled "SL", a UI coincidence, not `ACC_SUB_CLASS.SL`.) | High |

All other columns (`IS_DUMMY`, `IS_CHECK_BAL`, `IS_EXCLUDE4AUDIT`, `LK_NATURE_ID`, plus the
code/name columns) are genuinely used — form fields, report/autocomplete filters, or the
company-scoping join.

**Summary**

| Table | Column | Status | Confidence |
|---|---|---|---|
| `ACC_MAP_CLASS` | `PRNT_CODE` | Write-only / effectively unused | Medium-High |
| `ACC_SUB_CLASS` | `MCODE` | Write-only / effectively unused | High |
| `ACC_SUB_CLASS` | `SL` | Write-only / effectively unused | High |

Caveat: because no `CREATE TABLE` DDL exists in either repo, this audit can only catch columns
that leave *some* trace (an INSERT list, a SELECT, a model property). A column with literally
zero footprint anywhere in either repo is invisible to this method by construction.
