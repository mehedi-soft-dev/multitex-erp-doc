# Feature: Cost Center

```yaml
---
id: feat:acc-cost-center
module: accounting
category: master-data
service: CostCenterService
procedure: ACC_COST_CENTER_SELECT | GET_COST_CENTER_INFO | acc_cost_center_insert
mvc: CostCenterController.Index
api: [GET api/accounting/cost-centers/get-cost-centers-by-filter -> CostCentersController.GetListByFilter, GET api/accounting/cost-centers/get-cost-centers -> CostCentersController.GetCostCenters, POST api/accounting/cost-centers/save-cost-center -> CostCentersController.SaveCostCenter, PUT api/accounting/cost-centers/update-cost-center -> CostCentersController.UpdateCostCenter, GET api/accounting/cost-centers/get-cost-center -> CostCentersController.GetCostCenter, DELETE api/accounting/cost-centers/delete-cost-center -> CostCentersController.DeleteCostCenter, GET api/accounting/cost-centers/get-cost-center-select-models -> CostCentersController.CostCenterSelectModels]
pOption: "ACC_COST_CENTER_SELECT: 3000 list, 3001 DDL, 3002 DDL w/ office+department"
tables: [ACC_COST_CENTER, ACC_COST_CENTER_GROUP]
status: verified
---
```

## Overview

Cost Center (Accounting > Cost Center) is the actual selectable cost center — e.g. a department,
branch, or project — that gets tagged onto a voucher line so transactions can be reported "by
cost center", backed by table `ACC_COST_CENTER`. Every Cost Center belongs to one Cost Center
Group, which is only used for grouping/subtotaling in reports.

## Fields

### Add/Edit form

| Frontend Label (raw) | Bound To | Input Type | Required? | Meaning |
|---|---|---|---|---|
| "Code" | `vm.costCenter.COST_CENTER_CODE` | Text (read-only) | — | Auto-generated code. |
| "Name" | `vm.costCenter.COST_CENTER_NAME` | Text | Yes | The cost center's name. Error: "Cost Center is required". |
| "* Group" | `vm.costCenter.GROUP_ID` | Dropdown (options from Cost Center Group) | Yes | Which Cost Center Group this belongs to. Placeholder: "-- Select Cost Center Group --". |
| "Remarks" | `vm.costCenter.REMARKS` | Textarea | No | Free-text notes. |

List/search screen: dropdown "Cost Center Group" (`vm.form.GROUP_ID`) + text "Cost Center"
(`vm.form.COST_CENTER_NAME`).

### Columns actually used (`ACC_COST_CENTER`)

| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `COST_CENTER_ID` | ✅ | (auto) | ✅ (key) | |
| `COST_CENTER_CODE` | ✅ | (auto-generated) | — | shown read-only |
| `COST_CENTER_NAME` | ✅ | ✅ | ✅ | the only field the user retypes on edit |
| `GROUP_ID` | ✅ | ✅ | ✅ | which Cost Center Group this belongs to |
| `GR_NAME` | ✅ (joined, display-only) | — | — | the group's name, for display in lists |
| `REMARKS` | ✅ | ✅ | ✅ | free-text notes |
| `COMP_CODE` | ✅ | ✅ (set by the service layer, not the API layer — see Known Issues) | — | company scope |
| `TOTAL_REC` | (paging only) | — | — | total row count for the grid, not a real data field |

## Relationships

`ACC_COST_CENTER_GROUP` is the parent of `ACC_COST_CENTER` via `GROUP_ID`. From there,
`ACC_COST_CENTER` feeds the Voucher entry screen (cost-center picker on each line), the Draft
Voucher entry screen, and Cost-Center-wise Ledger / Summary Reports.

| Related Table / Module | Relationship | Where it's used | Why |
|---|---|---|---|
| `ACC_COST_CENTER_GROUP` | Parent (Cost Center belongs to a group) | Add/Edit form's "* Group" dropdown | Lets reports subtotal by group later. |
| Voucher entry screen | Picked per voucher line via `COST_CENTER_ID` | Voucher line entry | Tags a transaction with which cost center it belongs to. Optional — defaults to a sentinel "N/A" record (ID 1) rather than null if the user picks nothing. |
| Draft Voucher entry screen | Same `COST_CENTER_ID` picker | Draft voucher line entry | Same as above, before the voucher is finalized. |
| Ledger / Summary Reports | Joined on `COST_CENTER_ID` | `CostCenterWiseLadgerSummaryReport.rdlc`, `LedgerWiseCostCenterSummaryReport.rdlc` | Shows transactions grouped/filtered by cost center. |
| Department module | Cross-referenced | `Views\Department\_CostCenterList.cshtml` | Not explored in depth — noted for awareness. |

