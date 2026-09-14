# Feature: Voucher

```yaml
---
id: feat:acc-voucher
module: accounting
category: transaction
mvc: VoucherMasterController.Index
api: [GET api/accounting/voucher-masters/get-voucher-masters4post -> VoucherMastersController.GetVoucherMasters4post, GET api/accounting/voucher-masters/get-voucher-masters -> VoucherMastersController.GetVoucherMasters, GET api/accounting/voucher-masters/get-voucher-master -> VoucherMastersController.GetVoucherMaster, POST api/accounting/voucher-masters/save-voucher-master -> VoucherMastersController.SaveVoucherMaster, PUT api/accounting/voucher-masters/update-voucher-master -> VoucherMastersController.UpdateVoucherMaster, DELETE api/accounting/voucher-masters/delete-voucher-master -> VoucherMastersController.DeleteVoucherMaster, POST api/accounting/voucher-masters/save-tem-voucher-detail -> VoucherMastersController.SaveTemVoucheDetail, GET api/accounting/voucher-masters/get-voucher-temp-details -> VoucherMastersController.GetTempVoucheDetail, DELETE api/accounting/voucher-masters/delete-tem-voucher-detail -> VoucherMastersController.DeleteTemVoucheDetail, GET api/accounting/voucher-masters/get-last-narration -> VoucherMastersController.GetLastNarration, GET api/accounting/voucher-masters/get-bank-reconcile-vouchers -> VoucherMastersController.GetBankReconsileVouchers, PUT api/accounting/voucher-masters/update-bank-date -> VoucherMastersController.UpdateBankDate, GET api/accounting/voucher-masters/get-pending-bills -> VoucherMastersController.GetPandingBills, GET api/accounting/voucher-masters/get-payment-modes -> VoucherMastersController.GetPaymentModes, GET api/accounting/voucher-masters/get-lat-narration -> VoucherMastersController.GetLastNarrations, GET api/accounting/voucher-masters/get-last-vch-no -> VoucherMastersController.GetLastVchNo, GET api/accounting/voucher-masters/get-avail-same-bills -> VoucherMastersController.GetAvailSameBill]
service: VoucherMasterService
procedure: PKG_ACCOUNTING.acc_vch_master_select | PKG_ACCOUNTING.acc_voucher_master_paiging | PKG_ACCOUNTING.ACC_VOUCHER_MASTER_SELECT | PKG_ACCOUNTING.acc_voucher_master_insert | PKG_ACCOUNTING.acc_voucher_master_delete | PKG_ACCOUNTING.acc_temp_voucher_detail_insert | PKG_ACCOUNTING.acc_temp_voucher_detail_select | PKG_ACCOUNTING.acc_pending_bills
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL, ACC_TEMP_VOUCHER_DETAIL, ACC_DRAFT_VOUCHER, ACC_TEMP_DRAFT_VOUCHER, ACC_VOUCHER_TYPE, ACC_VOUCHER_MASTER_HIST, ACC_VOUCHER_DETAIL_HIST, ACC_SUB_CLASS, RF_ACTN_STATUS, ACC_VOUCHER_STS]
models: [ACC_VOUCHER_MASTER, ACC_TEMP_VOUCHER_DETAIL, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

**Module:** Accounting. **Tables:** `ACC_VOUCHER_MASTER` (master), `ACC_VOUCHER_DETAIL` (lines), `ACC_TEMP_VOUCHER_DETAIL` (per-user scratch rows for the line-entry grid). **Screen paths:** Accounting > Voucher Entry (state `voucher-masters`), Accounting > Master Voucher List (state `voucher-masters-list`).

Voucher is the finalized, real voucher (a debit/credit journal entry), posted directly to the real ledger tables. It uses the same master+detail double-entry shape as Draft Voucher, and in fact still goes through the same action-type-77 workflow engine (Action Status dropdown, `ACC_VOUCHER_STS` history) — Save/Update here is not workflow-free. A separate **Post** action (distinct from Save/Update) flips `IS_POSTED` from `N` to `Y`, which is the real "can't touch this anymore" terminal state, typically reached after the workflow status hits Management/Audit Approve.

**How this differs from Draft Voucher:**

| Aspect | Voucher (final) | Draft Voucher |
|---|---|---|
| `POST_ID` format | 10-digit number, no prefix (`GET_M_POST_ID_AUTO`) | `D` + 9 digits (`GET_DRFT_VCH_NO_AUTO`) |
| `IS_POSTED` values | `Y` (posted) / `N` (not posted) | `W` (working) / `C` (cancelled) |
| Delete | Archives to `ACC_VOUCHER_MASTER_HIST`/`ACC_VOUCHER_DETAIL_HIST` before hard-deleting | Hard-deletes with no archive |
| "Bill" sub-flow (Select Bill / Available Same Bill / Bill Ledger) | Present, for Bill-type vouchers | Not present |
| Conversion | n/a — this is the destination of Draft Voucher's Submit | Submit copies into this table, then deletes the draft |

There is no reverse "unpost"/"revert to draft" flow — once posted, the only way back is a manual delete (with no `IS_POSTED` guard in the stored procedure) or the archive-on-delete history tables.

**Files (in the old doc set):** `02-fields.md` (header and line-item fields, table columns), `03-relationships.md` (where Voucher data is used elsewhere, and why), `04-known-issues.md` (bugs/inconsistencies found in the current code), `05-unused-columns.md` (DB columns that exist but are never used anywhere in the app).

## Fields

### Header (master) fields — entry screen

Bound to `vm.voucher` (an `ACC_VOUCHER_MASTER` instance). Nearly identical to Draft Voucher's header — differences called out below.

| Frontend Label | Bound To | Input Type | Required? | DB Column | Meaning |
|---|---|---|---|---|---|
| Company | `vm.voucher.HR_COMPANY_ID` | Dropdown | Yes | `HR_COMPANY_ID` | Same as Draft Voucher. |
| Voucher Date | `vm.voucher.POST_DATE` | Date picker | Yes | `POST_DATE` | Same as Draft Voucher. |
| Voucher Number | `vm.voucher.VOUCHER_NO` | Text, disabled when auto-numbered | Conditional (`IS_VCH_NO_AUTO != 'Y'`) | `VOUCHER_NO` | Same conditional pattern as Draft Voucher (not always-auto). |
| Voucher Ref. Number | `vm.voucher.POST_ID` | Text, read-only | System-set | `POST_ID` | 10-digit numeric sequence, no letter prefix — differs from Draft's `D`+9-digit format. |
| Voucher Type | `vm.voucher.VOUCHER_TYPE_ID` | Dropdown | Yes | `VOUCHER_TYPE_ID` | Same as Draft Voucher. |
| Payment Mode | `vm.voucher.PAYMENT_MODE_ID` | Dropdown, shown for bank/cheque/bill types | Yes when visible | `PAYMENT_MODE_ID` | Same as Draft Voucher. |
| "{mode} NO" | `vm.voucher.CHQ_NO` | Text | No | `CHQ_NO` | Same as Draft Voucher, but a globally-unique-cheque-number check runs at save time here (not on Draft's insert). |
| "{mode} DATE" | `vm.voucher.CHQ_DATE` | Date picker | No | `CHQ_DATE` | Same as Draft Voucher. |
| Pay Type | `vm.voucher.PAY_TYPE` | Radio (A/C Pay vs Cash) | No | `PAY_TYPE` | Same as Draft Voucher. |
| Source Ref# | `vm.voucher.VOUCHER_SRC_DESC` | Text, read-only | No | `VOUCHER_SRC_DESC` | Same as Draft Voucher. |
| Last Voucher# | `vm.voucher.LAST_VOUCHER_NO` | Text, read-only, shown only for new records | No | *(not persisted, hint only)* | Not present on Draft's screen — a small addition unique to Voucher. |
| Narration | `vm.voucher.DESCRIPTION` | Textarea | No | `DESCRIPTION` | Same as Draft Voucher. |
| Account Name | `vm.voucher.ACNT_NAME` | Text, shown for cash-visible types | No | `ACNT_NAME` | Same as Draft Voucher. |
| Action Status | `vm.voucher.RF_ACTN_STATUS_ID` | Dropdown, required | Yes | `RF_ACTN_STATUS_ID` | Same workflow field/constants as Draft Voucher — this is not a draft-only field. |

Not directly bound to a visible input, but present on the model/round-tripped: `VOUCHER_MASTER_ID` (PK), `IS_POSTED` (`Y`/`N`, not `N`/`P`), `IS_VCH_NO_AUTO`, `COMP_CODE` (server-set), `EMPLOYEE_ID` (holds the user id), `ACTN_STS_TRACKER`, `REF_ID`/`DIN` (present, unused on this screen), `VCH_SRC` (populated by the insert procedure here, unlike on the draft screen), `LK_TRX_SRC_ID`/`LK_VOUCHER_SRC_TYPE_ID` (mostly hardcoded GL linkage), `ACC_GL_LINK_COA_H_ID` (hardcoded `1`), `GL_SOURCE_LINK` (used by delete and by other modules that create vouchers programmatically), `BANK_DATE` (not on this form — updated separately via the Bank Reconciliation screen's update-bank-date endpoint).

### Line/detail fields — Voucher Details grid

Entry row bound to `vm.ACC_VOUCHER_DETAIL` (an `ACC_TEMP_VOUCHER_DETAIL` instance, persisted into `ACC_TEMP_VOUCHER_DETAIL`). Essentially identical to Draft Voucher's grid, plus a Bill sub-flow that Draft Voucher doesn't have.

| Frontend Label | Bound To | Input Type | Required? | DB Column | Meaning |
|---|---|---|---|---|---|
| Account Head | resolves via `vm.accountHead` | Typeahead autocomplete | Yes | `ACC_SUB_CLASS_ID`, `SUB_NAME`, etc. | Same as Draft Voucher. |
| Voucher For | `VOUCHER_FOR_ID`/`LK_VOUCHER_FOR_TYPE_ID` | Dropdown, conditional | No | same | Same as Draft Voucher. |
| Bill No / Select Bill / Available Same Bill / Bill Ledger | `BILL_NO`, `BILL_REF_ID`, `BILL_DETAIL_ID` | Read-only text + modal buttons, shown only for Bill-eligible voucher types | No | `BILL_NO`, `BILL_REF_ID`, `BILL_DETAIL_ID` | **Not on Draft Voucher's screen.** Tied to `VOUCHER_TYPE_ID=10` ("Bill" type) and account codes `03`/`05`; lets the user pick a pending bill to settle. |
| Narration | `DESCRIPTION` | Text | No | `DESCRIPTION` | Same as Draft Voucher. |
| Cost Center | resolves to `COST_CENTER_ID` | Typeahead autocomplete | Yes | `COST_CENTER_ID` | Same as Draft Voucher, sentinel `1`="N/A". |
| Currency | `CURRENCY_ID` | Dropdown | Implicitly yes (default 1) | `CURRENCY_ID` | Same as Draft Voucher. |
| RATE | `EXCHANGE_RATE` | Text, read-only for local currency | No | `EXCHANGE_RATE` | Same as Draft Voucher. |
| VALUE (BDT) | `vm.BDT_VALUE` | Text | No | *(not persisted)* | Same as Draft Voucher. |
| DR / CR | `DR_AMT` / `CR_AMT` | Text (numeric) | One of DR/CR > 0 | `DR_AMT` / `CR_AMT` | Same as Draft Voucher. |

Grid columns (read-only): Account Head, Voucher For, Cost Center, Bill No, Narration, `HAS_CHILD` (disables Edit/Delete when referenced elsewhere), DR, CR, Action — identical column set to Draft Voucher.

**Unreachable columns:** `CP_DR_AMT`/`CP_CR_AMT` ("compliance" DR/CR) exist on `ACC_TEMP_VOUCHER_DETAIL`/`ACC_VOUCHER_DETAIL` and are copied through by the insert procedure, and the list grid even surfaces a `TOTAL_AMT_CP` aggregate — but the C# repository never sets these parameters when saving a line, so they're always 0 for anything entered through this screen (see Known Issues).

### List screen — search filters and grid columns

Search filters: Voucher No# (`VOUCHER_NO`), Voucher Reference# (`POST_ID`), Voucher Type (`VOUCHER_TYPE_ID`), Company (`HR_COMPANY_ID`), Trx Source (`LK_TRX_SRC_ID`), Posting Status (`IS_POSTED`, options `Y`=Posted / `N`=Un-Posted), From/To Date. Defaults to the last 20 days when no filter is set (cached in session storage from the previous search).

Grid columns: Posting Status badge, Voucher & Ref (`VOUCHER_NO`+`POST_ID`), Date & Company (`POST_DATE`+`COMP_SNAME`), Type & Source (`TYPENAME`+`TRX_SRC_NAME`), Prepared By (`LOGIN_ID`), Amount (`TOTAL_AMT`), Status (workflow badge, color-coded by `RF_ACTN_STATUS_ID`), Action (Print / Approve-workflow / Edit / Delete — Delete disabled client-side when `IS_POSTED=='Y'`).

### Columns actually used

#### `ACC_VOUCHER_MASTER` (master)

Same shape as `ACC_DRAFT_VOUCHER` (see Draft Voucher fields) with these differences: `IS_POSTED` is `Y`/`N`; `VCH_SRC` **is** populated by the insert procedure (unlike the draft table); `BANK_DATE` exists here for Bank Reconciliation.

| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `VOUCHER_MASTER_ID` | ✅ | (auto) | ✅ (key) | PK |
| `POST_ID` | ✅ | (auto) | ✅ | 10-digit numeric reference number |
| `POST_DATE` | ✅ | ✅ | ✅ | |
| `VOUCHER_NO` | ✅ | ✅ | ✅ | auto or manual per `IS_VCH_NO_AUTO` |
| `VOUCHER_TYPE_ID` | ✅ | ✅ | ✅ | FK to `ACC_VOUCHER_TYPE` |
| `DESCRIPTION` | ✅ | ✅ | ✅ | header narration |
| `EMPLOYEE_ID` | — | ✅ | ✅ | holds the user id |
| `REF_ID` / `DIN` | — | ✅ | ✅ | present, mostly unused on this screen |
| `CHQ_NO` / `CHQ_DATE` | — | ✅ | ✅ | conditional on voucher type; `CHQ_NO` uniqueness checked globally, not per company — see Known Issues |
| `COMP_CODE` | ✅ | ✅ | ✅ | company scope, set server-side |
| `IS_POSTED` | ✅ | (not in insert list) | ✅ (via Post action) | `Y`/`N`; only the Post action sets it to `Y` |
| `PAYMENT_MODE_ID` | — | ✅ | ✅ | |
| `VOUCHER_SRC_DESC` | — | ✅ | ✅ | |
| `ACNT_NAME` / `PAY_TYPE` | — | ✅ | ✅ | cash-voucher-only fields |
| `HR_COMPANY_ID` | — | ✅ | ✅ | |
| `RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER` | — | ✅ | ✅ | workflow state, also feeds `ACC_VOUCHER_STS` history |
| `VCH_SRC` | ✅ | ✅ | — | populated by the insert procedure (unlike the draft insert) |
| `ACC_GL_LINK_COA_H_ID` | — | (hardcoded `1`) | — | GL linkage placeholder |
| `LK_TRX_SRC_ID` | ✅ (shown as "Trx Source") | (hardcoded) | — | transaction-source lookup |
| `GL_SOURCE_LINK` | ✅ (used by delete) | — | — | tags vouchers created by other modules (Bills, Payroll, etc.) |
| `BANK_DATE` | ✅ (Bank Reconciliation) | — | ✅ (via separate `update-bank-date` endpoint) | not on the entry form |

#### `ACC_VOUCHER_DETAIL` (lines)

Mirrors `ACC_DRAFT_VOUCHER_DETAIL`: `VOUCHER_DETAIL_ID`, `VOUCHER_MASTER_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `DR_AMT`, `CR_AMT`, `COST_CENTER_ID`, `DESCRIPTION`, `M_CODE`, `XSTATUS`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`, `BILL_REF_ID`, `BILL_DETAIL_ID`, plus `CP_DR_AMT`/`CP_CR_AMT` (present in the schema, unreachable from this UI).

#### `ACC_TEMP_VOUCHER_DETAIL` (per-user staging table for the grid)

Same shape as `ACC_TEMP_DRAFT_VOUCHER`: `TEMP_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `SUB_NAME`, `DR_AMT`, `CR_AMT`, `DESCRIPTION`, `XSTATUS`, `MAP_CODE`, `USER_ID`, `COST_CENTER_ID`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`, `CP_DR_AMT`/`CP_CR_AMT` (accepted by the insert procedure, never set by the repository).

## Relationships

Voucher's per-user scratch lines (`ACC_TEMP_VOUCHER_DETAIL`) are copied by `USER_ID` into the final detail table `ACC_VOUCHER_DETAIL` on Save/Update, the same pattern Draft Voucher uses with its own `ACC_TEMP_DRAFT_VOUCHER` table. `ACC_VOUCHER_MASTER` relates 1:N to `ACC_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. Each detail line picks its account via `ACC_SUB_CLASS_ID` from the Chart of Accounts (`ACC_SUB_CLASS`) and its cost center via `COST_CENTER_ID`. The master row carries `PAYMENT_MODE_ID` (Payment Mode) and `VOUCHER_TYPE_ID` (`ACC_VOUCHER_TYPE`, also driving the voucher-number prefix). Workflow state (`RF_ACTN_STATUS_ID`/`ACTN_STS_TRACKER`) is driven by the same workflow engine as Draft Voucher — `RF_ACTN_STATUS`, `ACC_VOUCHER_STS` history, action type 77, status codes 335-338 — feeding the Action Status dropdown and the list screen's Approve-Workflow action.

