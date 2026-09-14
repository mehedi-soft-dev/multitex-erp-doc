# Table: ACC_OPENING_BALANCE

```yaml
---
id: tbl:ACC_OPENING_BALANCE
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_FISCAL_YEAR_ID->ACC_FISCAL_YEAR.ACC_FISCAL_YEAR_ID, ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, CREATED_BY->SC_USER.SC_USER_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, ACC_OPENING_BALANCE_ID]
---
```

Holds the opening figures for the next fiscal year, snapshotted from the closing trial balance when a fiscal year is closed via the Fiscal Year Close screen ("Closing Process" button). No C# code references this table directly — it is populated entirely by the Oracle closing procedure, so only its relationship to `ACC_FISCAL_YEAR` is confirmed; individual balance/account columns could not be sourced from either repo.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_FISCAL_YEAR_ID` | — | FK → `ACC_FISCAL_YEAR`; the only real foreign key onto a fiscal year anywhere in the schema | feature doc |

No further columns are named in any source doc — the closing procedure that populates this table (the one actually wired up, of two divergent implementations) is not decomposed further in `fiscal-year.md` / `fiscal-year-close.md`, and no C# model or repository touches this table to reveal more.

## Keys & Indexes

**Primary key:** `PK_ACC_OPENING_BALANCE` on `ACC_OPENING_BALANCE_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCOB_ACCFY` | `ACC_FISCAL_YEAR_ID` | `ACC_FISCAL_YEAR.ACC_FISCAL_YEAR_ID` |
| `FK_ACCOB_ACCSUB_CLASS` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |
| `FK_ACCOB_COMP` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_ACCOB_CRTBY_USR` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACCOB_UPDBY_USR` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_OPENING_BALANCE` | yes | `ACC_OPENING_BALANCE_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Created by the Fiscal Year Close transaction: selecting a period from `ACC_FISCAL_YEAR` and running the Closing Process snapshots the closing trial balance into `ACC_OPENING_BALANCE` (next year's opening figures) and flips that fiscal year's `IS_CLOSED` flag to `Y`. No explicit `COMMIT` exists in the closing procedure — only a `ROLLBACK` on exception — so whether a "successful" close actually persists here depends on connection autocommit settings. Two divergent closing implementations exist; the one the app calls has no guard against existing opening balances or unposted vouchers before writing here.

## Feature

[features/fiscal-year.md](../features/fiscal-year.md), [features/fiscal-year-close.md](../features/fiscal-year-close.md)
