# Table: ACC_COST_CENTER

```yaml
---
id: tbl:ACC_COST_CENTER
module: accounting
status: inferred
package: PKG_ACC_COST_CENTER
procedures: [ACC_COST_CENTER_SELECT, GET_COST_CENTER_INFO]
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, HR_OFFICE_ID->HR_OFFICE.HR_OFFICE_ID, COST_CENTER_ID]
---
```

Cost Center master — the actual selectable cost center (department, branch, project) tagged onto a voucher line so transactions can be reported "by cost center". Every Cost Center belongs to exactly one Cost Center Group.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `COST_CENTER_ID` | — | PK | feature doc |
| `COST_CENTER_CODE` | — | Auto-generated code, read-only on the form | feature doc |
| `COST_CENTER_NAME` | — | The cost center's name | feature doc |
| `GROUP_ID` | — | FK → `ACC_COST_CENTER_GROUP` | feature doc |
| `REMARKS` | — | Free-text notes | feature doc |
| `COMP_CODE` | — | Company scope | feature doc |
| `HR_COMPANY_ID` | — | Optional filter parameter on `ACC_COST_CENTER_SELECT`; never passed by the only caller, so always `NULL` in practice, and no C# model property exists for it | feature doc (unused-columns audit) |
| `HR_OFFICE_ID` | — | Same pattern as `HR_COMPANY_ID` — accepted as a filter parameter, never supplied, no model property | feature doc (unused-columns audit) |
| `HR_DEPARTMENT_ID_LST` | — | Read only by `GET_COST_CENTER_INFO`, which itself is never called from any C# code — orphaned consumption chain | feature doc (unused-columns audit) |

`GR_NAME` seen in list results is not a real column — it's a correlated-subquery alias (`ACC_COST_CENTER_GROUP.NAME`), not physically on this table. `TOTAL_REC` is a paging artifact, not a data column.

## Keys & Indexes

**Primary key:** `PK_ACC_COST_CENTER` on `COST_CENTER_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_COST_CENTER_NAME` | `GROUP_ID`, `COST_CENTER_NAME` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_COST_CNTR_HR_COMP_ID` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_COST_CNTR_HR_OFFICE_ID` | `HR_OFFICE_ID` | `HR_OFFICE.HR_OFFICE_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_COST_CENTER` | yes | `COST_CENTER_ID` |
| `UK_COST_CENTER_NAME` | yes | `GROUP_ID`, `COST_CENTER_NAME` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_COST_CENTER_GROUP` is the parent of `ACC_COST_CENTER` via `GROUP_ID` (one-level grouping only, used for report subtotaling). `ACC_COST_CENTER` feeds the Voucher entry screen and Draft Voucher entry screen (`COST_CENTER_ID` picked per voucher line, defaults to a sentinel "N/A" record with ID 1 rather than null), and is joined into Cost-Center-wise Ledger / Summary Reports. Voucher line tables (`ACC_VOUCHER_DETAIL`, `ACC_DRAFT_VOUCHER_DETAIL`, `ACC_TEMP_VOUCHER_DETAIL`) store `COST_CENTER_ID` as a plain reference with no enforced FK, so deleting a Cost Center already in use can orphan those references.

## Feature

[features/cost-center.md](../features/cost-center.md), [features/cost-center-group.md](../features/cost-center-group.md)
