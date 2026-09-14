# Feature: Draft Voucher

```yaml
---
id: feat:acc-draft-voucher
module: accounting
category: transaction
service: DraftVoucherService
procedure: ACC_DRAFT_VOUCHER_INSERT | ACC_CONFIRM_INSERT | acc_draft_voucher_delete | ACC_DRAFT_VOUCHER_SELECT | pkg_accounting.acc_vch_master_select | acc_draft_voucher_paiging | ACC_DRAFT_VOUCHER_PAIGING | VOUCHER_FOR_SELECT | acc_temp_draft_voucher_insert | acc_temp_draft_voucher_select | acc_voucher_draft_report
mvc: DraftVoucherController.Index
api: [GET api/accounting/draft-vouchers/get-draft-vouchers -> DraftVouchersController.GetVoucherQueues, GET api/accounting/draft-vouchers/get-draft-vouchers-by-filter -> DraftVouchersController.GetDraftVoucherListByFilter, POST api/accounting/draft-vouchers/get-voucher-for-list-by-filter -> DraftVouchersController.GetVoucherForListByFilter, GET api/accounting/draft-vouchers/get-draft-voucher -> DraftVouchersController.GetVoucherQueue, POST api/accounting/draft-vouchers/save-draft-voucher -> DraftVouchersController.SaveVoucherQueue, PUT api/accounting/draft-vouchers/update-draft-voucher -> DraftVouchersController.UpdateVoucherQueue, POST api/accounting/draft-vouchers/submit-draft-voucher -> DraftVouchersController.SubmitDraftVoucher, DELETE api/accounting/draft-vouchers/delete-draft-voucher -> DraftVouchersController.DeleteVoucherMaster, POST api/accounting/draft-vouchers/save-tem-draft-voucher -> DraftVouchersController.SaveTemVoucheDetail, GET api/accounting/draft-vouchers/get-temp-draft-vouchers -> DraftVouchersController.GetTempVoucheDetail, GET api/accounting/draft-vouchers/get-voucher-type -> DraftVouchersController.GetVoucherType, DELETE api/accounting/draft-vouchers/delete-temp-draft-voucher -> DraftVouchersController.DeleteTemVoucheDetail, GET api/accounting/draft-vouchers/get-last-narration -> DraftVouchersController.GetLastNarration]
tables: [ACC_DRAFT_VOUCHER, ACC_DRAFT_VOUCHER_DETAIL, ACC_TEMP_DRAFT_VOUCHER, ACC_TEMP_VOUCHER_DETAIL, ACC_VOUCHER_MASTER, ACC_VOUCHER_DETAIL, ACC_VOUCHER_TYPE, ACC_SUB_CLASS, RF_ACTN_STATUS, ACC_VOUCHER_STS]
models: [ACC_VOUCHER_MASTER, ACC_TEMP_VOUCHER_DETAIL, ACC_VOUCHER_DETAIL]
status: verified
---
```

## Overview

Draft Voucher (Module: Accounting) is found at Accounting > Draft Voucher Entry (UI-Router state `draft-vouchers`) and Accounting > Draft Voucher List (state `draft-voucher-list`).

It is a "working copy" of a voucher (a debit/credit journal entry) that an accountant can save, edit, and re-edit before it becomes a real, numbered voucher. It uses the same master+detail double-entry shape as a finalized Voucher — header fields like voucher no/date/type/payment mode, plus N debit/credit lines that must balance — but it lives in its own, separate set of tables so it never touches the real ledger data until explicitly submitted.

Tables: `ACC_DRAFT_VOUCHER` (master), `ACC_DRAFT_VOUCHER_DETAIL` (lines), `ACC_TEMP_DRAFT_VOUCHER` (per-user scratch rows for the line-entry grid).

**Important:** this is *not* a status flag on the same `ACC_VOUCHER_MASTER` table used by the final Voucher screen. It is two parallel tables (`ACC_DRAFT_VOUCHER`/`ACC_DRAFT_VOUCHER_DETAIL` vs `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL`) with a one-directional "Submit" conversion: clicking **Submit** runs a dedicated stored procedure (`ACC_CONFIRM_INSERT`) that copies the draft row into `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL` and then **deletes** it from the draft tables — there is no "un-submit".

Draft Vouchers also carry an approval-workflow status (`RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER`, workflow action type 77 "Accounting Workflow") that the final Voucher screen doesn't surface, so Draft Voucher effectively doubles as the approval queue before something becomes a posted voucher.

## Fields

### Header (master) fields — entry screen

