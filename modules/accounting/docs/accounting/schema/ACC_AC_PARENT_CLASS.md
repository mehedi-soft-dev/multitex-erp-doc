# Table: ACC_AC_PARENT_CLASS

```yaml
---
id: tbl:ACC_AC_PARENT_CLASS
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_AC_PARENT_CLASS_ID]
---
```

Level 1 (code `T`) of the 5-level Chart of Accounts hierarchy — the 5 fixed top-level groups (Assets, Liabilities, Income, Expenditure, Equity). Read-only in the UI; no Add/Edit screen exists for this level.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_AC_PARENT_CLASS_ID` | — | PK | feature doc |
| `NAME` | — | Display name (e.g. "ASSETS") | feature doc |
| `PARENT_CODE` | — | Sort/grouping code | feature doc |
| `COMP_CODE` | — | Company scope | feature doc |

All 4 columns are confirmed in use, including in Balance Sheet / Income Statement report rollups (`chart-of-accounts.md` Unused Columns audit).

## Keys & Indexes

**Primary key:** `PK_AC_PARENT_CLASS` on `ACC_AC_PARENT_CLASS_ID`

**Foreign keys:** none defined at the DB level.

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_AC_PARENT_CLASS` | yes | `ACC_AC_PARENT_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Top of the Chart of Accounts tree: `ACC_AC_PARENT_CLASS` → `ACC_AC_CLASS` → `ACC_MAIN_CLASS` → `ACC_MAP_CLASS` → `ACC_SUB_CLASS`. `ACC_AC_CLASS.ACC_AC_PARENT_CLASS_ID` is the FK down into this table. Also referenced (nullable FK) from `ACC_COA_TYPE_CONFIG_D` when a COA Type rule is configured at the Parent Class level.

## Feature

[features/chart-of-accounts.md](../features/chart-of-accounts.md)
