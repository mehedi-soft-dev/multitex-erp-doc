# Table: ACC_VOUCHER_TYPE

```yaml
---
id: tbl:ACC_VOUCHER_TYPE
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [VOUCHERTYPEID]
---
```

Lookup table of voucher types (e.g. cash/bank/journal voucher categories). Only ever referenced as an FK target in the source docs — no dedicated column list or Add/Edit screen was ever documented for it.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `VOUCHER_TYPE_ID` | — | PK, referenced as FK from `ACC_VOUCHER_MASTER.VOUCHER_TYPE_ID` and `ACC_DRAFT_VOUCHER.VOUCHER_TYPE_ID` | voucher.md, draft-voucher.md |

No other columns are named anywhere in the source docs. `voucher.md` and `draft-voucher.md` note that this table drives the Voucher Type dropdown, the visibility of Payment Mode/Cheque/Pay Type fields on the entry screen, and supplies the voucher-number prefix used by auto-numbering — but the columns backing those behaviors (e.g. a name/description column, a prefix column) are never explicitly named.

## Keys & Indexes

**Primary key:** `PK_VOUCHER_TYPE` on `VOUCHERTYPEID`

**Foreign keys:** none defined at the DB level.

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_VOUCHER_TYPE` | yes | `VOUCHERTYPEID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Parent of `ACC_VOUCHER_MASTER` (final vouchers) and `ACC_DRAFT_VOUCHER` (draft vouchers) via `VOUCHER_TYPE_ID`. Selecting a Voucher Type on the entry screen drives which optional fields (Payment Mode, Cheque No/Date, Pay Type) are shown and controls auto-generated voucher-number prefixing.

## Feature

[features/voucher.md](../features/voucher.md), [features/draft-voucher.md](../features/draft-voucher.md)