Technical reference (file : line): Voucher entry (cost-center picker)
`Client\app\controllers\voucherMastersController.js:287,315-316,569,865-866` — binds
`vm.ACC_VOUCHER_DETAIL.COST_CENTER_ID`, defaults to `{Value:1, Text:'N/A'}` when unset; Draft
voucher entry `Client\app\controllers\draftVouchersController.js` — same `COST_CENTER_ID`
binding; Voucher/report repositories referencing `COST_CENTER_ID`
`ERP.BLL\VoucherMasterService.cs`, `ERP.Data\VoucherMasterRepository.cs`,
`ERP.Data\DraftVoucherRepository.cs`, `ERP.Data\ReportRepository.cs`; Stored procedures joining
cost center into vouchers/reports `PKG_ACCOUNTING.sql:2309,3576,4535,4640,7020,8116,8166`; GL
account search / DDL stored procedure (own package, not in `PKG_ACCOUNTING.sql`)
`PKG_ACC_COST_CENTER.sql` — `ACC_COST_CENTER_SELECT` (options 3000 list, 3001 DDL, 3002 DDL w/
office+department).

## Known Issues

- **Delete can orphan voucher data**: `Delete(id)` runs
  `delete from ACC_COST_CENTER where COST_CENTER_ID='{id}'` with no `COMP_CODE` scoping and no
  check for existing voucher usage. Voucher line tables (`ACC_VOUCHER_DETAIL`,
  `ACC_DRAFT_VOUCHER_DETAIL`, `ACC_TEMP_VOUCHER_DETAIL`) all store `COST_CENTER_ID` as a plain
  reference — deleting a Cost Center already used on a voucher orphans those references, and
  since reports use inner joins in places, this can silently drop those historical voucher lines
  from cost-center-wise ledger reports. (Source: `CostCenterRepository.cs:19-23`; report joins at
  `PKG_ACCOUNTING.sql:2309,4535,7020`.)
- **One DDL search option has no company filter**: `ACC_COST_CENTER_SELECT` option `3002` (the
  office/department-concatenated DDL variant) accepts no `COMP_CODE` parameter at all — company
  scoping there depends entirely on whatever office/department IDs the caller happens to pass.
  (Source: `PKG_ACC_COST_CENTER.sql`, option 3002.)
- **Inconsistent company-code assignment between sibling controllers**:
  `CostCenterGroupsController` sets `model.COMP_CODE` itself at the API layer, but
  `CostCentersController` does not — it relies entirely on the BLL layer
  (`CostCenterService.cs:51`) to set it. Works today, but it's an inconsistent pattern between
  two near-identical controllers, and a trap if that BLL call is ever refactored or bypassed.
- **No stored procedures for Save/Delete**: same as Cost Center Group — the C# repository builds
  raw SQL via string concatenation (`String.Format`) instead of parameters, a
  SQL-injection-shaped pattern.

## Unused Columns

How this was checked: every column of `ACC_COST_CENTER` was grepped (whole word,
case-insensitive) across both repos. Two different column sets exist for this table across the
codebase: the old, now-dead `acc_cost_center_insert` stored procedure
(`PKG_ACCOUNTING.sql:2149-2168`, zero C# callers found), and the live raw-SQL insert the app
actually uses (`CostCenterRepository.cs:141-144`). `PKG_ACC_COST_CENTER.sql`'s
`ACC_COST_CENTER_SELECT` additionally references 3 columns that don't appear in either insert
path at all.

| Column | Verdict | Confidence |
|---|---|---|
| `HR_COMPANY_ID` | Unused by the live app. Only ever referenced as an optional filter parameter (`pHR_COMPANY_ID`) in `ACC_COST_CENTER_SELECT` — but `CostCenterRepository.GetListByFilter` (the only caller) never passes it, so it's permanently `NULL` in every call. The `ACC_COST_CENTER` C# model has no property for it. No insert anywhere (dead or live) ever sets it. | High |
| `HR_OFFICE_ID` | Unused by the live app. Same pattern as `HR_COMPANY_ID` — accepted as a filter parameter that's never supplied, no model property, never inserted. | High |
| `HR_DEPARTMENT_ID_LST` | Unused by the live app. Same pattern. The one function that meaningfully reads it, `GET_COST_CENTER_INFO` (`PKG_ACC_COST_CENTER.sql:5-65`), is itself never called from any C# code — and its only other caller, `PKG_ACC_MISC_REPORT.sql`, is also never invoked from this app. The entire consumption chain for these 3 columns is orphaned. | High |

All other columns (`COST_CENTER_ID`, `COST_CENTER_NAME`, `COMP_CODE`, `REMARKS`,
`COST_CENTER_CODE`, `GROUP_ID`) are actively used — see Fields above.

Note: `GR_NAME` (seen in list results) is not a real column — it's a correlated-subquery alias
(`(select NAME from ACC_COST_CENTER_GROUP where GROUP_ID=C.GROUP_ID...) AS GR_NAME`,
`CostCenterRepository.cs:72`), not a dead-column case.

Caveat: these 3 columns clearly exist in the physical table (they're referenced in
`WHERE`/`JOIN` clauses), but nothing found in either repository ever populates or displays them
for this app — they may serve some other HR-side consumer entirely outside both repositories,
which this audit can't see.
