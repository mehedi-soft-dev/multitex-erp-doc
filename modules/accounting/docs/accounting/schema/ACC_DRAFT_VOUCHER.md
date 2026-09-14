# Table: ACC_DRAFT_VOUCHER

```yaml
---
id: tbl:ACC_DRAFT_VOUCHER
module: accounting
status: inferred
model: ACC_VOUCHER_MASTER
package: PKG_ACCOUNTING
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, HR_OFFICE_ID->HR_OFFICE.HR_OFFICE_ID, ACC_GL_LINK_COA_H_ID->ACC_GL_LINK_COA_H.ACC_GL_LINK_COA_H_ID, LK_TRX_SRC_ID->LOOKUP_DATA.LOOKUP_DATA_ID, RF_ACTN_STATUS_ID->RF_ACTN_STATUS.RF_ACTN_STATUS_ID]
---
```

Header table for a Draft Voucher — a "working copy" of a voucher that can be saved/edited before becoming a real, numbered voucher. Same master+detail double-entry shape as `ACC_VOUCHER_MASTER` but lives in its own parallel table so it never touches the real ledger until Submit. Note: the C# model bound to this table is the shared `ACC_VOUCHER_MASTER` model class (mapped from `ACC_DRAFT_VOUCHER` columns), not a distinct `ACC_DRAFT_VOUCHER` model class.

