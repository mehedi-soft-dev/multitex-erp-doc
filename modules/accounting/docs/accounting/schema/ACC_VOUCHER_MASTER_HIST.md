# Table: ACC_VOUCHER_MASTER_HIST

```yaml
---
id: tbl:ACC_VOUCHER_MASTER_HIST
module: accounting
status: inferred
package: PKG_ACCOUNTING
---
```

Archive table for deleted final vouchers. `ACC_VOUCHER_MASTER_DELETE` copies the master row here before hard-deleting it from `ACC_VOUCHER_MASTER`. Has zero read-side references anywhere in the codebase — nothing selects from it, no API exposes it, no Angular screen displays it (the "Voucher Delete History" feature is not implemented; only the write-side archive exists).

**Status:** inferred, and unusually thin — the source docs do not enumerate this table's full column list (no INSERT statement's full column list is quoted), only that it receives an archived copy of `ACC_VOUCHER_MASTER` plus two delete-audit columns.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_MASTER_ID` | Int64 (inferred) | Presumed PK, mirrors `ACC_VOUCHER_MASTER.VOUCHER_MASTER_ID` | features/voucher.md (inferred — archive of the master row) |
| `DELETE_BY` | Int64 (inferred) | Intended to record who deleted the voucher; the `UPDATE ACC_VOUCHER_MASTER_HIST SET DELETE_BY=..., DELETE_DATE=...` statement is commented out in `PKG_ACCOUNTING.sql`, so this column is always null/blank in practice despite the history-list query expecting it populated via a join | features/voucher.md |
| `DELETE_DATE` | DateTime (inferred) | Same as `DELETE_BY` — intended but never actually set (commented-out statement) | features/voucher.md |

**Not independently confirmed column-by-column:** the remaining columns of `ACC_VOUCHER_MASTER` (`POST_ID`, `POST_DATE`, `VOUCHER_NO`, `VOUCHER_TYPE_ID`, `DESCRIPTION`, etc. — see `ACC_VOUCHER_MASTER.md`) are presumed to be mirrored here since this is an archive-before-delete copy of that row, but no source doc quotes this table's own insert/select column list, so this is a structural inference, not a confirmed fact — do not treat it as verified.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:** none defined at the DB level.

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Populated by `ACC_VOUCHER_MASTER_DELETE` (`PKG_ACCOUNTING.sql:4359-4445`) as an archive-before-hard-delete step for `ACC_VOUCHER_MASTER`. Paired with `ACC_VOUCHER_DETAIL_HIST` for the corresponding detail-line archive. No known FK/join target reads from this table.

## Feature

[features/voucher.md](../features/voucher.md), [features/voucher-delete-history.md](../features/voucher-delete-history.md)
