# Feature: Cost Center Group

```yaml
---
id: feat:acc-cost-center-group
module: accounting
category: master-data
procedure: ACC_COST_CENTER_GROUP_SELECT
mvc: CostCenterGroupController.Index
api: [GET api/accounting/cost-center-groups/get-cost-center-groups-by-filter -> CostCenterGroupsController.GetListByFilter, GET api/accounting/cost-center-groups/get-cost-center-groups-for-ddl -> CostCenterGroupsController.GetListForDDL, GET api/accounting/cost-center-groups/get-cost-center-groups -> CostCenterGroupsController.GetCostCenterGroups, POST api/accounting/cost-center-groups/save-cost-center-group -> CostCenterGroupsController.SaveCostCenterGroup, PUT api/accounting/cost-center-groups/update-cost-center-group -> CostCenterGroupsController.UpdateCostCenterGroup, GET api/accounting/cost-center-groups/get-cost-center-group -> CostCenterGroupsController.GetCostCenterGroup, DELETE api/accounting/cost-center-groups/delete-cost-center-group -> CostCenterGroupsController.DeleteCostCenterGroup]
tables: [ACC_COST_CENTER_GROUP, ACC_COST_CENTER]
status: verified
---
```

## Overview

Cost Center Group (Accounting > Cost Center Group) is a simple grouping/label for Cost Centers —
e.g. grouping cost centers by division or region, backed by table `ACC_COST_CENTER_GROUP`. It's
a one-level parent of Cost Center (not a multi-level tree like Chart of Accounts): every Cost
Center belongs to exactly one Cost Center Group. Its only real job is to give reports a way to
subtotal cost centers by group.

## Fields

### Add/Edit form

| Frontend Label (raw) | Bound To | Input Type | Required? | Meaning |
|---|---|---|---|---|
| "Cost Center" *(mislabeled — see below)* | `vm.costCenterGroup.NAME` | Text | Yes | The group's name. Error shown: "Cost Center Group Name is required". |
| "Display Order" | `vm.costCenterGroup.DISPLAY_ORDER` | Text (numeric) | Yes | Controls the order groups appear in on lists/reports. |
| "Remarks" | `vm.costCenterGroup.REMARKS` | Textarea | No | Free-text notes. |

The Add/Edit form's Name field is labeled "Cost Center", not "Cost Center Group" or "Name" —
confusing, since this screen is for the group, not an individual cost center. See Known Issues.

List/search screen label: "Cost Center Group" → `vm.form.NAME` (text filter).

### Columns actually used (`ACC_COST_CENTER_GROUP`)

| Column | List | Add | Edit | Notes |
|---|---|---|---|---|
| `GROUP_ID` | ✅ | (auto) | ✅ (key) | |
| `NAME` | ✅ | ✅ | ✅ | the group's name |
| `DISPLAY_ORDER` | ✅ | ✅ | ✅ | sort order |
| `REMARKS` | ✅ | ✅ | ✅ | free-text notes |
| `COMP_CODE` | ✅ | ✅ | — (not changed on update) | company scope |
| `TOTAL_REC` | (paging only) | — | — | total row count for the grid, not a real data field |

## Relationships

`ACC_COST_CENTER_GROUP` is the parent of `ACC_COST_CENTER` via `GROUP_ID`, and feeds the Cost
Center Add/Edit screen's "* Group" dropdown and Ledger / Summary Reports grouped by Cost Center
Group.

| Related Table / Module | Relationship | Where it's used | Why |
|---|---|---|---|
| `ACC_COST_CENTER` | Foreign key: `GROUP_ID` | Every Cost Center record | Each Cost Center belongs to exactly one group. |
| Cost Center Add/Edit screen | Populates the "* Group" dropdown | `get-cost-center-groups-for-ddl` API | Lets the user pick which group a new/edited Cost Center belongs to. |
| Ledger / Summary Reports | Joined for the `GR_NAME` column and grouping | `CostCenterGroupLadgerSummaryReport.rdlc` and similar | Reports subtotal transactions by Cost Center Group. |

Technical reference (file : line): Repository (typo: "Cneter" not "Center" — baked into the
class name and DI wiring) `ERP.Data\CostCneterGroupRepository.cs`, `ICostCneterGroupRepository.cs`;
API controller `Api\CostCenterGroupsController.cs` (`get-cost-center-groups-for-ddl` at line 38);
Cost Center's Group dropdown `Views\CostCenter\_Edit.cshtml:75-82`; Stored procedure (read-only;
own package file, not in `PKG_ACCOUNTING.sql`) `PKG_ACC_COST_CENTER_GROUP.sql` —
`ACC_COST_CENTER_GROUP_SELECT`; Report joins `PKG_ACC_COST_CENTER.sql:104`
(`NVL(G.NAME,'N/A') AS GR_NAME`).

## Known Issues

- **Mislabeled form field**: the Add/Edit form's Name field is labeled "Cost Center" instead of
  something like "Cost Center Group Name" — confusing since this screen creates a group, not an
  individual cost center.
- **Delete has no safety checks**: `Delete(id)` runs
  `delete from ACC_COST_CENTER_GROUP where GROUP_ID='{id}'` with no `COMP_CODE` scoping (a group
  ID from another company could be deleted) and no check for Cost Centers still assigned to this
  group — deleting a group in use leaves those Cost Centers pointing at a `GROUP_ID` that no
  longer exists. (Source: `CostCneterGroupRepository.cs:168-172`.)
- **No stored procedures for Save/Delete**: unlike some other menus, Cost Center Group has no
  PL/SQL procedure for insert/update/delete at all — the C# repository builds raw SQL by directly
  concatenating values into the query string (`String.Format`) rather than using parameters. This
  is a SQL-injection-shaped pattern, even though today's inputs come from internal validated
  fields.
- **Filename/class typo**: the repository is named `CostCneterGroupRepository`/
  `ICostCneterGroupRepository` (missing the "e" — "Cneter" instead of "Center"). This isn't just
  a filename quirk — the misspelled class name is used directly in the BLL's constructor
  parameter type, so it's baked into how the app wires dependencies, not something that can be
  silently renamed without touching that wiring.

## Unused Columns

How this was checked: every column of `ACC_COST_CENTER_GROUP` was grepped (whole word,
case-insensitive) across both repos.

**Result: no unused columns.** All 5 columns (`GROUP_ID`, `NAME`, `COMP_CODE`, `DISPLAY_ORDER`,
`REMARKS`) are confirmed used — `GROUP_ID` as the FK target from `ACC_COST_CENTER.GROUP_ID`,
`NAME` in the form/filter and reused in the cost-center-group report, `DISPLAY_ORDER` as the
list/grid sort order, `REMARKS`/`COMP_CODE` as form fields.

Confidence: high — a small table, fully traced.
