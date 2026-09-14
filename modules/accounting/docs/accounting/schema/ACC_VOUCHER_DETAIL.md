# Table: ACC_VOUCHER_DETAIL

```yaml
---
id: tbl:ACC_VOUCHER_DETAIL
module: accounting
status: inferred
model: ACC_VOUCHER_DETAIL
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, PARENT_ID->ACC_VOUCHER_DETAIL.VOUCHER_DETAIL_ID, LK_VOUCHER_FOR_TYPE_ID->LOOKUP_DATA.LOOKUP_DATA_ID, COST_CENTER_ID->ACC_COST_CENTER.COST_CENTER_ID, VOUCHER_MASTER_ID->ACC_VOUCHER_MASTER.VOUCHER_MASTER_ID, VOUCHER_DETAIL_ID]
---
```

Line/detail table for a finalized voucher — one debit or credit row per GL account touched. Child of `ACC_VOUCHER_MASTER`.

**Status:** inferred from feature docs; no `ALL_TAB_COLUMNS` dump. No explicit C# types stated in source docs; `*_ID`/date/amount columns typed by naming convention only (not independently confirmed).

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_DETAIL_ID` | Int64 (inferred) | PK | features/voucher.md, features/draft-voucher.md |
| `VOUCHER_MASTER_ID` | Int64 (inferred) | FK → `ACC_VOUCHER_MASTER` | features/voucher.md |
| `COMP_CODE` | string | Company scope | features/voucher.md |
| `AC_CODE` | string | Chart-of-Accounts code segment | features/voucher.md, features/chart-of-accounts.md |
| `MAIN_CODE` | string | Chart-of-Accounts code segment | features/voucher.md, features/chart-of-accounts.md |
| `ACC_SUB_CLASS_ID` | Int64 (inferred) | FK → `ACC_SUB_CLASS` (Chart of Accounts) | features/voucher.md, features/chart-of-accounts.md |
| `SUB_CODE` | string | Chart-of-Accounts code segment | features/voucher.md, features/chart-of-accounts.md |
| `DR_AMT` | decimal (inferred) | Debit amount | features/voucher.md |
| `CR_AMT` | decimal (inferred) | Credit amount | features/voucher.md |
| `COST_CENTER_ID` | Int64 (inferred) | FK → Cost Center; sentinel `1` = "N/A" | features/voucher.md |
| `DESCRIPTION` | string | Per-line narration | features/voucher.md |
| `M_CODE` | string | Always hardcoded `'000'` on write; read back as `MAP_CODE` on `ACC_TEMP_VOUCHER_DETAIL` — real usage, not flagged as dead | features/voucher.md |
| `XSTATUS` | ? | Grid sort order; type not stated | features/voucher.md |
| `CURRENCY_ID` | Int64 (inferred) | FK → currency; default `1` | features/voucher.md |
| `EXCHANGE_RATE` | decimal (inferred) | Read-only for local currency | features/voucher.md |
| `LK_VOUCHER_FOR_TYPE_ID` | Int64 (inferred) | Lookup: "Voucher For" type (Buyer/Supplier/Employee/Bank) | features/voucher.md |
| `VOUCHER_FOR_ID` | Int64 (inferred) | Secondary-party reference id | features/voucher.md |
| `BILL_NO` | string | Bill sub-flow (Bill-type vouchers only) | features/voucher.md |
| `BILL_REF_ID` | Int64 (inferred) | Bill sub-flow | features/voucher.md |
| `BILL_DETAIL_ID` | Int64 (inferred) | Bill sub-flow; backfilled by Checker Maker's "Update BILL" repair | features/voucher.md, features/checker-maker.md |
| `BILL_KEY` | string (inferred) | Derived key rebuilt by Checker Maker's "Update BILL" repair; read only by Duplicate Bill Payment Report and that repair job's own follow-up query — thin/rarely-used | features/voucher.md, features/checker-maker.md |
| `PARENT_ID` | Int64 (inferred) | Real usage but PL/SQL-only — no C# model property or repository reference; used for `HAS_CHILD` computation, last-bill-payment-date maintenance, and reports | features/voucher.md |
| `CP_DR_AMT` | decimal (inferred) | "Compliance" debit amount; copied through by the insert procedure but never set by the C# repository — write-only/unreachable from the UI | features/voucher.md, features/compliance-vouchers.md |
| `CP_CR_AMT` | decimal (inferred) | "Compliance" credit amount; same as `CP_DR_AMT` | features/voucher.md, features/compliance-vouchers.md |

## Keys & Indexes

**Primary key:** `ACC_VOUCHER_DETAIL_PK` on `VOUCHER_DETAIL_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCVCHDTL_ACCSUBCLASS` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |
| `FK_ACCVCHDTL_PARENTID` | `PARENT_ID` | `ACC_VOUCHER_DETAIL.VOUCHER_DETAIL_ID` |
| `FK_ACCVCHDTL_VCRFORTYPID` | `LK_VOUCHER_FOR_TYPE_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |
| `FK_COST_CENTER` | `COST_CENTER_ID` | `ACC_COST_CENTER.COST_CENTER_ID` |
| `FK_VCHR_MASTER` | `VOUCHER_MASTER_ID` | `ACC_VOUCHER_MASTER.VOUCHER_MASTER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `ACC_VOUCHER_DETAIL_PK` | yes | `VOUCHER_DETAIL_ID` |
| `IDX_ACCSUBCLS_ACC_VCHR_DTL` | no | `ACC_SUB_CLASS_ID` |
| `IDX_BILL_NO` | no | `BILL_NO` |
| `IDX_VCHFORTYP_VCHRFOR_ACC_VCHRDTL` | no | `LK_VOUCHER_FOR_TYPE_ID`, `VOUCHER_FOR_ID` |
| `IDX_VCHRMSTR_VCHR_DTL` | no | `VOUCHER_MASTER_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_VOUCHER_MASTER` 1:N `ACC_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. Each line's account resolves via `ACC_SUB_CLASS_ID` (and code parts `AC_CODE`/`MAIN_CODE`/`SUB_CODE`) into Chart of Accounts (`ACC_SUB_CLASS`), and its cost center via `COST_CENTER_ID`. `ACC_TEMP_VOUCHER_DETAIL` rows are copied by `USER_ID` into this table on Save/Update. Deleting the parent voucher archives detail rows into `ACC_VOUCHER_DETAIL_HIST` before hard-deleting. `ACC_DRAFT_VOUCHER_DETAIL` is the equivalent table for draft (unsubmitted) vouchers, with the same column shape minus the Bill sub-flow (`BILL_REF_ID`, `BILL_DETAIL_ID`) and compliance columns (`CP_DR_AMT`/`CP_CR_AMT`).

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md), [features/checker-maker.md](../features/checker-maker.md), [features/bank-reconciliation.md](../features/bank-reconciliation.md), [features/stock-closing.md](../features/stock-closing.md), [features/chart-of-accounts.md](../features/chart-of-accounts.md), [features/receive-payment.md](../features/receive-payment.md), [features/cost-center-wise-ledger-summary.md](../features/cost-center-wise-ledger-summary.md), [features/ledger-wise-cost-center-summary.md](../features/ledger-wise-cost-center-summary.md)
