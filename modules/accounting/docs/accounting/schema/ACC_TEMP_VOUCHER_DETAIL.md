# Table: ACC_TEMP_VOUCHER_DETAIL

```yaml
---
id: tbl:ACC_TEMP_VOUCHER_DETAIL
module: accounting
status: inferred
model: ACC_TEMP_VOUCHER_DETAIL
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, USER_ID->SC_USER.SC_USER_ID]
---
```

Per-user scratch/staging table for the final-Voucher line-entry grid — holds in-progress lines (keyed by `USER_ID`) before they are committed into `ACC_VOUCHER_DETAIL` on Save/Update.

**Status:** inferred from feature docs; no `ALL_TAB_COLUMNS` dump. No explicit C# types stated beyond identity/date/amount naming convention.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `TEMP_ID` | Int64 (inferred) | PK | features/voucher.md, features/draft-voucher.md |
| `COMP_CODE` | string | Company scope; select procedure's `pCOMP_CODE` filter is commented out (Known Issue), but the column itself is genuinely load-bearing — selected into `ACC_VOUCHER_DETAIL.COMP_CODE` at insert | features/voucher.md |
| `AC_CODE` | string | Chart-of-Accounts code segment | features/voucher.md |
| `MAIN_CODE` | string | Chart-of-Accounts code segment | features/voucher.md |
| `ACC_SUB_CLASS_ID` | Int64 (inferred) | FK → `ACC_SUB_CLASS` | features/voucher.md |
| `SUB_CODE` | string | Chart-of-Accounts code segment | features/voucher.md |
| `SUB_NAME` | string | Account display name | features/voucher.md |
| `DR_AMT` | decimal (inferred) | Debit amount | features/voucher.md |
| `CR_AMT` | decimal (inferred) | Credit amount | features/voucher.md |
| `DESCRIPTION` | string | Per-line narration | features/voucher.md |
| `XSTATUS` | ? | Type not stated | features/voucher.md |
| `MAP_CODE` | string | Read back from `ACC_VOUCHER_DETAIL.M_CODE` | features/voucher.md |
| `USER_ID` | Int64 (inferred) | Keys the per-user staging rows | features/voucher.md |
| `COST_CENTER_ID` | Int64 (inferred) | FK → Cost Center | features/voucher.md |
| `CURRENCY_ID` | Int64 (inferred) | FK → currency | features/voucher.md |
| `EXCHANGE_RATE` | decimal (inferred) | | features/voucher.md |
| `LK_VOUCHER_FOR_TYPE_ID` | Int64 (inferred) | "Voucher For" type lookup | features/voucher.md |
| `VOUCHER_FOR_ID` | Int64 (inferred) | Secondary-party reference id | features/voucher.md |
| `BILL_NO` | string | Bill sub-flow | features/voucher.md |
| `BILL_REF_ID` | Int64 (inferred) | Bill sub-flow | features/voucher.md |
| `BILL_DETAIL_ID` | Int64 (inferred) | Bill sub-flow | features/voucher.md |
| `VOUCHER_MASTER_ID` | Int64 (inferred) | Round-tripped when reopening/editing | features/voucher.md |
| `VOUCHER_DETAIL_ID` | Int64 (inferred) | Round-tripped when reopening/editing | features/voucher.md |
| `HAS_CHILD` | string (inferred) | Y/N; disables Edit/Delete on the grid when the line is referenced elsewhere | features/voucher.md |
| `CP_DR_AMT` | decimal (inferred) | Accepted by the insert procedure, never set by the repository — write-only/unreachable from the UI | features/voucher.md |
| `CP_CR_AMT` | decimal (inferred) | Same as `CP_DR_AMT` | features/voucher.md |

**Not real columns (joins/computed):** `COST_CENTER_NAME`, `VOUCHER_FOR_NAME`, `VOUCHER_FOR_TYPE_NAME` — C# model properties populated via joins in the select procedure, not persisted columns.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACC_TMP_VCHDTL` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |
| `FK_ACC_TMP_VCHDTL_SCUSER` | `USER_ID` | `SC_USER.SC_USER_ID` |

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_TEMP_VOUCHER_DETAIL` holds per-user scratch lines for the final-Voucher entry grid, scoped by `USER_ID`; rows are copied into `ACC_VOUCHER_DETAIL` (child of `ACC_VOUCHER_MASTER` via `VOUCHER_MASTER_ID`) on Save/Update. Structurally mirrors the draft-voucher equivalent, `ACC_TEMP_DRAFT_VOUCHER`. Account resolves via `ACC_SUB_CLASS_ID` into Chart of Accounts; cost center via `COST_CENTER_ID`.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md)
