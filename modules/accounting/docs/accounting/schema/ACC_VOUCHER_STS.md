# Table: ACC_VOUCHER_STS

```yaml
---
id: tbl:ACC_VOUCHER_STS
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACTION_BY->SC_USER.SC_USER_ID, RF_ACTN_STATUS_ID->RF_ACTN_STATUS.RF_ACTN_STATUS_ID, CREATED_BY->SC_USER.SC_USER_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, ACC_VOUCHER_STS_ID]
---
```

Workflow status history table for vouchers — records the approval-workflow state transitions (tied to `RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER` on `ACC_VOUCHER_MASTER`). Only ever referenced as a workflow-history side-effect table in the source docs — no dedicated column list or Add/Edit screen was ever documented for it.

## Columns

No columns are explicitly named anywhere in the source docs. `voucher.md` states that `ACC_VOUCHER_MASTER.RF_ACTN_STATUS_ID` / `ACTN_STS_TRACKER` "also feeds `ACC_VOUCHER_STS` history", implying it carries at least a voucher reference and a status/tracker value per history row, but no specific column names are given.

## Keys & Indexes

**Primary key:** `PK_ACC_VOUCHER_STS` on `ACC_VOUCHER_STS_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACTEMP_ACCVOUCHERSTS` | `ACTION_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACTNSTS_ACCVOUCHERSTS` | `RF_ACTN_STATUS_ID` | `RF_ACTN_STATUS.RF_ACTN_STATUS_ID` |
| `FK_CRTUSER_ACCVOUCHERSTS` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_UPDUSER_ACCVOUCHERSTS` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_VOUCHER_STS` | yes | `ACC_VOUCHER_STS_ID` |
| `UK_ACC_VOUCHER_STS` | yes | `ACC_VOUCHER_STS_ID`, `RF_ACTN_STATUS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Populated as a side effect of workflow actions on `ACC_VOUCHER_MASTER`: when a voucher's `RF_ACTN_STATUS_ID` changes (Submit / Management Approve / Audit Approve), a corresponding history row is written here. The Bulk Post/Unpost screen (`voucher-post-unpost.md`) also mutates this table directly — toggling a voucher's `IS_POSTED` flag, and if a workflow tracker exists, deletes Management/Audit-approve rows and forces the status back to "Submit" in `ACC_VOUCHER_STS`.

**Known issue:** Bulk-Post hardcodes the resulting workflow status to `RF_ACTN_STATUS_ID=336` (Submit) regardless of prior history, even if the voucher had already progressed further (337/338) — a voucher's status can silently regress (per `voucher.md` Known Issues, `PKG_ACCOUNTING.sql:4262-4265`).

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md), [features/voucher-post-unpost.md](../features/voucher-post-unpost.md)