Deleting a final voucher first archives the master and detail rows into `ACC_VOUCHER_MASTER_HIST`/`ACC_VOUCHER_DETAIL_HIST` before hard-deleting the live rows (`ACC_VOUCHER_MASTER_DELETE`) — unlike Draft Voucher, whose delete is a pure hard delete with no archive step.

Draft Voucher is the source of the Submit conversion into Voucher (via `ACC_CONFIRM_INSERT`); this Draft→Final path is one-directional — there is no reverse "unpost"/"revert to draft" flow.

Other modules (Bills, Payroll, Export/Import Bill, Fund Request, Cash Bill Realize, Store Receive, Check Bill, Cheque Issue) create/link vouchers by writing the `GL_SOURCE_LINK` tag on `ACC_VOUCHER_MASTER` directly at the PL/SQL layer — confirmed zero C# callers for these procedures in either repository, so this is a completely separate code path from manually-entered vouchers, bypassing `VoucherMasterService`/`VoucherMasterRepository`/`VoucherMastersController`.

The final Voucher screen's "Voucher For" typeahead is actually served by Draft Voucher's own API route (`get-voucher-for-list-by-filter`), called from `voucherMastersController.js:434` and `MasterVoucherListController.js:249` — a cross-screen dependency worth knowing before refactoring/removing Draft Voucher's API.

