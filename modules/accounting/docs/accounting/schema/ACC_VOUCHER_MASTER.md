# Table: ACC_VOUCHER_MASTER

```yaml
---
id: tbl:ACC_VOUCHER_MASTER
module: accounting
status: inferred
model: ACC_VOUCHER_MASTER
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [CREATED_BY->SC_USER.SC_USER_ID, HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, HR_OFFICE_ID->HR_OFFICE.HR_OFFICE_ID, PAYMENT_MODE_ID->ACC_PAYMENT_MODE.PAYMENT_MODE_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, VOUCHER_TYPE_ID->ACC_VOUCHER_TYPE.VOUCHERTYPEID, LK_TRX_SRC_ID->LOOKUP_DATA.LOOKUP_DATA_ID, RF_ACTN_STATUS_ID->RF_ACTN_STATUS.RF_ACTN_STATUS_ID, ACC_GL_LINK_COA_H_ID->ACC_GL_LINK_COA_H.ACC_GL_LINK_COA_H_ID, LK_VOUCHER_SRC_TYPE_ID->LOOKUP_DATA.LOOKUP_DATA_ID, VOUCHER_MASTER_ID]
---
```

Header table for a finalized, posted-or-postable voucher (a debit/credit journal entry) — the "real" voucher table, as opposed to the parallel `ACC_DRAFT_VOUCHER` working-copy table. 1:N parent of `ACC_VOUCHER_DETAIL`.

