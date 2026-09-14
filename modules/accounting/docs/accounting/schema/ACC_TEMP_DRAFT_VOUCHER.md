# Table: ACC_TEMP_DRAFT_VOUCHER

```yaml
---
id: tbl:ACC_TEMP_DRAFT_VOUCHER
module: accounting
status: inferred
model: ACC_TEMP_VOUCHER_DETAIL
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID]
---
```

Per-user scratch/staging table for the Draft Voucher line-entry grid — holds in-progress lines (keyed by `USER_ID`) before they are committed into `ACC_DRAFT_VOUCHER_DETAIL` on Save/Update. Note: bound to the shared `ACC_TEMP_VOUCHER_DETAIL` C# model class, persisted here for drafts (vs. `ACC_TEMP_VOUCHER_DETAIL` table for final vouchers).

**Status:** inferred from feature docs; no `ALL_TAB_COLUMNS` dump.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `TEMP_ID` | Int64 (inferred) | PK | features/draft-voucher.md |
| `COMP_CODE` | string | Company scope; the select procedure's `pCOMP_CODE` param is accepted but never filtered on (Known Issue) | features/draft-voucher.md |
| `AC_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md |
| `MAIN_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md |
| `ACC_SUB_CLASS_ID` | Int64 (inferred) | FK → `ACC_SUB_CLASS` | features/draft-voucher.md |
| `SUB_CODE` | string | Chart-of-Accounts code segment | features/draft-voucher.md |
| `SUB_NAME` | string | Account display name | features/draft-voucher.md |
| `DR_AMT` | decimal (inferred) | Debit amount | features/draft-voucher.md |
| `CR_AMT` | decimal (inferred) | Credit amount | features/draft-voucher.md |
| `DESCRIPTION` | string | Per-line narration | features/draft-voucher.md |
| `XSTATUS` | ? | Type not stated | features/draft-voucher.md |
| `MAP_CODE` | string | Unused/write-only — only populated when re-opening a submitted draft (from `M_CODE`, always `'000'`); never shown/acted on | features/draft-voucher.md |
| `USER_ID` | string (inferred, mixed-type) | Keys the per-user staging rows; written via a `VARCHAR2` parameter but read via `NUMBER` parameters elsewhere — a latent type-mismatch (flagged as a Known Issue) | features/draft-voucher.md |
| `COST_CENTER_ID` | Int64 (inferred) | FK → Cost Center | features/draft-voucher.md |
| `CURRENCY_ID` | Int64 (inferred) | FK → currency | features/draft-voucher.md |
| `EXCHANGE_RATE` | decimal (inferred) | | features/draft-voucher.md |
| `LK_VOUCHER_FOR_TYPE_ID` | Int64 (inferred) | "Voucher For" type lookup | features/draft-voucher.md |
| `VOUCHER_FOR_ID` | Int64 (inferred) | Secondary-party reference id | features/draft-voucher.md |
| `BILL_NO` | string | | features/draft-voucher.md |

**Gap / unconfirmed:** `BILL_REF_ID`/`BILL_DETAIL_ID` are set client-side but never sent to/used by the server for this table — source doc flags it's unclear whether these are even real columns here (see `ACC_DRAFT_VOUCHER_DETAIL.md`). Not included above.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACC_TMP_DFT_VCHDTL` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Per-user scratch lines for the Draft Voucher entry grid, scoped by `USER_ID`; copied into `ACC_DRAFT_VOUCHER_DETAIL` (child of `ACC_DRAFT_VOUCHER` via `VOUCHER_MASTER_ID`) on Save/Update. Structurally mirrors the final-voucher equivalent, `ACC_TEMP_VOUCHER_DETAIL`. Account resolves via `ACC_SUB_CLASS_ID` into Chart of Accounts; cost center via `COST_CENTER_ID`.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md)
