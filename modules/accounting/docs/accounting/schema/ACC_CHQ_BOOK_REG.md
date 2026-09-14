# Table: ACC_CHQ_BOOK_REG

```yaml
---
id: tbl:ACC_CHQ_BOOK_REG
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_BANK_ACCOUNT_ID->ACC_BANK_ACCOUNT.ACC_BANK_ACCOUNT_ID, CREATED_BY->SC_USER.SC_USER_ID, HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, ACC_CHQ_BOOK_REG_ID]
---
```

Header table for a Cheque Book Register (one row per physical cheque book issued against a bank account, book number + leaf range). Referenced by the not-yet-implemented Cheque Book Registers screen; no column list exists in source docs beyond the table's existence and role. The underlying Oracle package (`PKG_ACC_CHQ_BOOK_REG` in the sibling `MultitechERP` repo) is dated May 2025 and appears fully built at the database layer, but no .NET controller or Angular screen consumes it anywhere, in either repo.

## Columns

No columns are named in the source docs. The feature docs describe the concept only: book number and leaf range tracked at the header level, with one `ACC_CHQ_BOOK_REG_LEAF` row auto-generated per cheque number in that range.

## Keys & Indexes

**Primary key:** `PK_ACC_CHQ_BOOK_REG` on `ACC_CHQ_BOOK_REG_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCCHQBKREG_BANKBRNCH` | `ACC_BANK_ACCOUNT_ID` | `ACC_BANK_ACCOUNT.ACC_BANK_ACCOUNT_ID` |
| `FK_ACCCHQBKREG_CRTBY` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACCCHQBKREG_HRCOMPID` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_ACCCHQBKREG_UPDBY` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_CHQ_BOOK_REG` | yes | `ACC_CHQ_BOOK_REG_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Header of a header/leaf pair with `ACC_CHQ_BOOK_REG_LEAF` (one register header to many leaf rows, auto-generated over the registered cheque-number range). Feeds the (also unimplemented) Cheque Issue and Cheque Cancellation flows — `cheque-cancellation.md` notes a cancelled leaf links to a replacement leaf, implying the relationship lives on `ACC_CHQ_BOOK_REG_LEAF` rather than this header table.

## Feature

[features/cheque-book-registers.md](../features/cheque-book-registers.md), [features/cheque-cancellation.md](../features/cheque-cancellation.md)
