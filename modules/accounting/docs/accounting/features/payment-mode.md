# Feature: Payment Mode

```yaml
---
id: feat:acc-payment-mode
module: accounting
category: master-data
service: PaymentModeService
procedure: ac_payment_mode_select | ac_payment_mode_select_by_Id | ac_payment_mode_delete | acc_payment_mode_insert
mvc: PaymentModeController.Index
api: [GET api/accounting/payment-modes/get-payment-modes -> PaymentModesController.GetPayementModes, POST api/accounting/payment-modes/save-payment-mode -> PaymentModesController.SavePaymentMode, PUT api/accounting/payment-modes/update-payment-mode -> PaymentModesController.UpdateCompany, GET api/accounting/payment-modes/get-payment-mode -> PaymentModesController.GetPaymentMode, DELETE api/accounting/payment-modes/delete-payment-mode -> PaymentModesController.DeletePaymentMode]
tables: [ACC_PAYMENT_MODE, ACC_VOUCHER_MASTER, ACC_MAP_PAY_MODE]
status: verified
---
```

## Overview

Payment Mode is a setup screen (Accounting > Payment Mode) where the accountant defines the ways
a payment can be made — e.g. Cash, Cheque, Bank Transfer — backed by table `ACC_PAYMENT_MODE`.
Once set up here, these show up as a dropdown everywhere else a voucher records how it was paid.

## Fields

What the user sees on the Add/Edit form, and what it maps to underneath.

| Frontend Label | DB Column | Type | Required? | Meaning |
|---|---|---|---|---|
| CODE | `REF_CODE` | Text (auto, read-only) | — | Auto-generated code like `001`, `002`. User can't edit it. |
| Name | `PM_NAME` | Text | Yes | The payment mode's name, e.g. "Cash", "Cheque". |
| Short Name | `SHORT_NAME` | Text | Yes | A short abbreviation for the name. |
| Remarks | `REMARKS` | Text | No | Free-text notes. |
| *(not shown on screen)* | `PAYMENT_MODE_ID` | Number (auto) | — | Auto-generated ID. Used internally to link a voucher to its payment mode. |
| *(not shown on screen)* | `COMP_CODE` | Text (auto) | — | Which company this record belongs to. Set automatically from the logged-in user. |

Two form fields ("Short Name" and "Remarks") share a coding mistake in the underlying HTML —
see Known Issues.

## Relationships

Payment Mode is a lookup table. Nothing points into it except one thing: a Voucher records
which payment mode was used, via `PAYMENT_MODE_ID`.

- `ACC_VOUCHER_MASTER` (Voucher) — foreign key `PAYMENT_MODE_ID`, used on the Voucher entry
  screen to record how the voucher was paid.
- `ACC_VOUCHER_MASTER` (Draft Voucher) — same foreign key, shared model; used on the Draft
  Voucher entry screen before the voucher is finalized.
- `ACC_MAP_PAY_MODE` — mapping table of Voucher Type → allowed Payment Modes; filters the
  dropdown on the Voucher entry screen, since some payment modes only make sense for certain
  voucher types.
- Monthly Stock Closing / Opening — passes along the voucher's payment mode through the
  month-end stock closing process with no new meaning, just carrying it through when posting.
- Voucher Report, Duplicate Bill Payment Report — display the payment mode name on
  printed/exported reports.

Technical reference (file : line): Voucher model FK `ERP.Model\Accounting\ACC_VOUCHER_MASTER.cs:48`;
Voucher repository (read/write) `ERP.Data\VoucherMasterRepository.cs:90,253`;
Voucher-type-filtered lookup (joins `ACC_MAP_PAY_MODE`) `ERP.Data\VoucherMasterRepository.cs:638-644`;
Service wrapper `ERP.BLL\VoucherMasterService.cs:165-170` (`IVoucherMasterService.cs:28`);
API — filtered list `Api\VoucherMastersController.cs:272-278` →
`GET api/accounting/voucher-masters/get-payment-modes?voucherTypeId=`;
Client JS (filtered) `Client\app\services\voucherMasterService.js:126-128`,
`controllers\voucherMastersController.js:43,219,228-230,276,1024,1067`;
Voucher views `Views\VoucherMaster\_Edit.cshtml:60`, `_VoucherList.cshtml:91-92`;
Draft voucher repository `ERP.Data\DraftVoucherRepository.cs:88,298,317`;
Draft voucher API — unfiltered list `Api\DraftVouchersController.cs:128` (uses
`PaymentModeService.GetPaymentModes(comp_code)`, not voucher-type-filtered);
Draft voucher client JS `Client\app\controllers\draftVouchersController.js:35,155,183,316,872-874,964`;
Draft voucher views `Views\DraftVoucher\_Edit.cshtml:54-55`, `_VoucherList.cshtml:103-104`;
Stock closing/opening `ERP.Data\StockClosingRepository.cs:102,138`;
Reports `Areas\Accounting\Reports\AccountingDataSet.Designer.cs`, `VoucherReport.rdlc`,
`DuplicateBillPaymentReport.rdlc`.