**Status:** inferred from feature docs (`features/voucher.md`, `features/draft-voucher.md` and others) — column list reconstructed from the union of every insert/update/select column list referenced there, not from `ALL_TAB_COLUMNS`. No explicit C# types are stated in the source docs beyond `VOUCHER_MASTER_ID` (`Int64`/`NUMBER`, confirmed by a known-issue note about `int id` vs `Int64 VOUCHER_MASTER_ID`); other `*_ID`/date/amount columns below are typed by the identity/audit naming convention (see `_conventions.md`), not independently confirmed — flagged per row where relevant.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_MASTER_ID` | Int64 | PK, sequence-generated | features/voucher.md, features/draft-voucher.md |
| `POST_ID` | string | System-set voucher reference number; 10-digit numeric, no prefix (`GET_M_POST_ID_AUTO`) — contrast `ACC_DRAFT_VOUCHER.POST_ID`'s `D`+9-digit format | features/voucher.md |
| `POST_DATE` | DateTime (inferred) | Voucher/transaction date | features/voucher.md |
| `VOUCHER_NO` | string | Auto- or manually-numbered per `IS_VCH_NO_AUTO` | features/voucher.md |
| `VOUCHER_TYPE_ID` | Int64 (inferred) | FK → `ACC_VOUCHER_TYPE` | features/voucher.md |
| `DESCRIPTION` | string | Header narration | features/voucher.md |
| `EMPLOYEE_ID` | Int64 (inferred) | Holds the user id | features/voucher.md |
| `REF_ID` | string | Present, mostly unused on the Voucher screen; set by `StockClosingService.cs` for the stock-closing path, and copied from the draft's `POST_ID` on Submit | features/voucher.md, features/draft-voucher.md |
| `DIN` | string | Present, unused on this screen | features/voucher.md |
| `CHQ_NO` | string | Cheque/instrument number; global (not company-scoped) uniqueness check at save time | features/voucher.md |
| `CHQ_DATE` | DateTime (inferred) | Cheque/instrument date | features/voucher.md |
| `COMP_CODE` | string | Company scope, set server-side | features/voucher.md |
| `IS_POSTED` | string | `Y`=Posted / `N`=Un-posted (contrast draft's `W`/`C`); flipped in bulk by Voucher Post/Unpost | features/voucher.md, features/voucher-post-unpost.md |
| `PAYMENT_MODE_ID` | Int64 (inferred) | FK → `ACC_PAYMENT_MODE` | features/voucher.md, features/payment-mode.md |
| `VOUCHER_SRC_DESC` | string | Read-only source ref text | features/voucher.md |
| `ACNT_NAME` | string | Cash-voucher-only free-text payee/account name | features/voucher.md |
| `PAY_TYPE` | string | `A` (A/C Pay) / `C` (Cash) radio | features/voucher.md |
| `HR_COMPANY_ID` | Int64 (inferred) | FK → `HR_COMPANY` | features/voucher.md |
| `RF_ACTN_STATUS_ID` | Int64 (inferred) | FK → `RF_ACTN_STATUS`; workflow status (action type 77) | features/voucher.md, features/draft-voucher.md |
| `ACTN_STS_TRACKER` | string (inferred) | Workflow correlation id, feeds `ACC_VOUCHER_STS` history | features/voucher.md |
| `VCH_SRC` | string | Populated by the final-voucher insert procedure (unlike the draft insert, which never sets it) | features/voucher.md, features/draft-voucher.md |
| `ACC_GL_LINK_COA_H_ID` | Int64 (inferred) | GL linkage placeholder, hardcoded `1` from this screen (other modules hardcode other values, e.g. `12` from Cheque Issue) — write-only/effectively unused | features/voucher.md |
| `LK_TRX_SRC_ID` | Int64 (inferred) | Transaction-source lookup ("Trx Source" filter/column) | features/voucher.md |
| `LK_VOUCHER_SRC_TYPE_ID` | Int64 (inferred) | Accepted by insert but never supplied by the C# repository — always `NULL`; effectively unused | features/voucher.md |
| `GL_SOURCE_LINK` | string (inferred) | Tags vouchers created by other modules (Bills, Payroll, Export/Import Bill, Fund Request, Cash Bill Realize, Store Receive, Check Bill, Cheque Issue); used by delete | features/voucher.md |
| `GL_LINK_REF_NO` | string (inferred) | Written by ~15 other modules' own voucher-creation code with a real document number; never read back anywhere — pure write sink (unused) | features/voucher.md |
| `BANK_DATE` | DateTime (inferred) | Date the transaction cleared the bank statement; written only by Bank Reconciliation's per-row update, not on the entry form | features/voucher.md, features/bank-reconciliation.md |
| `IS_VCH_NO_AUTO` | string | System param controlling whether `VOUCHER_NO` is auto-generated | features/voucher.md |
| `LAST_UPDATE_DATE` | DateTime (inferred) | Audit; set to `SYSDATE` on update, write-only/effectively unused (no explicit UI read) | features/voucher.md |
| `CREATION_DATE` | DateTime (inferred) | Audit; write-only/effectively unused | features/voucher.md |

**Gap:** `CREATED_BY`/`LAST_UPDATED_BY` audit columns are not explicitly named for `ACC_VOUCHER_MASTER` in the source docs (only `ACC_DRAFT_VOUCHER` lists them explicitly); the list-screen's "Updated By" grid column and voucher-post-unpost.md's `UPDATED_BY` query field suggest an equivalent column exists, but its exact name isn't confirmed here — not included above to avoid inventing a name.

## Keys & Indexes

**Primary key:** `ACC_VOUCHER_MASTER_PK` on `VOUCHER_MASTER_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_ACC_VCHMASTER_01` | `POST_ID` |
| `UK_ACC_VCHMASTER_02` | `HR_COMPANY_ID`, `VOUCHER_TYPE_ID`, `VOUCHER_NO` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCVCH_CREATBY` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACCVCH_HRCOMPID` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_ACCVCH_HROFFICEID` | `HR_OFFICE_ID` | `HR_OFFICE.HR_OFFICE_ID` |
| `FK_ACCVCH_PAYMODE` | `PAYMENT_MODE_ID` | `ACC_PAYMENT_MODE.PAYMENT_MODE_ID` |
| `FK_ACCVCH_UPDTBY` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACCVCH_VCH_TYPID` | `VOUCHER_TYPE_ID` | `ACC_VOUCHER_TYPE.VOUCHERTYPEID` |
| `FK_LKDATATRXSRC_AVCRMSTR` | `LK_TRX_SRC_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |
| `FK_RFACTNSTS_VCRMSTER` | `RF_ACTN_STATUS_ID` | `RF_ACTN_STATUS.RF_ACTN_STATUS_ID` |
| `FK_VCHM_ACGLLNKCOAH` | `ACC_GL_LINK_COA_H_ID` | `ACC_GL_LINK_COA_H.ACC_GL_LINK_COA_H_ID` |
| `FK_VCRSCRTPID_AVM` | `LK_VOUCHER_SRC_TYPE_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `ACC_VOUCHER_MASTER_PK` | yes | `VOUCHER_MASTER_ID` |
| `IDX_POST_DT_VCHRMSTR` | no | `POST_DATE` |
| `UK_ACC_VCHMASTER_01` | yes | `POST_ID` |
| `UK_ACC_VCHMASTER_02` | yes | `HR_COMPANY_ID`, `VOUCHER_TYPE_ID`, `VOUCHER_NO` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_VOUCHER_MASTER` 1:N `ACC_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. Per-user scratch lines in `ACC_TEMP_VOUCHER_DETAIL` are copied by `USER_ID` into `ACC_VOUCHER_DETAIL` on Save/Update. `ACC_DRAFT_VOUCHER` is the source of a one-directional "Submit" conversion into `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL` via `ACC_CONFIRM_INSERT` (the new voucher's `REF_ID` is set from the draft's `POST_ID`). Deleting a voucher archives the master row into `ACC_VOUCHER_MASTER_HIST` before hard-deleting it. `VOUCHER_TYPE_ID` → `ACC_VOUCHER_TYPE`; `PAYMENT_MODE_ID` → `ACC_PAYMENT_MODE`; `HR_COMPANY_ID` → `HR_COMPANY`; `RF_ACTN_STATUS_ID` → `RF_ACTN_STATUS`, also driving `ACC_VOUCHER_STS` workflow history. `GL_SOURCE_LINK` is written directly (PL/SQL-layer, no C# caller) by other modules — Bills, Payroll, Export/Import Bill, Fund Request, Cash Bill Realize, Store Receive, Check Bill, Cheque Issue — and by Stock Closing's closing/opening voucher generation.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md), [features/checker-maker.md](../features/checker-maker.md), [features/bank-reconciliation.md](../features/bank-reconciliation.md), [features/voucher-post-unpost.md](../features/voucher-post-unpost.md), [features/stock-closing.md](../features/stock-closing.md), [features/payment-mode.md](../features/payment-mode.md), [features/cost-center-wise-ledger-summary.md](../features/cost-center-wise-ledger-summary.md), [features/ledger-wise-cost-center-summary.md](../features/ledger-wise-cost-center-summary.md)
