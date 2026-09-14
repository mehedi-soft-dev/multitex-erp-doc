# Table: RF_ACTN_STATUS

```yaml
---
id: tbl:RF_ACTN_STATUS
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [RF_ACTN_TYPE_ID->RF_ACTN_TYPE.RF_ACTN_TYPE_ID, CREATED_BY->SC_USER.SC_USER_ID, HR_DEPARTMENT_ID->HR_DEPARTMENT.HR_DEPARTMENT_ID, PARENT_ID->RF_ACTN_STATUS.RF_ACTN_STATUS_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, RF_ACTN_STATUS_ID]
---
```

Shared reference lookup of workflow action statuses (e.g. Create Draft, Submit, Management Approve, Audit Approve), used across action type 77 "Accounting Workflow". Only ever referenced as an FK target in the source docs — no dedicated column list or Add/Edit screen was ever documented for it.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `RF_ACTN_STATUS_ID` | — | PK, referenced as FK from `ACC_VOUCHER_MASTER.RF_ACTN_STATUS_ID` and `ACC_DRAFT_VOUCHER.RF_ACTN_STATUS_ID`. Known values include `336` (Submit), `337`/`338` (Management/Audit Approve), per `voucher.md` Known Issues | voucher.md, draft-voucher.md |

No other columns are named anywhere in the source docs.

## Keys & Indexes

**Primary key:** `PK_RF_ACTN_STATUS` on `RF_ACTN_STATUS_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_RF_ACTN_STATUS` | `RF_ACTN_TYPE_ID`, `ACTN_STATUS_NAME` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACTYPE_ACSTS` | `RF_ACTN_TYPE_ID` | `RF_ACTN_TYPE.RF_ACTN_TYPE_ID` |
| `FK_CRTUSER_ACSTS` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_DEPT_ACTNSTS` | `HR_DEPARTMENT_ID` | `HR_DEPARTMENT.HR_DEPARTMENT_ID` |
| `FK_PACTNSTS_ACTNSTS` | `PARENT_ID` | `RF_ACTN_STATUS.RF_ACTN_STATUS_ID` |
| `FK_UPDUSER_ACSTS` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `INDX_PURCREQD_ACTION_SORT` | no | `ACTION_SORT` |
| `INDX_PURCREQD_RFACTNTYPEID` | no | `RF_ACTN_TYPE_ID` |
| `PK_RF_ACTN_STATUS` | yes | `RF_ACTN_STATUS_ID` |
| `UK_RF_ACTN_STATUS` | yes | `RF_ACTN_TYPE_ID`, `ACTN_STATUS_NAME` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Referenced from `ACC_VOUCHER_MASTER.RF_ACTN_STATUS_ID` and `ACC_DRAFT_VOUCHER.RF_ACTN_STATUS_ID`, paired with `ACTN_STS_TRACKER` on each. Drives the "Action Status" dropdown on both the Voucher and Draft Voucher entry screens (workflow action type 77) and the color-coded status badge on the Voucher list grid. Draft Voucher additionally treats picking "Submit Draft Voucher" as a trigger for the Submit conversion flow (`ACC_CONFIRM_INSERT`) rather than a plain save. Status transitions are recorded as history in `ACC_VOUCHER_STS`.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md)