Bound to `vm.voucher` (an `ACC_VOUCHER_MASTER` model instance, mapped from `ACC_DRAFT_VOUCHER` columns).

| Frontend Label | Bound To | Input Type | Required? | DB Column | Meaning |
|---|---|---|---|---|---|
| Company | `vm.voucher.HR_COMPANY_ID` | Dropdown | Yes | `HR_COMPANY_ID` | Which company/entity this voucher belongs to. |
| Voucher Date | `vm.voucher.POST_DATE` | Date picker | Yes | `POST_DATE` | The transaction date. |
| Voucher Number | `vm.voucher.VOUCHER_NO` | Text, disabled when auto-numbered | Conditional (only when `IS_VCH_NO_AUTO != 'Y'`) | `VOUCHER_NO` | Auto-generated (`GET_DRFT_VCH_NO_AUTO`) or manually typed, depending on a system parameter. |
| Voucher Ref. Number | `vm.voucher.POST_ID` | Text, read-only | Yes (system-set) | `POST_ID` | The draft's own internal reference id, format `D` + 9-digit sequence. Copied into the final voucher's `REF_ID` on Submit. |
| Voucher Type | `vm.voucher.VOUCHER_TYPE_ID` | Dropdown | Yes | `VOUCHER_TYPE_ID` | Cash Payment / Cash Receive / Bank Payment / Bank Receive / Contra / Bill / LC Payment, etc. Drives which other fields show. |
| Payment Mode | `vm.voucher.PAYMENT_MODE_ID` | Dropdown, shown only for bank/cheque voucher types | Yes when visible | `PAYMENT_MODE_ID` | From the Payment Mode master. |
| "{mode} NO" (label follows the payment mode name, e.g. "CHEQUE NO") | `vm.voucher.CHQ_NO` | Text | No | `CHQ_NO` | Cheque/instrument number. |
| "{mode} DATE" | `vm.voucher.CHQ_DATE` | Date picker | No | `CHQ_DATE` | Cheque/instrument date. |
| Pay Type | `vm.voucher.PAY_TYPE` | Radio: A/C Pay (`A`) vs Cash (`C`) | No | `PAY_TYPE` | Only shown for cash-type voucher types. |
| Account Name | `vm.voucher.ACNT_NAME` | Text | No | `ACNT_NAME` | Free-text payee/account name; auto-filled from the first debit line's account when cash mode is shown. |
| Source Ref# | `vm.voucher.VOUCHER_SRC_DESC` | Text | No | `VOUCHER_SRC_DESC` | Auto-populated on new drafts from the user's office type; used in auto voucher-number generation. |
| Action Status | `vm.voucher.RF_ACTN_STATUS_ID` | Dropdown (workflow statuses, action type 77) | Yes | `RF_ACTN_STATUS_ID` | Workflow step (Create Draft / Submit Draft Voucher / Management Approves / Audit Approve). Picking "Submit Draft Voucher" triggers the Submit flow instead of a plain Save. |
| Narration | `vm.voucher.DESCRIPTION` | Textarea | No | `DESCRIPTION` | Free-text header note, separate from per-line narration. Has a "refresh" button that pulls the last narration used for the selected account head. |

Not directly bound to a visible input, but present on the model / round-tripped: `VOUCHER_MASTER_ID` (PK), `IS_POSTED` (`W`=Working/draft, `C`=Cancelled — set by which button is clicked), `IS_VCH_NO_AUTO` (system param), `COMP_CODE` (set server-side, not user-editable), `EMPLOYEE_ID` (holds the user id, doubles as created-by/updated-by), `ACTN_STS_TRACKER` (workflow correlation id), `REF_ID`/`DIN` (present on the model, largely unused on this screen).

### Line/detail fields — Voucher Details grid

The entry row above the grid is bound to `vm.ACC_VOUCHER_DETAIL` (an `ACC_TEMP_VOUCHER_DETAIL` model instance, persisted into `ACC_TEMP_DRAFT_VOUCHER` for drafts).