Ruled out: no other model has a `PAYMENT_MODE_ID`/`PM_NAME`/`PM_ID` property; the generic
`LOOKUP_DATA` lookup mechanism does not include Payment Mode; `StockClosingsController.cs` and
`CheckerMakerRepository.cs` do not reference payment mode.

## Known Issues

- **Page title typo**: shows "Payement mode" instead of "Payment Mode" (`Index.cshtml`).
- **Short Name field bug**: its HTML `name` attribute is wrongly set to `"PREFIX"` instead of
  `SHORT_NAME` (`_Edit.cshtml`). This breaks the form's per-field validation.
- **Remarks field bug**: its HTML `name` attribute is also `"PREFIX"` — same value as the Short
  Name field, so the two fields collide (`_Edit.cshtml`).
- **Confusing validation messages**: Short Name enforces min=3/max=10 characters, but the
  on-screen messages say the opposite ("Maximum length 3", "Minimum length 10").
- **Misleading method name**: the API's update action is called `UpdateCompany` even though it
  updates a payment mode, not a company (`PaymentModesController.cs`).
- **No server-side validation**: the `ACC_PAYMENT_MODE` model has no `[Required]`/`[StringLength]`
  attributes — all validation happens only in the browser (AngularJS).
- **Delete leaves orphaned data (stored procedure bug)**: `ac_payment_mode_delete` deletes from
  `ACC_MAP_PAY_MODE` using `WHERE MAP_PAY_MODE_ID = pPAYMENT_MODE_ID` — but `MAP_PAY_MODE_ID` is
  that table's own surrogate key, a completely different ID space from `PAYMENT_MODE_ID`. It
  should say `WHERE PAYMENT_MODE_ID = pPAYMENT_MODE_ID`, exactly as the insert/update procedure
  does correctly a few lines earlier. As written, deleting a payment mode almost never cleans up
  its voucher-type mappings, leaving orphaned rows in `ACC_MAP_PAY_MODE` that point to a payment
  mode which no longer exists. (Source: `PKG_ACCOUNTING.sql`,
  `E:\multitech_workspace\MultitechERP\src\ERPSolution\oracle\packages\PKG_ACCOUNTING.sql:1742`.)
- **List/search is not scoped by company**: `ac_payment_mode_select` has no `COMP_CODE` parameter
  and no company filter in its `WHERE` clause, unlike insert/update which both take and store
  `pCOMP_CODE`. In a multi-company app, this means the Payment Mode list/search screen returns
  every company's payment modes, not just the logged-in user's. (Source: same file, line
  1696-1729.)
- **Minor — redundant subqueries**: `ac_payment_mode_select` and `ac_payment_mode_select_by_Id`
  each run two separate correlated subqueries against `ACC_MAP_PAY_MODE`/`acc_voucher_type` per
  row (one for the voucher-type ID list, one for the name list) — these could be combined into a
  single pass. Not a real performance concern at current table sizes, just avoidable duplication.
- **Minor — inconsistent procedure naming**: the insert procedure is `acc_payment_mode_insert`
  (double-`c` prefix), while select/select-by-id/delete all use the single-`c` `ac_payment_mode_*`
  prefix — same package (`PKG_ACCOUNTING`), same feature, two different naming conventions.
  Confirmed via `ERP.Data/PaymentModeRepository.cs:133` (`SavePaymentMode`, called for both create
  and update via `id=0` vs `id>0`).

## Unused Columns

How this was checked: every column of `ACC_PAYMENT_MODE` was grepped (whole word,
case-insensitive) across both repos — this app (`MultiTechERPAccounting`) and the Oracle package
source (`MultitechERP/src/ERPSolution/oracle/packages`) — looking for any real read/write beyond
the column's own declaration. No `CREATE TABLE` DDL exists in either repo, so the column list
itself is reconstructed from the fullest `INSERT` statement plus the C# model class.

**Result: no unused columns.** All 6 columns (`PAYMENT_MODE_ID`, `PM_NAME`, `COMP_CODE`,
`REMARKS`, `REF_CODE`, `SHORT_NAME`) are genuinely read and written somewhere in the app — form
fields, grid columns, or joins from other tables (`ACC_MAP_PAY_MODE`, vouchers).

Confidence: high — this is a small, fully-traced table.
