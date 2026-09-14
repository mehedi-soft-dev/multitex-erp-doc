# Table: ACC_SUB_CLASS

```yaml
---
id: tbl:ACC_SUB_CLASS
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_MAP_CLASS_ID->ACC_MAP_CLASS.ACC_MAP_CLASS_ID, LK_NATURE_ID->LOOKUP_DATA.LOOKUP_DATA_ID, ACC_SUB_CLASS_ID]
---
```

Level 5 (code `G`) of the 5-level Chart of Accounts hierarchy — the actual GL account posted to on a voucher (e.g. "Styletex Limited", code `102030009`). Full Add/Edit/Delete support in the UI, plus the only level with a real "is this account in use?" check before delete.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_SUB_CLASS_ID` | — | PK, key on edit | feature doc |
| `ACC_MAP_CLASS_ID` | — | FK → `ACC_MAP_CLASS`, which Map Class this sits under; changed only via "Change Parent Group" | feature doc |
| `SUB_CODE` | — | Auto-generated leaf account code (e.g. `102030009` = `MAIN_CODE` + 4-digit running number) | feature doc |
| `SUB_NAME` | — | Account name; the only field the user actually types | feature doc |
| `AC_CODE` | — | Inherited/derived code from parent levels | feature doc |
| `MAIN_CODE` | — | Inherited/derived code from parent levels | feature doc |
| `MAP_CODE` | — | Inherited/derived code from parent levels | feature doc |
| `MCODE` | — | **Write-only / effectively unused** — inserted (`pMCODE`) and round-tripped, but no other reference anywhere in either repo (confidence: high) | feature doc |
| `SL` | — | **Write-only / effectively unused** — inserted, round-tripped, never read for any real purpose (confidence: high) | feature doc |
| `IS_DUMMY` | — | Marks a placeholder/non-postable account | feature doc |
| `IS_CHECK_BAL` | — | Drives whether the account's running balance is shown (reports/autocomplete) | feature doc |
| `IS_EXCLUDE4AUDIT` | — | Excludes the account from audit reports | feature doc |
| `LK_NATURE_ID` | — | FK to a "nature" lookup; scopes GL search by company via `HR_COMPANY` | feature doc |
| `COMP_CODE` | — | Company scope. **Data-quality issue:** some rows have `COMP_CODE = NULL` instead of `001` (confirmed on `mtexdev`, company `001`) | feature doc |

## Keys & Indexes

**Primary key:** `PK_ACC_SUB_CLASS` on `ACC_SUB_CLASS_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_COA_CODE01` | `COMP_CODE`, `AC_CODE`, `MAIN_CODE`, `SUB_CODE` |
| `UK_SUB_CODE` | `SUB_CODE` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCMAPCLASS_ACCSUBCLASS` | `ACC_MAP_CLASS_ID` | `ACC_MAP_CLASS.ACC_MAP_CLASS_ID` |
| `FK_LKNATUREID_ACCSUBCLS` | `LK_NATURE_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `IDX_IS_DUMMY_ACCSUBCLS` | no | `IS_DUMMY` |
| `PK_ACC_SUB_CLASS` | yes | `ACC_SUB_CLASS_ID` |
| `UK_SUB_CODE` | yes | `SUB_CODE` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Bottom of the Chart of Accounts tree, child of `ACC_MAP_CLASS` (via `ACC_MAP_CLASS_ID`). This is the table every voucher line ultimately points to: referenced by `ACC_VOUCHER_DETAIL` and `ACC_DRAFT_VOUCHER_DETAIL` (via `SUB_CODE`, checked by the delete-guard) and by `ACC_TEMP_VOUCHER_DETAIL`/`ACC_TEMP_DRAFT_VOUCHER` (via `ACC_SUB_CLASS_ID`) on every voucher/draft-voucher line. Also referenced (nullable FK) from `ACC_COA_TYPE_CONFIG_D` when a COA Type rule is configured at the Sub Class (GL account) level.

**Known issue:** the delete-guard (`VoucherMasterRepository.CheckGlTransactionExist`) filters only by `SUB_CODE` — the `compCode` parameter is passed but never used in the SQL, so account codes not unique across companies can cause a false-match block (per `chart-of-accounts.md` Known Issues).

## Feature

[features/chart-of-accounts.md](../features/chart-of-accounts.md)