| Frontend Label | Bound To | Input Type | Required? | DB Column | Meaning |
|---|---|---|---|---|---|
| Account Head | resolves to `AC_CODE`/`MAIN_CODE`/`SUB_CODE`/`ACC_SUB_CLASS_ID`/`SUB_NAME` | Typeahead autocomplete | Yes | `ACC_SUB_CLASS_ID`, `SUB_NAME`, etc. | The GL account this line posts to, from Chart of Accounts. |
| "Voucher For" (label follows type, e.g. Buyer/Supplier/Employee/Bank) | `VOUCHER_FOR_ID` / `LK_VOUCHER_FOR_TYPE_ID` | Dropdown, shown only when the account head has a non-general voucher-for type | No | `VOUCHER_FOR_ID`, `LK_VOUCHER_FOR_TYPE_ID` | Attaches a secondary reference (a specific buyer, supplier, employee, or bank) to the line. |
| Narration | `DESCRIPTION` | Text | No | `DESCRIPTION` | Per-line note. |
| Cost Center | resolves to `COST_CENTER_ID` | Typeahead autocomplete | Yes | `COST_CENTER_ID` | From Cost Center; defaults to sentinel `1` ("N/A") on new lines. |
| Currency | `CURRENCY_ID` | Dropdown | Implicitly yes (defaults to 1) | `CURRENCY_ID` | Line currency; a non-local currency triggers a rate lookup and appends a rate note to the narration. |
| RATE | `EXCHANGE_RATE` | Text, read-only for local currency | No | `EXCHANGE_RATE` | Exchange rate vs. local currency, auto-fetched. |
| VALUE (BDT) | `vm.BDT_VALUE` | Text | No | *(not persisted — convenience field only)* | Type the local-currency value and DR/CR is back-computed by dividing by the rate. |
| DR | `DR_AMT` | Text (numeric) | One of DR/CR must be > 0 | `DR_AMT` | Debit amount. |
| CR | `CR_AMT` | Text (numeric) | One of DR/CR must be > 0 | `CR_AMT` | Credit amount. |

Grid columns (read-only): Account Head (`SUB_NAME`), Voucher For (`VOUCHER_FOR_NAME`), Cost Center (`COST_CENTER_NAME`), Bill No (`BILL_NO`), Narration (`DESCRIPTION`), `HAS_CHILD` (Y/N — disables Edit/Delete when the line is referenced elsewhere), DR, CR, and an Action column.

### List screen — search filters and grid columns

Search form: Voucher No# (`VOUCHER_NO`), Voucher Reference# (`POST_ID`), Voucher Type (`VOUCHER_TYPE_ID`), Company (`HR_COMPANY_ID`), Trx Source (`LK_TRX_SRC_ID`), Posting Status (`IS_POSTED`, options limited to `W`=Draft / `C`=Cancelled), From/To Date.

Grid columns: `VOUCHER_NO` + `POST_ID`, `POST_DATE` + `COMP_SNAME`, `TYPENAME` + `TRX_SRC_NAME`, `LOGIN_ID` (prepared-by), `IS_POSTED` (rendered as a "Draft"/"Cancelled" badge), `TOTAL_AMT` (summed from `ACC_DRAFT_VOUCHER_DETAIL`), `EVENT_NAME`/`ACTN_ROLE_FLAG` (workflow status text), and an Action column (Edit / Approve-workflow / Print / Delete).

### Columns actually used

#### `ACC_DRAFT_VOUCHER` (master)

| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `VOUCHER_MASTER_ID` | Yes | (auto) | Yes (key) | PK, from `acc_draft_voucher_seq` |
| `POST_ID` | Yes | (auto) | Yes | draft reference number, `D` + 9 digits |
| `POST_DATE` | Yes | Yes | Yes | |
| `VOUCHER_NO` | Yes | Yes | Yes | auto or manual per `IS_VCH_NO_AUTO` |
| `VOUCHER_TYPE_ID` | Yes | Yes | Yes | FK to `ACC_VOUCHER_TYPE` |
| `DESCRIPTION` | Yes | Yes | Yes | header narration |
| `EMPLOYEE_ID` | — | Yes | Yes | holds the user id; doubles as created-by/updated-by |
| `REF_ID` / `DIN` | — | Yes | Yes | present on the model, mostly unused on this screen |
| `CHQ_NO` / `CHQ_DATE` | — | Yes | Yes | conditional on voucher type |
| `COMP_CODE` | Yes | Yes | Yes | company scope, set server-side |
| `IS_POSTED` | Yes | Yes | Yes | `W` (draft) / `C` (cancelled); set to `W` automatically if `ACC_CONFIRM_INSERT` fails |
| `PAYMENT_MODE_ID` | — | Yes | Yes | |
| `VOUCHER_SRC_DESC` | — | Yes | Yes | used in auto voucher-number generation |
| `ACNT_NAME` / `PAY_TYPE` | — | Yes | Yes | cash-voucher-only fields |
| `HR_COMPANY_ID` | — | Yes | Yes | |
| `RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER` | — | Yes | Yes | workflow state |
| `VCH_SRC` | Yes (read) | — | — | present on model, not set by the insert procedure — see Known Issues |
| `ACC_GL_LINK_COA_H_ID` | — | (hardcoded `1`) | — | GL linkage placeholder |
| `LK_TRX_SRC_ID` | Yes (shown as "Trx Source") | (hardcoded, accounting module constant) | — | transaction-source lookup |
| `GL_SOURCE_LINK` | Yes (used by delete & confirm) | — | — | links back to whatever external module generated this voucher |