**Status:** inferred from feature docs; no `ALL_TAB_COLUMNS` dump.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_MASTER_ID` | Int64 | PK, from `acc_draft_voucher_seq` | features/draft-voucher.md |
| `POST_ID` | string | Draft's own reference id, format `D` + 9-digit sequence (`GET_DRFT_VCH_NO_AUTO`); copied into the final voucher's `REF_ID` on Submit | features/draft-voucher.md |
| `POST_DATE` | DateTime (inferred) | Transaction date | features/draft-voucher.md |
| `VOUCHER_NO` | string | Auto- or manually-numbered per `IS_VCH_NO_AUTO` | features/draft-voucher.md |
| `VOUCHER_TYPE_ID` | Int64 (inferred) | FK → `ACC_VOUCHER_TYPE` | features/draft-voucher.md |
| `DESCRIPTION` | string | Header narration | features/draft-voucher.md |
| `EMPLOYEE_ID` | Int64 (inferred) | Holds the user id; doubles as created-by/updated-by | features/draft-voucher.md |
| `REF_ID` | string | Present on the model, mostly unused on this screen | features/draft-voucher.md |
| `DIN` | string | Threaded through every layer but never referenced by any view/JS file — unused/write-only | features/draft-voucher.md |
| `CHQ_NO` | string | Cheque/instrument number | features/draft-voucher.md |
| `CHQ_DATE` | DateTime (inferred) | Cheque/instrument date | features/draft-voucher.md |
| `COMP_CODE` | string | Company scope, set server-side | features/draft-voucher.md |
| `IS_POSTED` | string | `W`=Working/draft, `C`=Cancelled; reset to `W` if `ACC_CONFIRM_INSERT` (Submit) fails | features/draft-voucher.md |
| `PAYMENT_MODE_ID` | Int64 (inferred) | FK → `ACC_PAYMENT_MODE` | features/draft-voucher.md |
| `VOUCHER_SRC_DESC` | string | Auto-populated from user's office type; used in auto voucher-number generation | features/draft-voucher.md |
| `ACNT_NAME` | string | Cash-voucher-only free-text account name | features/draft-voucher.md |
| `PAY_TYPE` | string | `A`/`C` radio, cash-type only | features/draft-voucher.md |
| `HR_COMPANY_ID` | Int64 (inferred) | FK → `HR_COMPANY` | features/draft-voucher.md |
| `RF_ACTN_STATUS_ID` | Int64 (inferred) | FK → `RF_ACTN_STATUS`; workflow status (action type 77) | features/draft-voucher.md |
| `ACTN_STS_TRACKER` | string (inferred) | Workflow correlation id | features/draft-voucher.md |
| `VCH_SRC` | string | Present on model, read on this screen, but never set by `ACC_DRAFT_VOUCHER_INSERT` — write-only/effectively unused (default `'OWN'` is client-side only, never persisted) | features/draft-voucher.md |
| `ACC_GL_LINK_COA_H_ID` | Int64 (inferred) | GL linkage placeholder, hardcoded `1`; rarely used from this screen | features/draft-voucher.md |
| `LK_TRX_SRC_ID` | Int64 (inferred) | Transaction-source lookup | features/draft-voucher.md |
| `GL_SOURCE_LINK` | string (inferred) | Links back to the external module that generated the voucher; rarely used from this screen, populated via `ACC_DRAFT_VCH_SAVE4MISC_SRC` (export-bill/bank-realization flows) | features/draft-voucher.md |
| `GL_LINK_REF_NO` | string (inferred) | Rarely used from this screen | features/draft-voucher.md |
| `IS_VCH_NO_AUTO` | string | System param | features/draft-voucher.md |
| `CREATED_BY` | Int64 (inferred) | Audit; joined for "Prepared By" on the paging query — active use | features/draft-voucher.md |
| `LAST_UPDATED_BY` | Int64 (inferred) | Audit; set on update but never joined by the draft paging query — write-only | features/draft-voucher.md |
| `LAST_UPDATE_DATE` | DateTime (inferred) | Audit; write-only | features/draft-voucher.md |
| `CREATION_DATE` | DateTime (inferred) | Audit; set on insert, never mapped back — write-only | features/draft-voucher.md |
| `HR_OFFICE_ID` | ? | Low confidence — only appears in a fully commented-out dead-code block; flagged in source docs for manual DB-side confirmation that it's even a real column | features/draft-voucher.md |

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `POST_ID_UQ` | `POST_ID` |
| `UK_ACC_DRFT_VCH01` | `HR_COMPANY_ID`, `VOUCHER_TYPE_ID`, `VOUCHER_NO` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_DRFTVCH_HRCOMPID` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_DRFTVCH_HROFFICEID` | `HR_OFFICE_ID` | `HR_OFFICE.HR_OFFICE_ID` |
| `FK_DRFT_VCHM_ACGLLNKCOAH` | `ACC_GL_LINK_COA_H_ID` | `ACC_GL_LINK_COA_H.ACC_GL_LINK_COA_H_ID` |
| `FK_LKDATATRXSRC_ADV` | `LK_TRX_SRC_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |
| `FK_RFACTNSTS_DRFTVCR` | `RF_ACTN_STATUS_ID` | `RF_ACTN_STATUS.RF_ACTN_STATUS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `POST_ID_UQ` | yes | `POST_ID` |
| `UK_ACC_DRFT_VCH01` | yes | `HR_COMPANY_ID`, `VOUCHER_TYPE_ID`, `VOUCHER_NO` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_DRAFT_VOUCHER` 1:N `ACC_DRAFT_VOUCHER_DETAIL` via `VOUCHER_MASTER_ID`. `ACC_TEMP_DRAFT_VOUCHER` holds per-user scratch lines copied by `USER_ID` into `ACC_DRAFT_VOUCHER_DETAIL` on Save/Update. On Submit, the draft master+lines are copied into `ACC_VOUCHER_MASTER`/`ACC_VOUCHER_DETAIL` via `ACC_CONFIRM_INSERT` and then hard-deleted from the draft tables (one-directional; no "un-submit"). `VOUCHER_TYPE_ID` → `ACC_VOUCHER_TYPE`; `PAYMENT_MODE_ID` → `ACC_PAYMENT_MODE`; `RF_ACTN_STATUS_ID` → `RF_ACTN_STATUS`, also driving `ACC_VOUCHER_STS` workflow history.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md)
