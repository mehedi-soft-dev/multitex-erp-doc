# Table: ACC_COST_CENTER_GROUP

```yaml
---
id: tbl:ACC_COST_CENTER_GROUP
module: accounting
status: inferred
package: PKG_ACC_COST_CENTER_GROUP
procedures: [ACC_COST_CENTER_GROUP_SELECT]
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [GROUP_ID]
---
```

Cost Center Group master — a simple grouping/label for Cost Centers (e.g. by division or region), used purely so reports can subtotal cost centers by group. Not a multi-level tree like Chart of Accounts: every Cost Center belongs to exactly one group.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `GROUP_ID` | — | PK | feature doc |
| `NAME` | — | The group's name | feature doc |
| `DISPLAY_ORDER` | — | Sort order for lists/reports | feature doc |
| `REMARKS` | — | Free-text notes | feature doc |
| `COMP_CODE` | — | Company scope (set on insert; not changed on update) | feature doc |

All 5 columns confirmed in use (`cost-center-group.md` Unused Columns audit, confidence: high).

## Keys & Indexes

**Primary key:** `ACC_COST_CENTER_GROUP_PK` on `GROUP_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_CST_CNTR_GRP_NAME` | `NAME` |

**Foreign keys:** none defined at the DB level.

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `ACC_COST_CENTER_GROUP_PK` | yes | `GROUP_ID` |
| `UK_CST_CNTR_GRP_NAME` | yes | `NAME` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_COST_CENTER_GROUP` is the parent of `ACC_COST_CENTER` via `GROUP_ID`, and feeds the Cost Center Add/Edit screen's "* Group" dropdown plus Ledger / Summary Reports grouped by Cost Center Group (joined for the `GR_NAME` display column). No `COMP_CODE` scoping or in-use check exists on delete, so a group ID from another company could be deleted, or a group still assigned to Cost Centers, leaving those records pointing at a `GROUP_ID` that no longer exists.

## Feature

[features/cost-center-group.md](../features/cost-center-group.md), [features/cost-center.md](../features/cost-center.md)