#### `ACC_DRAFT_VOUCHER_DETAIL` (lines)

Mirrors `ACC_VOUCHER_DETAIL`: `VOUCHER_DETAIL_ID`, `VOUCHER_MASTER_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `DR_AMT`, `CR_AMT`, `COST_CENTER_ID`, `DESCRIPTION`, `M_CODE` (hardcoded `'000'` on insert), `XSTATUS`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`.

#### `ACC_TEMP_DRAFT_VOUCHER` (per-user staging table for the grid)

`TEMP_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `SUB_NAME`, `DR_AMT`, `CR_AMT`, `DESCRIPTION`, `XSTATUS`, `MAP_CODE`, `USER_ID`, `COST_CENTER_ID`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`.

## Relationships

`ACC_TEMP_DRAFT_VOUCHER` holds per-user scratch lines that get copied (by `USER_ID`) into `ACC_DRAFT_VOUCHER_DETAIL` on Save/Update. `ACC_DRAFT_VOUCHER` is the draft master, related 1:N to `ACC_DRAFT_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. Each detail line picks `ACC_SUB_CLASS_ID` from the Chart of Accounts and `COST_CENTER_ID` from Cost Center. The header picks `PAYMENT_MODE_ID` from Payment Mode and `VOUCHER_TYPE_ID` from `ACC_VOUCHER_TYPE`. The workflow engine (`RF_ACTN_STATUS`/`ACC_VOUCHER_STS`, action type 77) drives `ACTN_STS_TRACKER`/`RF_ACTN_STATUS_ID` on the draft master. On Submit, the draft master and lines are copied to `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL` and then deleted from the draft tables. The draft master also feeds the Voucher Draft Report / Day Book / Voucher print.

Detail relationships:

- `ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` — destination of the Submit conversion, used via the `submit-draft-voucher` route calling `ACC_CONFIRM_INSERT`. Turns a draft into a real, numbered voucher; the new voucher's `REF_ID` is set to the draft's `POST_ID` for traceability, and the draft rows are deleted afterward.
- `ACC_TEMP_DRAFT_VOUCHER` — per-user staging area, used on every line add/edit while composing a draft. Lets the user build up lines interactively before they're committed to `ACC_DRAFT_VOUCHER_DETAIL` on Save.
- Chart of Accounts (`ACC_SUB_CLASS`) — FK via `ACC_SUB_CLASS_ID`/`AC_CODE`/`MAIN_CODE`/`SUB_CODE` on every line, used by the Account Head autocomplete to select which GL account a line posts to.
- Cost Center — FK via `COST_CENTER_ID` on every line, used by the Cost Center autocomplete (defaults to sentinel "N/A", ID 1); same pattern as the final Voucher screen.
- Payment Mode — FK via `PAYMENT_MODE_ID` on the header, used by the Payment Mode dropdown shown for bank/cheque voucher types; same relationship as on the final Voucher screen.
- `ACC_VOUCHER_TYPE` — FK via `VOUCHER_TYPE_ID`, drives the Voucher Type dropdown and visibility of Payment Mode/Cheque/Pay Type fields; also supplies the voucher-number prefix used by auto-numbering.
- Workflow engine (`RF_ACTN_STATUS` / `ACC_VOUCHER_STS`, action type 77) — via `RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER`, drives the Action Status dropdown on the entry screen and the "Approve workflow" button on the list screen. Draft Voucher is also the workflow queue: choosing "Submit Draft Voucher" as the next status actually calls the Submit API instead of a plain Save.
- Voucher For (Buyer/Supplier/Employee/Bank lookups) — via `LK_VOUCHER_FOR_TYPE_ID`/`VOUCHER_FOR_ID` per line, a conditional dropdown on account-head selection that tags a line with a specific secondary party, resolved dynamically per account head's configured type.
- Reports — the `acc_voucher_draft_report` stored procedure powers Draft Voucher's own Print button and the Day Book export; this is a distinct report procedure from the finalized voucher's `acc_voucher_report`.
- `ACC_VOUCHER_MASTER` (again) — via a `GetDefaultModel4VchMaster` cross-call, the final Voucher screen also calls into `DraftVoucherService` for the "is voucher number auto?" system-setting lookup. Both screens share this lookup — worth knowing if `DraftVoucherService` is ever refactored/renamed.

### Technical reference (file : line)

| Layer | File |
|---|---|
| UI-Router routes | `ERPSolution/Areas/Accounting/Client/app/config.accountingRoute.js:226-256` |
| MVC shell controller | `ERPSolution/Areas/Accounting/Controllers/DraftVoucherController.cs` |
| Entry-form partial view | `ERPSolution/Areas/Accounting/Views/DraftVoucher/_VoucherList.cshtml` |
| List/search partial view | `ERPSolution/Areas/Accounting/Views/DraftVoucher/_DraftVoucherList.cshtml` |
| Entry-form Angular controller | `ERPSolution/Areas/Accounting/Client/app/controllers/draftVouchersController.js` |
| List Angular controller | `ERPSolution/Areas/Accounting/Client/app/controllers/DraftVoucherListController.js` |
| Web API controller | `ERPSolution/Areas/Accounting/Api/DraftVouchersController.cs` |
| BLL | `ERP.BLL/DraftVoucherService.cs`, `ERP.BLL/IDraftVoucherService.cs` |
| Repository | `ERP.Data/DraftVoucherRepository.cs`, `ERP.Data/IDraftVoucherRepository.cs` |
| Shared models | `ERP.Model.Accounting/ACC_VOUCHER_MASTER.cs`, `ACC_TEMP_VOUCHER_DETAIL.cs`, `ACC_VOUCHER_DETAIL.cs` |
| Stored procedures | `PKG_ACCOUNTING.sql` (sibling repo `MultitechERP/src/ERPSolution/oracle/packages/PKG_ACCOUNTING.sql`) |

| Route | Verb | BLL call | Stored procedure |
|---|---|---|---|
| `get-draft-vouchers` | GET | `GetVoucherMasters` | `acc_draft_voucher_paiging` (pOption 3000) — legacy/dead, see Known Issues |
| `get-draft-vouchers-by-filter` | GET | `GetDraftVoucherByFilter` | `ACC_DRAFT_VOUCHER_PAIGING` (pOption 3001) — the one the live List screen uses |
| `get-voucher-for-list-by-filter` | POST | `GetVoucherForListByFilter` | `VOUCHER_FOR_SELECT` |
| `get-draft-voucher` | GET | `GetVoucherMaster` / `GetDefaultModel4VchMaster` | `ACC_DRAFT_VOUCHER_SELECT` / `pkg_accounting.acc_vch_master_select` (pOption 1001) |
| `save-draft-voucher` | POST | `SaveVoucherMaster(0, model)` | `ACC_DRAFT_VOUCHER_INSERT` (`PKG_ACCOUNTING.sql:3246`) |
| `update-draft-voucher` | PUT | `SaveVoucherMaster(id, model)` | same procedure, branches on `pVOUCHER_MASTER_ID` |
| `submit-draft-voucher` | POST | `SubmitDraftVoucher` | `ACC_CONFIRM_INSERT` (`PKG_ACCOUNTING.sql:2756-2946`) — the draft→final conversion |
| `delete-draft-voucher` | DELETE | `DeleteVoucherMaster` | `acc_draft_voucher_delete` (`PKG_ACCOUNTING.sql:3461`) |
| `save-tem-draft-voucher` | POST | `SaveTemVoucheDetail` | `acc_temp_draft_voucher_insert` |
| `get-temp-draft-vouchers` | GET | `GetTempVoucheDetail` | `acc_temp_draft_voucher_select` (`PKG_ACCOUNTING.sql:3543`) |
| `delete-temp-draft-voucher` | DELETE | `DeleteTemVoucheDetail` | raw SQL, no stored procedure |
| `get-last-narration` | GET | `GetLastNarration` | raw SQL against `ACC_DRAFT_VOUCHER_DETAIL`/`ACC_DRAFT_VOUCHER` |

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Debug leftover in production exception handler**: `ACC_CONFIRM_INSERT`'s `EXCEPTION WHEN OTHERS` block ends with `insert into test_tab values(pMsg);` (`PKG_ACCOUNTING.sql:2945`). If `test_tab` doesn't exist (or its shape doesn't match) in a given environment, this raises a *new*, unhandled exception inside the exception handler, masking the real error that triggered the Submit failure.
- **Delete has no company/ownership scoping**: `acc_draft_voucher_delete` (`PKG_ACCOUNTING.sql:3461-3491`) deletes by `VOUCHER_MASTER_ID` alone — no `COMP_CODE` check, and no check that the caller owns/created the draft. Any authenticated user who can guess/enumerate a `VOUCHER_MASTER_ID` can delete another company's or another user's draft voucher and its lines. The C# controller does pass a `userId`, but the SP only uses it to clean the *unrelated* `ACC_TEMP_DRAFT_VOUCHER` staging rows (line 3484), not to restrict which draft can be deleted.
- **Duplicate stored-procedure parameter in Save/Update**: `DraftVoucherRepository.SaveVoucherMaster` (`ERP.Data/DraftVoucherRepository.cs:296-320`) passes `pPAYMENT_MODE_ID` twice in the `CommandParameter` list (line 298 and line 317) — the equivalent method for the final Voucher (`VoucherMasterRepository.SaveVoucherMaster`) passes it only once. Depending on how `OraDatabase.ExecuteStoredProcedure` binds duplicate named parameters, this is either harmless (last-wins) or a latent binding bug.
- **`ACC_DRAFT_VOUCHER_SELECT` has no company filter**: (`PKG_ACCOUNTING.sql:2578-2607`) selects by `POST_ID` only, with no `COMP_CODE` check — a user who knows/guesses another company's draft `POST_ID` can load and edit it via `get-draft-voucher`. (The equivalent `acc_voucher_master_select` for final vouchers accepts a `pCOMP_CODE` param but doesn't use it in its `WHERE` clause either — same gap on both screens.)
- **`acc_temp_draft_voucher_select` accepts but ignores `pCOMP_CODE`**: the procedure signature takes `pCOMP_CODE` (`PKG_ACCOUNTING.sql:3543`) and the repository passes the current company code, but the query (`PKG_ACCOUNTING.sql:3578`) filters only by `USER_ID`, never by company. If the same login is used across multiple companies without clearing staging rows between sessions, in-progress line items from one company could bleed into another company's draft being composed concurrently.
- **Legacy/dead list endpoint**: `ACC_DRAFT_VOUCHER_PAIGING` pOption 3000 (`PKG_ACCOUNTING.sql:2369-2396`, wired to `get-draft-vouchers`) requires at least one search filter or it silently returns zero rows. The live List screen doesn't call this endpoint at all — it uses pOption 3001 instead — so this path looks like dead code left over from an earlier grid implementation (matching commented-out code in `draftVouchersController.js:524-592`).
- **Duplicate/dead entry-form view**: `Views/DraftVoucher/_Edit.cshtml` is a second, simpler header-only form (no line grid, no Save/Submit wiring beyond a delete-confirmation modal) that doesn't appear to be referenced by any UI-Router state — `_VoucherList.cshtml` is the one actually routed to for both add and edit. Worth confirming it's genuinely unused before deleting.
- **`VCH_SRC` not set by the draft insert procedure**: `ACC_DRAFT_VOUCHER_INSERT`'s insert column list (`PKG_ACCOUNTING.sql:3296-3315`) doesn't include `VCH_SRC`, even though the C#/JS layer reads `vm.voucher.VCH_SRC` (defaulting it to `'OWN'` client-side) and the dead `_Edit.cshtml` form has commented-out bindings against it — suggesting a `VCH_SRC`-based edit-lock feature was intended but never wired up server-side for drafts (the final Voucher's insert procedure does populate it, at `PKG_ACCOUNTING.sql:2833`).
- **Mixed types for the same "user" concept**: `ACC_TEMP_DRAFT_VOUCHER.USER_ID` is written via a `VARCHAR2` parameter (`PKG_ACCOUNTING.sql:3498`) but read via `NUMBER` parameters elsewhere (`PKG_ACCOUNTING.sql:2579,2589,3543`). Oracle implicit conversion papers over this today, but it's a latent type-mismatch trap.
- **Null `pUSER_ID` collapses to a shared bucket**: `ACC_DRAFT_VOUCHER_SELECT`'s reload step does `DELETE FROM ACC_TEMP_DRAFT_VOUCHER WHERE USER_ID = NVL(pUSER_ID, 0)` (`PKG_ACCOUNTING.sql:2588-2589`) — if `pUSER_ID` is ever null, this clears/targets a shared `USER_ID = 0` bucket instead of failing loudly, which could cross-contaminate or wipe another null-userId session's in-progress lines.
- **Cancel button mislabeled**: the "Cancel" action on the entry screen renders as `<i class="fa fa-times"></i> Cancle` — a typo (`_VoucherList.cshtml:279`).
- **`IS_POSTED` 2-state enum hides a failure case**: only `W`/`C` are exposed in the UI, but `ACC_CONFIRM_INSERT` also sets `IS_POSTED` back to `W` on a failed Submit (`PKG_ACCOUNTING.sql:2934-2936`) — there's no UI affordance to distinguish "a submit attempt failed and reverted to Working" from "never submitted"; both show the same "Draft" badge.
- **No stored procedure for temp-detail delete**: `DeleteTemVoucheDetail` (`ERP.Data/DraftVoucherRepository.cs:444-457`) builds `delete from ACC_TEMP_DRAFT_VOUCHER where TEMP_ID='{0}'` via raw string formatting rather than a parameterized query, with no `COMP_CODE`/`USER_ID` scoping — same SQL-injection-shaped pattern flagged in the Cost Center Group and Cost Center docs.
- **`int id` vs `Int64 VOUCHER_MASTER_ID`**: the Web API's delete/update actions take `int id` (`DraftVouchersController.cs:152,177`) while the underlying column/sequence is `NUMBER`/`Int64` — same pattern as the final Voucher API, so not unique to Draft Voucher, but would silently break once IDs exceed `Int32.MaxValue`.

## Unused Columns

How this was checked: every column of `ACC_DRAFT_VOUCHER`, `ACC_DRAFT_VOUCHER_DETAIL`, and `ACC_TEMP_DRAFT_VOUCHER` was grepped (whole word, case-insensitive) across both repos, cross-checked against `PKG_ACC_REPORT.sql` and `PKG_CM_EXPORT_BILL.sql` (which also touch these tables). No `CREATE TABLE` DDL exists in either repo; column lists are reconstructed from the union of every INSERT/SELECT/UPDATE column list found.

### `ACC_DRAFT_VOUCHER` (master)

| Column | Verdict | Confidence |
|---|---|---|
| `VCH_SRC` | **Write-only / effectively unused.** Never set by `ACC_DRAFT_VOUCHER_INSERT` or `ACC_DRAFT_VCH_SAVE4MISC_SRC`. The only place a draft row is ever assigned a value is dead/commented-out code in `PKG_CM_EXPORT_BILL.sql:4671-4932`. Read back and defaulted client-side (`'OWN'`) but that default is never actually persisted. Already flagged as a known issue. | High |
| `DIN` | **Unused / write-only.** Threaded through every layer of the insert/update/select round trip, but no `.cshtml` or `.js` file under the Draft Voucher screen ever references it — always an empty string. | High |
| `REF_ID` | **Write-only from this screen.** Inserted and selected back, but `draftVouchersController.js` never sets or displays it — always empty on this screen. (Not dead app-wide: other flows like `StockClosingRepository.cs` populate `REF_ID` for a different voucher-entry path.) | Medium |
| `CREATION_DATE` | **Write-only.** Set to `SYSDATE` on insert, but never mapped in `DraftVoucherRepository.GetVoucherMaster` and never shown in the list grid. | High |
| `LAST_UPDATED_BY` | **Write-only.** Set on every update, but the draft-specific paging query only joins `CREATED_BY` (for "Prepared By") — never `LAST_UPDATED_BY`. (Contrast: the final Voucher's own paging query *does* join it.) | High |
| `LAST_UPDATE_DATE` | **Write-only.** Same pattern as `LAST_UPDATED_BY`. | High |
| `GL_LINK_REF_NO`, `GL_SOURCE_LINK`, `ACC_GL_LINK_COA_H_ID` | **Rarely used from this screen.** Zero references anywhere under the Draft Voucher UI; `ACC_DRAFT_VOUCHER_INSERT` hardcodes `ACC_GL_LINK_COA_H_ID=1` and never sets the other two. They're only populated via the unrelated `ACC_DRAFT_VCH_SAVE4MISC_SRC` procedure (export-bill/bank-realization flows) and read by `ACC_CONFIRM_INSERT`/delete for bill-linking — real, but not from this screen. | Medium |
| `HR_OFFICE_ID` | **Unused; possibly not even a real column.** Only appears inside a fully commented-out dead-code block in `PKG_CM_EXPORT_BILL.sql:4671-4932`. Not part of any live insert/select. Flagged for manual DB-side confirmation. | Low |

All other columns (`VOUCHER_MASTER_ID`, `POST_ID`, `POST_DATE`, `VOUCHER_NO`, `VOUCHER_TYPE_ID`, `DESCRIPTION`, `EMPLOYEE_ID`, `CHQ_NO`, `CHQ_DATE`, `COMP_CODE`, `IS_POSTED`, `PAYMENT_MODE_ID`, `CREATED_BY`, `ACNT_NAME`, `PAY_TYPE`, `HR_COMPANY_ID`, `IS_VCH_NO_AUTO`, `LK_TRX_SRC_ID`, `VOUCHER_SRC_DESC`, `RF_ACTN_STATUS_ID`, `ACTN_STS_TRACKER`) are in active, verified use.

### `ACC_DRAFT_VOUCHER_DETAIL` (lines)

| Column | Verdict | Confidence |
|---|---|---|
| `M_CODE` | **Write-only / effectively unused.** Every insert path hardcodes the literal `'000'` — never derived from real data. The one place a value is read back (repopulating `ACC_TEMP_DRAFT_VOUCHER.MAP_CODE`) is itself dead — see below. No view ever reads `M_CODE` directly. | High |
| `IS_B_OR_C_AC` | **Unused.** Only ever written by `ACC_DRAFT_VCH_SAVE4MISC_SRC` (comment: `B=Bill, C=Bill Collection`) — no `SELECT`, `WHERE`, or C#/JS reference reads it back anywhere. | High |

All other columns (`VOUCHER_DETAIL_ID`, `VOUCHER_MASTER_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `DR_AMT`, `CR_AMT`, `COST_CENTER_ID`, `DESCRIPTION`, `XSTATUS`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`) are in active use.

### `ACC_TEMP_DRAFT_VOUCHER` (per-user staging table)

| Column | Verdict | Confidence |
|---|---|---|
| `MAP_CODE` | **Unused / write-only.** Only ever populated when re-opening a submitted draft, from `M_CODE` (which is always the constant `'000'` — see above). Selected back out and mapped into the C# model, but never appears in the grid column set or is otherwise displayed/acted on. Not part of the "new line" insert at all — only settable via the reopen-draft path. | High |

All other columns (`TEMP_ID`, `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `SUB_CODE`, `SUB_NAME`, `DR_AMT`, `CR_AMT`, `DESCRIPTION`, `XSTATUS`, `USER_ID`, `COST_CENTER_ID`, `CURRENCY_ID`, `EXCHANGE_RATE`, `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID`, `BILL_NO`) are in active use. (`COMP_CODE` looked like a dead pass-through at first glance — the select procedure's `pCOMP_CODE` filter is commented out — but the column itself is genuinely load-bearing: it's selected directly into `ACC_DRAFT_VOUCHER_DETAIL.COMP_CODE` at insert time.)