Every downstream accounting report ultimately reads posted+unposted voucher rows from `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL`, each filtering `IS_POSTED` itself as needed: `acc_voucher_report`, `acc_cheque_report`, `acc_Ledger_report`, `acc_control_Ledger_report`, `acc_trial_balance_report`, `acc_cash_book_report`, `acc_bank_book_report`, `acc_bank_book_currency_report`, `acc_COST_CNTR_LEDGER_report`, `ACC_LEDGER_COST_CNTR_REPORT`, `acc_stock_closing_select`, `acc_duplicate_bills_report`.

### Technical reference (file : line)

| Layer | File |
|---|---|
| UI-Router routes | `ERPSolution/Areas/Accounting/Client/app/config.accountingRoute.js:194-224` |
| MVC shell controller | `ERPSolution/Areas/Accounting/Controllers/VoucherMasterController.cs` (only `Index`, `_VoucherList`, `_MasterVoucherList` actions exist) |
| Entry-form partial view | `ERPSolution/Areas/Accounting/Views/VoucherMaster/_VoucherList.cshtml` |
| List/search partial view | `ERPSolution/Areas/Accounting/Views/VoucherMaster/_MasterVoucherList.cshtml` |
| Entry-form Angular controller | `ERPSolution/Areas/Accounting/Client/app/controllers/voucherMastersController.js` |
| List Angular controller | `ERPSolution/Areas/Accounting/Client/app/controllers/MasterVoucherListController.js` |
| Web API controller | `ERPSolution/Areas/Accounting/Api/VoucherMastersController.cs` |
| BLL | `ERP.BLL/VoucherMasterService.cs`, `ERP.BLL/IVoucherMasterService.cs` |
| Repository | `ERP.Data/VoucherMasterRepository.cs`, `ERP.Data/IVoucherMasterRepository.cs` |
| Shared models | `ERP.Model.Accounting/ACC_VOUCHER_MASTER.cs`, `ACC_TEMP_VOUCHER_DETAIL.cs`, `ACC_VOUCHER_DETAIL.cs` |
| Stored procedures | `PKG_ACCOUNTING.sql` (sibling repo `MultitechERP/src/ERPSolution/oracle/packages/PKG_ACCOUNTING.sql`) |

