# Table: ACC_VOUCHER_DETAIL_HIST

```yaml
---
id: tbl:ACC_VOUCHER_DETAIL_HIST
module: accounting
status: inferred
package: PKG_ACCOUNTING
---
```

Archive table for deleted final-voucher detail lines. `ACC_VOUCHER_MASTER_DELETE` copies detail rows here before hard-deleting them from `ACC_VOUCHER_DETAIL`. Has zero read-side references anywhere in the codebase (same as `ACC_VOUCHER_MASTER_HIST`) — write-only, no viewer built.

**Status:** inferred, and thin — no source doc quotes this table's full column list.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_DETAIL_ID` | Int64 (inferred) | Presumed PK, mirrors `ACC_VOUCHER_DETAIL.VOUCHER_DETAIL_ID` | features/voucher.md (inferred — archive of the detail row) |
| `VOUCHER_MASTER_ID` | Int64 (inferred) | Presumed FK, mirrors `ACC_VOUCHER_DETAIL.VOUCHER_MASTER_ID`, linking back to the archived `ACC_VOUCHER_MASTER_HIST` row | features/voucher.md (inferred) |

**Not independently confirmed column-by-column:** the remaining columns of `ACC_VOUCHER_DETAIL` (`AC_CODE`, `MAIN_CODE`, `ACC_SUB_CLASS_ID`, `DR_AMT`, `CR_AMT`, etc. — see `ACC_VOUCHER_DETAIL.md`) are presumed to be mirrored here since this is an archive-before-delete copy of those rows, but no source doc quotes this table's own insert/select column list — structural inference only, not verified. Unlike `ACC_VOUCHER_MASTER_HIST`, no `DELETE_BY`/`DELETE_DATE`-equivalent columns are mentioned for this table in the source docs either.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:** none defined at the DB level.

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Populated by `ACC_VOUCHER_MASTER_DELETE` (`PKG_ACCOUNTING.sql:4359-4445`) as an archive-before-hard-delete step for `ACC_VOUCHER_DETAIL`, paired with the master archive in `ACC_VOUCHER_MASTER_HIST` via (presumed) `VOUCHER_MASTER_ID`. No known FK/join target reads from this table.

## Feature

[features/voucher.md](../features/voucher.md), [features/voucher-delete-history.md](../features/voucher-delete-history.md)
