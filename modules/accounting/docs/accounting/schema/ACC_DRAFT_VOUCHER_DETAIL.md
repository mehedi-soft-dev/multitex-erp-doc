# Table: ACC_DRAFT_VOUCHER_DETAIL

```yaml
---
id: tbl:ACC_DRAFT_VOUCHER_DETAIL
module: accounting
status: inferred
model: ACC_VOUCHER_DETAIL
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, LK_VOUCHER_FOR_TYPE_ID->LOOKUP_DATA.LOOKUP_DATA_ID]
---
```

Line/detail table for a Draft Voucher — mirrors `ACC_VOUCHER_DETAIL` but without the Bill sub-flow or compliance columns. Note: bound to the shared `ACC_VOUCHER_DETAIL` C# model class, not a distinct draft-specific model.

**Status:** inferred from feature docs; no `ALL_TAB_COLUMNS` dump.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_DETAIL_ID` | Int64 (inferred) | PK | features/draft-voucher.md |
| `VOUCHER_MASTER_ID` | Int64 (inferred) | FK → `ACC_DRAFT_VOUCHER` | features/draft-voucher.md |
| `COMP_CODE` | string | Company scope | features/draft-voucher.md |
| `AC_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md, features/chart-of-accounts.md |
| `MAIN_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md, features/chart-of-accounts.md |
| `ACC_SUB_CLASS_ID` | Int64 (inferred) | FK → `ACC_SUB_CLASS` (Chart of Accounts) | features/draft-voucher.md, features/chart-of-accounts.md |
| `SUB_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md, features/chart-of-accounts.md |
| `DR_AMT` | decimal (inferred) | Debit amount | features/draft-voucher.md |
| `CR_AMT` | decimal (inferred) | Credit amount | features/draft-voucher.md |
| `COST_CENTER_ID` | Int64 (inferred) | FK → Cost Center | features/draft-voucher.md |
| `DESCRIPTION` | string | Per-line narration | features/draft-voucher.md |
| `M_CODE` | string | Hardcoded `'000'` on every insert path — write-only/effectively unused; the one place it's read back (`ACC_TEMP_DRAFT_VOUCHER.MAP_CODE`) is itself dead (only settable via the reopen-draft path) | features/draft-voucher.md |
| `XSTATUS` | ? | Type not stated | features/draft-voucher.md |
| `CURRENCY_ID` | Int64 (inferred) | FK → currency | features/draft-voucher.md |
| `EXCHANGE_RATE` | decimal (inferred) | | features/draft-voucher.md |
| `LK_VOUCHER_FOR_TYPE_ID` | Int64 (inferred) | "Voucher For" type lookup | features/draft-voucher.md |
| `VOUCHER_FOR_ID` | Int64 (inferred) | Secondary-party reference id | features/draft-voucher.md |
| `BILL_NO` | string | | features/draft-voucher.md |
| `IS_B_OR_C_AC` | string (inferred) | `B`=Bill, `C`=Bill Collection; only ever written by `ACC_DRAFT_VCH_SAVE4MISC_SRC`, never read back — unused | features/draft-voucher.md |

**Gap / unconfirmed:** `BILL_REF_ID` and `BILL_DETAIL_ID` are set client-side (`draftVouchersController.js`) but never sent to the server (`SaveTemVoucheDetail` doesn't pass them, and the insert procedure's column list never references them) — the source doc explicitly flags this as "worth a DDL check to confirm" whether these are even real columns on this table (unlike `ACC_VOUCHER_DETAIL`, which does have them). Not included in the column list above pending that confirmation.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCDRAFTVCHDTL_ACCSUBCLASS` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |
| `FK_DRFTACCVCHDTL_VCRFORTYPID` | `LK_VOUCHER_FOR_TYPE_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_DRAFT_VOUCHER` 1:N `ACC_DRAFT_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. `ACC_TEMP_DRAFT_VOUCHER` rows are copied by `USER_ID` into this table on Save/Update. Account resolves via `ACC_SUB_CLASS_ID` into Chart of Accounts; cost center via `COST_CENTER_ID`. On Submit, rows are copied into `ACC_VOUCHER_DETAIL` (via `ACC_CONFIRM_INSERT`) and then deleted — no archive/history table for draft deletes (unlike the final voucher's `ACC_VOUCHER_DETAIL_HIST`).

## Feature

[features/draft-voucher.md](../features/draft-voucher.md), [features/chart-of-accounts.md](../features/chart-of-accounts.md)
