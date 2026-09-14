# Table: ACC_MAIN_CLASS

```yaml
---
id: tbl:ACC_MAIN_CLASS
module: accounting
status: inferred
model: ACC_MAIN_CLASSModel
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_AC_CLASS_ID->ACC_AC_CLASS.ACC_AC_CLASS_ID, ACC_MAIN_CLASS_ID]
---
```

Level 3 (code `M`) of the 5-level Chart of Accounts hierarchy — a broad group under an Account Class (e.g. "Accounts Receivables", code `10203`). Full Add/Edit/Delete support in the UI.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_MAIN_CLASS_ID` | — | PK, key on edit | feature doc |
| `ACC_AC_CLASS_ID` | — | FK → `ACC_AC_CLASS`, which Account Class this sits under | feature doc |
| `AC_CODE` | — | Inherited from the Account Class | feature doc |
| `MAIN_CODE` | — | Auto-generated short code (e.g. `10203`) | feature doc |
| `MAIN_NAME` | — | Display name; the only field the user actually types | feature doc |
| `COMP_CODE` | — | Company scope | feature doc |

All 6 real columns confirmed in use. `CTRL_GRP` and `DISP_MAIN_NAME` appear as properties on `ACC_MAIN_CLASSModel.cs` but are **not real persisted columns** — they are computed literal/expression aliases from report/autocomplete queries (`'M' as CTRL_GRP`, `mc.MAIN_NAME||' << '||ac.CLASS_NAME as DISP_MAIN_NAME`), never part of any INSERT/UPDATE (per `chart-of-accounts.md` Unused Columns audit).

## Keys & Indexes

**Primary key:** `PK_ACC_MAIN_CLASS` on `ACC_MAIN_CLASS_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACC_AC_CLASS_MAINCLASS` | `ACC_AC_CLASS_ID` | `ACC_AC_CLASS.ACC_AC_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_MAIN_CLASS` | yes | `ACC_MAIN_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Sits between `ACC_AC_CLASS` (parent, via `ACC_AC_CLASS_ID`) and `ACC_MAP_CLASS` (child, via `ACC_MAP_CLASS.ACC_MAIN_CLASS_ID`) in the Chart of Accounts tree. Also referenced (nullable FK) from `ACC_COA_TYPE_CONFIG_D` when a COA Type rule is configured at the Main Class level.

**Known issue:** `MainClassRepository.Delete` runs a raw `DELETE ... WHERE <id>=...` with no check for existing child `ACC_MAP_CLASS` rows and no company filter — can orphan children (per `chart-of-accounts.md` Known Issues).

## Feature

[features/chart-of-accounts.md](../features/chart-of-accounts.md)
