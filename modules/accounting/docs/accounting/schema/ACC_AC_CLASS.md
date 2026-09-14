# Table: ACC_AC_CLASS

```yaml
---
id: tbl:ACC_AC_CLASS
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_AC_PARENT_CLASS_ID->ACC_AC_PARENT_CLASS.ACC_AC_PARENT_CLASS_ID, ACC_AC_CLASS_ID]
---
```

Level 2 (code `A`) of the 5-level Chart of Accounts hierarchy — a sub-category within a Parent Class (e.g. "CURRENT ASSET" under Assets). Read-only in the UI; a Save stored procedure exists (`acc_ac_class_insert`) but has a known column-mapping bug and is not called by any live C# code.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_AC_CLASS_ID` | — | PK | feature doc |
| `ACC_AC_PARENT_CLASS_ID` | — | FK → `ACC_AC_PARENT_CLASS` | feature doc |
| `AC_CODE` | — | Short numeric code (e.g. `102`) | feature doc |
| `CLASS_NAME` | — | Display name (e.g. "CURRENT ASSET") | feature doc |
| `AC_GROUP` | — | Grouping code; drives Balance Sheet/Income Statement report grouping (`rptBalanceSheet.rdlc`, `rptIncomeStatementDetail.rdlc`) | feature doc |
| `COMP_CODE` | — | Company scope | feature doc |

All 6 columns confirmed in use (`chart-of-accounts.md` Unused Columns audit, confidence: high).

## Keys & Indexes

**Primary key:** `PK_AC_CLASS` on `ACC_AC_CLASS_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_PRENT_CLASS_AC_CLASS` | `ACC_AC_PARENT_CLASS_ID` | `ACC_AC_PARENT_CLASS.ACC_AC_PARENT_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_AC_CLASS` | yes | `ACC_AC_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Sits between `ACC_AC_PARENT_CLASS` (parent, via `ACC_AC_PARENT_CLASS_ID`) and `ACC_MAIN_CLASS` (child, via `ACC_MAIN_CLASS.ACC_AC_CLASS_ID`) in the Chart of Accounts tree. Also referenced (nullable FK) from `ACC_COA_TYPE_CONFIG_D` when a COA Type rule is configured at the Account Class level.

**Known issue:** the `acc_ac_class_insert` stored procedure inserts the new sequence ID into `COMP_CODE` and the caller's ID into `ACC_AC_CLASS_ID` — a shifted-column bug. Dormant (no C# caller), but a live trap if wired up later. (Source: `PKG_ACCOUNTING.sql:2123-2147`, per `chart-of-accounts.md` Known Issues.)

## Feature

[features/chart-of-accounts.md](../features/chart-of-accounts.md)