**Related but not a column verdict:** `draftVouchersController.js:406-407` sets client-side model fields `BILL_REF_ID`/`BILL_DETAIL_ID` that are never sent to the server — `SaveTemVoucheDetail` doesn't pass them, and the insert procedure's column list never references them. This suggests `BILL_REF_ID`/`BILL_DETAIL_ID` may not even be real columns of `ACC_TEMP_DRAFT_VOUCHER` (unlike `ACC_VOUCHER_DETAIL`, which does have them) — worth a DDL check to confirm.

### Summary

| Table | Column | Status | Confidence |
|---|---|---|---|
| `ACC_DRAFT_VOUCHER` | `VCH_SRC` | Write-only / effectively unused | High |
| `ACC_DRAFT_VOUCHER` | `DIN` | Unused / write-only | High |
| `ACC_DRAFT_VOUCHER` | `REF_ID` | Write-only from this screen | Medium |
| `ACC_DRAFT_VOUCHER` | `CREATION_DATE` | Write-only | High |
| `ACC_DRAFT_VOUCHER` | `LAST_UPDATED_BY` | Write-only | High |
| `ACC_DRAFT_VOUCHER` | `LAST_UPDATE_DATE` | Write-only | High |
| `ACC_DRAFT_VOUCHER` | `GL_LINK_REF_NO` / `GL_SOURCE_LINK` / `ACC_GL_LINK_COA_H_ID` | Rarely used from this screen (used elsewhere) | Medium |
| `ACC_DRAFT_VOUCHER` | `HR_OFFICE_ID` | Unused; possibly not a real column | Low |
| `ACC_DRAFT_VOUCHER_DETAIL` | `M_CODE` | Write-only / effectively unused | High |
| `ACC_DRAFT_VOUCHER_DETAIL` | `IS_B_OR_C_AC` | Unused | High |
| `ACC_TEMP_DRAFT_VOUCHER` | `MAP_CODE` | Unused / write-only | High |
