# Table: ACC_MAP_CLASS

```yaml
---
id: tbl:ACC_MAP_CLASS
module: accounting
status: inferred
package: PKG_ACCOUNTING
procedures: [acc_map_class_select]
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_MAIN_CLASS_ID->ACC_MAIN_CLASS.ACC_MAIN_CLASS_ID, ACC_MAP_CLASS_ID]
---
```

Level 4 (code `N`) of the 5-level Chart of Accounts hierarchy — a sub-group under a Main Class (e.g. "Accounts Receivable-Garments", code `0001`). Full Add/Edit/Delete support in the UI; also updated by the "Change Parent Group" feature.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_MAP_CLASS_ID` | — | PK, key on edit | feature doc |
| `ACC_MAIN_CLASS_ID` | — | FK → `ACC_MAIN_CLASS`, which Main Class this sits under | feature doc |
| `MAP_CODE` | — | Auto-generated short code (e.g. `0001`) | feature doc |
| `MAP_NAME` | — | Display name; the only field the user actually types | feature doc |
| `PRNT_CODE` | — | Parent's code, copied down. **Write-only / effectively unused** — the real-value assignment is commented out (`ERP.BLL/UnilayerChartofAccountService.cs:248`); always inserted as `NULL` in practice (confidence: medium-high) | feature doc |
| `AC_CODE` | — | Inherited from parent levels | feature doc |
| `MAIN_CODE` | — | Inherited from parent levels | feature doc |
| `COMP_CODE` | — | Company scope | feature doc |

`CTRL_GRP` appears as a model property but is a computed literal (`'N' as CTRL_GRP`) from the GL-account autocomplete report, not a real inserted/updated column.

## Keys & Indexes

**Primary key:** `PK_ACC_MAP_CLASS` on `ACC_MAP_CLASS_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCMAPCLASS_ACCMAINCLASS` | `ACC_MAIN_CLASS_ID` | `ACC_MAIN_CLASS.ACC_MAIN_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_MAP_CLASS` | yes | `ACC_MAP_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Sits between `ACC_MAIN_CLASS` (parent, via `ACC_MAIN_CLASS_ID`) and `ACC_SUB_CLASS` (child, via `ACC_SUB_CLASS.ACC_MAP_CLASS_ID`) in the Chart of Accounts tree. Also referenced (nullable FK) from `ACC_COA_TYPE_CONFIG_D` when a COA Type rule is configured at the Map Class level.

**Known issues:** `acc_map_class_select` option 3000 (default path) has no company filter, unlike sibling option 3001; `MapClassRepository.Delete` runs a raw delete with no check for existing child `ACC_SUB_CLASS` rows and no company filter, which can orphan children (per `chart-of-accounts.md` Known Issues).

## Feature

[features/chart-of-accounts.md](../features/chart-of-accounts.md)
