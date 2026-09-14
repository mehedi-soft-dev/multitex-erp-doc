# Table: ACC_CHQ_BOOK_REG_LEAF

```yaml
---
id: tbl:ACC_CHQ_BOOK_REG_LEAF
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_CHQ_BOOK_REG_ID->ACC_CHQ_BOOK_REG.ACC_CHQ_BOOK_REG_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, ACC_CHQ_BOOK_REG_LEAF_ID]
---
```

Leaf/detail table for a Cheque Book Register — one row auto-generated per individual cheque number within a register's leaf range, tracking used/available/cancelled status. Referenced by the not-yet-implemented Cheque Book Registers screen; no column list exists in source docs beyond what's below.

## Columns

No columns are named in the source docs. The feature docs describe the concept only: leaf-level used/available/cancelled status, and (per `cheque-cancellation.md`) a cancelled leaf links to a replacement leaf — implying at least a status column and a self-referencing "replacement leaf" FK, but neither is named explicitly anywhere.

## Keys & Indexes

**Primary key:** `PK_ACC_CHQ_BOOK_REG_LEAF` on `ACC_CHQ_BOOK_REG_LEAF_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_ACC_CHQ_BOOK_REG_LEAF` | `ACC_CHQ_BOOK_REG_ID`, `CHEQUE_NO` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCHQBKREGLF_ACCHQBKREG` | `ACC_CHQ_BOOK_REG_ID` | `ACC_CHQ_BOOK_REG.ACC_CHQ_BOOK_REG_ID` |
| `FK_ACCHQBKREGLF_UPDBY` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_CHQ_BOOK_REG_LEAF` | yes | `ACC_CHQ_BOOK_REG_LEAF_ID` |
| `UK_ACC_CHQ_BOOK_REG_LEAF` | yes | `ACC_CHQ_BOOK_REG_ID`, `CHEQUE_NO` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Detail/leaf child of `ACC_CHQ_BOOK_REG` (one register header to many leaf rows). Intended to feed the (also unimplemented) Cheque Issue package and the Cheque Cancellation flow, where a cancelled leaf links to its replacement leaf — likely a self-referencing FK on this table, per `cheque-cancellation.md`, though the actual column is not named in source docs.

## Feature

[features/cheque-book-registers.md](../features/cheque-book-registers.md)