| Route | Verb | BLL call | Stored procedure |
|---|---|---|---|
| `get-voucher-masters4post` | GET | `GetVoucherMasters4post` | `pkg_accounting.acc_vch_master_select` pOption 1002 — the live List screen's data source |
| `get-voucher-masters` | GET | `GetVoucherMasters` | `PKG_ACCOUNTING.acc_voucher_master_paiging` — legacy/unused |
| `get-voucher-master` | GET | `GetVoucherMaster` (+ `IDraftVoucherService.GetDefaultModel4VchMaster` for new records) | `PKG_ACCOUNTING.ACC_VOUCHER_MASTER_SELECT` |
| `save-voucher-master` | POST | `SaveVoucherMaster(0, model)` | `PKG_ACCOUNTING.acc_voucher_master_insert` pOption 1000 |
| `update-voucher-master` | PUT | `SaveVoucherMaster(id, model)` | same procedure, branches on `pVOUCHER_MASTER_ID` |
| `post-all-voucher-master` | POST | `PostAllVoucherMaster` | same procedure, pOption 1002 (bulk Post) |
| `post-voucher-master` | POST | `PostVoucherMaster` | same procedure, pOption 1001 (single Post) |
| `delete-voucher-master` | DELETE | `DeleteVoucherMaster` | `PKG_ACCOUNTING.acc_voucher_master_delete`, pOption 4000 |
| `save-tem-voucher-detail` | POST | `SaveTemVoucheDetail` | `PKG_ACCOUNTING.acc_temp_voucher_detail_insert` |
| `get-voucher-temp-details` | GET | `GetTempVoucheDetail` | `PKG_ACCOUNTING.acc_temp_voucher_detail_select` pOption 3001 |
| `delete-tem-voucher-detail` | DELETE | `DeleteTemVoucheDetail` | raw SQL, no stored procedure |
| `get-bank-reconcile-vouchers` / `update-bank-date` | GET / PUT | `GetBankReconsileVouchers` / `UpdateBankDate` | feeds the Bank Reconciliation screen |
| `get-pending-bills` / `get-avail-same-bills` | GET | `GetPandingBills` / `GetAvailSameBill` | `PKG_ACCOUNTING.acc_pending_bills` / `pkg_accounting.acc_vch_master_select` pOption 1000 — back the "Select Bill" / "Available Same Bill" modals |

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- 🔴 **Delete has no company/ownership scoping, and no `IS_POSTED` guard**: `ACC_VOUCHER_MASTER_DELETE` (`PKG_ACCOUNTING.sql:4359-4445`) deletes by `VOUCHER_MASTER_ID` alone — no `COMP_CODE` check, no ownership check, and **no check that `IS_POSTED<>'Y'`**. This is worse than Draft Voucher's equivalent gap: it can hard-delete an already-posted, real ledger voucher (archived to `_HIST` tables first, but still removed from the live tables every report reads from). The list-screen UI disables the delete button when a voucher is posted, but that's client-side only — nothing stops a direct API call.
- 🔴 **`acc_temp_voucher_detail_select` deliberately comments out its own company filter**: `PKG_ACCOUNTING.sql:2311` reads `Where --td.COMP_CODE=pCOMP_CODE and \n td.USER_ID=pUSER_ID` — the `pCOMP_CODE` parameter is accepted and passed by the repository, but the WHERE clause for it is literally commented out in the SQL. A user's in-progress line items from one company can bleed into another company's voucher being composed concurrently.
- 🔴 **`ACC_VOUCHER_MASTER_SELECT` has no `COMP_CODE` filter**: `PKG_ACCOUNTING.sql:3590-3605` selects by `POST_ID` only, despite accepting `pCOMP_CODE` — a user who knows/guesses another company's `POST_ID` can load and edit it via `get-voucher-master`. Same gap already documented for Draft Voucher's equivalent procedure.
- 🔴 **`acc_voucher_report` ignores `pCOMP_CODE`**: `PKG_ACCOUNTING.sql:4504-4546` filters only by `pVOUCHER_MASTER_ID` — a user who can enumerate `VOUCHER_MASTER_ID` values in the print URL could print another company's voucher.
- 🟠 **Legacy/dead list endpoint**: `acc_voucher_master_paiging` (`PKG_ACCOUNTING.sql:2320-2355`), wired to `get-voucher-masters`, requires at least one search filter or returns zero rows and is never called by the live List screen (which uses `get-voucher-masters4post` instead) — same "legacy/dead" pattern as Draft Voucher's unused paging option.
- 🟠 **`SaveTemVoucheDetail` never populates `CP_DR_AMT`/`CP_CR_AMT`**: `VoucherMasterRepository.cs:141-173` omits these parameters even though `ACC_TEMP_VOUCHER_DETAIL_INSERT` accepts them and `ACC_VOUCHER_MASTER_INSERT` faithfully copies them through to `ACC_VOUCHER_DETAIL`. Combined with the C# model classes not declaring these properties at all, `TOTAL_AMT_CP` (surfaced on the list grid's paging query) is always 0 for anything entered through this screen — a compliance-ledger feature that exists in the schema/stored procedures but is unreachable from the UI.
- 🟠 **Duplicate cheque-number check is not company-scoped**: `PKG_ACCOUNTING.sql:3903-3912` blocks a duplicate `CHQ_NO` globally across all companies, unlike the voucher-number duplicate check a few lines later which is scoped by `HR_COMPANY_ID`+`VOUCHER_TYPE_ID`. Two legitimately different companies can't reuse the same cheque number even though that's a normal real-world scenario.
- 🟠 **Bulk-Post hardcodes the resulting workflow status regardless of history**: `PKG_ACCOUNTING.sql:4262-4265` sets `RF_ACTN_STATUS_ID=336` (Submit) whenever a tracker existed, even if the voucher had already progressed to 337/338 (Management/Audit Approve) — a bulk-posted voucher's status can silently regress in the data, confusing anyone auditing after the fact.
- 🟠 **Archive-on-delete doesn't record who/when deleted**: `PKG_ACCOUNTING.sql:4413-4417` — the `UPDATE ACC_VOUCHER_MASTER_HIST SET DELETE_BY=..., DELETE_DATE=...` statement is commented out, even though the history-list query expects `DELETE_BY` to be populated via a join. Any "Last Delete By" column in a voucher-history UI will always show null/blank.
- 🟡 **`PostVoucherMaster` BLL method discards its own result**: `ERP.BLL/VoucherMasterService.cs:108-112` calls the repository, ignores the return, and returns a brand-new empty `ACC_VOUCHER_MASTER()` — currently harmless since the Angular caller doesn't use the response body, but a landmine for any future caller expecting the posted voucher's data back.
- 🟡 **`CheckGlTransactionExist` silently drops a format parameter**: `VoucherMasterRepository.cs:500-508` passes `compCode` as a `String.Format` argument the format string never references — the method never actually scopes by company despite its signature suggesting it does.
- 🟡 **Dead/orphaned view files**: `Views/VoucherMaster/_Edit.cshtml` and `Views/VoucherMaster/_VoucherList - Copy.cshtml` (note the literal space in the filename) exist on disk but aren't reachable via any controller action or UI-Router state — same "leftover duplicate view" pattern as Draft Voucher's dead `_Edit.cshtml`.
- 🟡 **Dead migration utility left in the repository**: `VoucherMasterRepository.UpdateBillKey`/`UpdateBillDetailId` (`VoucherMasterRepository.cs:646-685`) runs raw `UPDATE`s to backfill `BILL_DETAIL_ID`/`BILL_KEY` for `VOUCHER_TYPE_ID=10` — looks like a one-time data-fix script; no controller action calls it.
- 🟡 **Inconsistent DB-access pattern within the same repository**: `GetCurrencyList()` and `GetUserOfficeType()` (`VoucherMasterRepository.cs:710-777`) each instantiate their own `new OraDatabase()` instead of using the class's injected `db` field, unlike every other method in the same file.
- 🟡 **Two differently-scoped `GetLastNarration` overloads with the same name**: one keyed by account (`get-last-narration`), one by user (`get-lat-narration` — note the route's own typo, "lat" instead of "last"). Easy to confuse when tracing calls.
- 🟡 **`GetNewPostID` is dead code**: `VoucherMasterRepository.cs:22-28` computes a new `POST_ID` via raw `MAX(POST_ID)+1` SQL, but its only caller in the BLL is commented out — real `POST_ID` generation happens inside the stored procedure (`GET_M_POST_ID_AUTO`) instead.
- 🟡 **`int id` vs `Int64 VOUCHER_MASTER_ID`**: `DeleteVoucherMaster`, `UpdateVoucherMaster`, `UpdateBankDate` all take `int id` while the underlying column/sequence is `NUMBER`/`Int64` — same latent overflow risk documented for Draft Voucher.
- 🟡 **`GET_VCH_NO_AUTO` duplicates `GET_DRFT_VCH_NO_AUTO` almost verbatim**: two separate PL/SQL functions implement the same monthly-sequence-per-company/type/prefix logic for final vs. draft voucher numbers — a maintenance-cost duplication, not a functional bug, but any future fix to the numbering logic needs to be applied in both places.

## Unused Columns

How this was checked: every column of `ACC_VOUCHER_MASTER`, `ACC_VOUCHER_DETAIL`, and `ACC_TEMP_VOUCHER_DETAIL` was grepped (whole word, case-insensitive) across both repos. No `CREATE TABLE` DDL exists in either repo; column lists are reconstructed from the union of every INSERT/UPDATE/SELECT column list found in `PKG_ACCOUNTING.sql` (plus other packages that also write these tables directly) and the C# model/repository code.

### `ACC_VOUCHER_MASTER` (master)

| Column | Verdict | Confidence |
|---|---|---|
| `GL_LINK_REF_NO` | **Unused — a pure write sink.** Written on every voucher insert, and by ~15 *other* modules' own voucher-creation code (Cheque Issue, Export/Import Bill, Payroll, Fund Request, Cash Bill Realize, Store Receive, Check Bill, etc.) with a real document number — but a search for any `SELECT`/`WHERE`/`JOIN` against it anywhere in the Oracle package tree returns zero results. Dozens of modules populate it; nothing ever reads it back. No C# reference at all. | High |
| `ACC_GL_LINK_COA_H_ID` | **Write-only / effectively unused.** Always hardcoded on every insert (`1` from the voucher screen, `12` from Cheque Issue, etc.). Every other hit for this name is the unrelated *config table* `ACC_GL_LINK_COA_H` — never a real `SELECT`/`WHERE`/`JOIN` against `ACC_VOUCHER_MASTER.ACC_GL_LINK_COA_H_ID` itself. | High |
| `LK_VOUCHER_SRC_TYPE_ID` | **Effectively unused.** Accepted by the insert procedure, but the C# repository never supplies a value — always inserted `NULL`. Selectable/filterable in stored procedures, but the repository never supplies that filter param either, and no Angular field binds to it. | Medium-High |
| `LAST_UPDATE_DATE` | **Write-only / effectively unused.** Set to `SYSDATE` on every update; rides through the paging query's `m.*` payload, but no Angular file binds to it and the single-record fetch never explicitly maps it (only `LAST_UPDATED_BY` is consumed, for the "Updated By" grid column). | Medium |
| `CREATION_DATE` | **Write-only / effectively unused.** Same pattern as `LAST_UPDATE_DATE` — set at insert, rides through, never explicitly read or bound anywhere. | Medium |

Confirmed real usage (not flagged): `LK_TRX_SRC_ID` (filter param, "Trx Source" column), `REF_ID`/`DIN` (set by `StockClosingService.cs` for the stock-closing voucher path, and copied from Draft Voucher's `POST_ID` on Submit), `GL_SOURCE_LINK`, `BANK_DATE` (used by Bank Reconciliation), and every other column bound to a form field, grid column, or workflow property.

### `ACC_VOUCHER_DETAIL` (lines)

| Column | Verdict | Confidence |
|---|---|---|
| `CP_DR_AMT` / `CP_CR_AMT` | **Write-only / unreachable from the UI.** Already flagged in Known Issues — the C# model has no properties for them, `SaveTemVoucheDetail` never sets them, so `TOTAL_AMT_CP` on the list grid is always 0 for anything entered through this screen. | High |
| `BILL_KEY` | **Rarely used — read by a live report, but the only writer is dead code.** `acc_duplicate_bills_report` genuinely groups/dedups by it and is called from a real, reachable report path (`ReportRepository.cs`). But the only code that ever writes `BILL_KEY` is `VoucherMasterRepository.UpdateBillKey`/`UpdateBillDetailId` — a one-off migration utility with zero controller callers (also flagged as dead code in Known Issues). Net effect: the report's grouping runs over all-NULL/stale data unless that abandoned utility is manually re-run. | Medium |
| `PARENT_ID` | **Real usage, but PL/SQL-only (no C# path).** Heavily used inside the Oracle package for `HAS_CHILD` computation, last-bill-payment-date maintenance, and several report queries — but no C# model exposes it and no repository method reads/writes it by name; it's only ever set server-side inside the insert procedures. Same category as `GL_SOURCE_LINK`. | Medium-High |

Confirmed real usage: `VOUCHER_DETAIL_ID`, `VOUCHER_MASTER_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `DR_AMT`, `CR_AMT`, `COST_CENTER_ID`, `DESCRIPTION`, `CURRENCY_ID`, `EXCHANGE_RATE`, `BILL_NO`, `BILL_REF_ID`, `BILL_DETAIL_ID`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `XSTATUS` (grid sort order). `M_CODE` is always hardcoded `'000'` on write but *is* read back as `MAP_CODE` and round-tripped through the C# layer and the Angular "Voucher For" UI — real usage, not flagged (a pattern that looked suspicious at first glance, same as on the Draft Voucher table, but here it clears the bar).

### `ACC_TEMP_VOUCHER_DETAIL` (per-user staging table)

Note: `COST_CENTER_NAME`, `VOUCHER_FOR_NAME`, `VOUCHER_FOR_TYPE_NAME` are model properties but **not real persisted columns** — they're computed via joins in the select procedure. Excluded from this audit since they aren't DB columns.

| Column | Verdict | Confidence |
|---|---|---|
| `CP_DR_AMT` / `CP_CR_AMT` | **Write-only / unreachable from the UI.** Same as on `ACC_VOUCHER_DETAIL` — the insert procedure declares both parameters, but the repository never sets them and the C# model has no properties for them at all. | High |

All other columns (`TEMP_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `SUB_NAME`, `DR_AMT`, `CR_AMT`, `DESCRIPTION`, `XSTATUS`, `MAP_CODE`, `USER_ID`, `COST_CENTER_ID`, `EXCHANGE_RATE`, `CURRENCY_ID`, `BILL_REF_ID`, `BILL_NO`, `BILL_DETAIL_ID`, `VOUCHER_MASTER_ID`, `VOUCHER_DETAIL_ID`, `HAS_CHILD`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`) are explicitly read/written and in active use.

### Summary

| Table | Column | Status | Confidence |
|---|---|---|---|
| `ACC_VOUCHER_MASTER` | `GL_LINK_REF_NO` | Unused (pure write sink, no reader anywhere despite ~15 modules populating it) | High |
| `ACC_VOUCHER_MASTER` | `ACC_GL_LINK_COA_H_ID` | Write-only / effectively unused | High |
| `ACC_VOUCHER_MASTER` | `LK_VOUCHER_SRC_TYPE_ID` | Effectively unused | Medium-High |
| `ACC_VOUCHER_MASTER` | `LAST_UPDATE_DATE` | Write-only / effectively unused | Medium |
| `ACC_VOUCHER_MASTER` | `CREATION_DATE` | Write-only / effectively unused | Medium |
| `ACC_VOUCHER_DETAIL` | `CP_DR_AMT` / `CP_CR_AMT` | Write-only / unreachable | High |
| `ACC_VOUCHER_DETAIL` | `BILL_KEY` | Rarely used — report-reachable, writer is dead code | Medium |
| `ACC_VOUCHER_DETAIL` | `PARENT_ID` | Real usage, but PL/SQL-only | Medium-High |
| `ACC_TEMP_VOUCHER_DETAIL` | `CP_DR_AMT` / `CP_CR_AMT` | Write-only / unreachable | High |
