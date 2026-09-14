# Table: ACC_COA_TYPE_CONFIG_D

```yaml
---
id: tbl:ACC_COA_TYPE_CONFIG_D
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, ACC_AC_CLASS_ID->ACC_AC_CLASS.ACC_AC_CLASS_ID, ACC_MAIN_CLASS_ID->ACC_MAIN_CLASS.ACC_MAIN_CLASS_ID, ACC_MAP_CLASS_ID->ACC_MAP_CLASS.ACC_MAP_CLASS_ID, ACC_AC_PARENT_CLASS_ID->ACC_AC_PARENT_CLASS.ACC_AC_PARENT_CLASS_ID, ACC_COA_TYPE_CONFIG_D_ID]
---
```

Detail table (one row per selected GL node) for a COA Type Configuration rule — points into the Chart of Accounts at whichever one of its 5 tree levels the parent header rule targets. Like its header table, no menu route, controller, API, or Angular screen exists to maintain it; reconstructed entirely from the Oracle package's stored procedures.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_COA_TYPE_CONFIG_D_ID` | — | PK | feature doc |
| `ACC_COA_TYPE_CONFIG_H_ID` | — | FK → `ACC_COA_TYPE_CONFIG_H` (the header rule) | feature doc |
| `ACC_AC_PARENT_CLASS_ID` | — | Nullable FK → `ACC_AC_PARENT_CLASS`; populated only when the header's layer is Parent Class | feature doc |
| `ACC_AC_CLASS_ID` | — | Nullable FK → `ACC_AC_CLASS`; populated only when the header's layer is Account Class | feature doc |
| `ACC_MAIN_CLASS_ID` | — | Nullable FK → `ACC_MAIN_CLASS`; populated only when the header's layer is Main Class | feature doc |
| `ACC_MAP_CLASS_ID` | — | Nullable FK → `ACC_MAP_CLASS`; populated only when the header's layer is Map Class | feature doc |
| `ACC_SUB_CLASS_ID` | — | Nullable FK → `ACC_SUB_CLASS`; populated only when the header's layer is Sub Class | feature doc |

Exactly one of the 5 level FKs is populated per row, matching the header's `LK_COA_LAYER_ID`.

## Keys & Indexes

**Primary key:** `SYS_C0030459` on `ACC_COA_TYPE_CONFIG_D_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |
| `FK_ACC_AC_CLASS_ID` | `ACC_AC_CLASS_ID` | `ACC_AC_CLASS.ACC_AC_CLASS_ID` |
| `FK_ACC_MAIN_CLASS_ID` | `ACC_MAIN_CLASS_ID` | `ACC_MAIN_CLASS.ACC_MAIN_CLASS_ID` |
| `FK_ACC_MAP_CLASS_ID` | `ACC_MAP_CLASS_ID` | `ACC_MAP_CLASS.ACC_MAP_CLASS_ID` |
| `FK_AC_PARENT_CLASS_ID` | `ACC_AC_PARENT_CLASS_ID` | `ACC_AC_PARENT_CLASS.ACC_AC_PARENT_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `SYS_C0030459` | yes | `ACC_COA_TYPE_CONFIG_D_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_COA_TYPE_CONFIG_D` belongs to `ACC_COA_TYPE_CONFIG_H` via `ACC_COA_TYPE_CONFIG_H_ID`, and each row's populated FK points into one of the 5 Chart of Accounts tree levels (`ACC_AC_PARENT_CLASS`, `ACC_AC_CLASS`, `ACC_MAIN_CLASS`, `ACC_MAP_CLASS`, `ACC_SUB_CLASS`). The consuming report queries (Income Tax, Direct Expenses, Purchase Account, Profit/Loss Ledger & Retained Earnings) join through this table to resolve "all GL nodes of COA Type X" at report time.

## Feature

[features/coa-type-configuration.md](../features/coa-type-configuration.md)
