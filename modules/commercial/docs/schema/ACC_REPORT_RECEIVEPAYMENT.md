# Table: ACC_REPORT_RECEIVEPAYMENT

```yaml
---
id: tbl:ACC_REPORT_RECEIVEPAYMENT
module: accounting
status: db-verified
model: "n/a — shared staging table, not a real business entity"
package: PKG_ACCOUNTING
procedures: []
---
```

Shared staging table for the "Receive Payment" report (a Cash & Bank ledger movement summary,
despite the name). Not a real business entity — purely a scratch space one report writes into and
reads back from.

**Status:** `db-verified` — pulled directly from Oracle's own catalog on the dev instance.

## Finding: zero schema safeguards, confirms the known bugs

The docs site's Receive Payment page already documents: no filter at all on the read-back query, a
cleanup step that only clears one hardcoded user id, a hardcoded company constant, and no isolation
between concurrent runs (one shared physical table, not per-session).

**Verified: the schema itself has zero constraints of any kind.** No PK, no FK, no unique
constraint, no index — nothing. Currently holds **6,708 rows** and growing, which is exactly the
symptom you'd expect from "cleanup only clears one hardcoded user id" — the table just keeps
accumulating.

## Columns

`AC_CODE`, `MAIN_CODE`, `SUB_CODE`, `SUB_NAME`, `AMOUNT`, `USER_ID`, `COMP_CODE`, `GR_CODE`,
`SGR_CODE`, `MAP_NAME`, `MAP_CODE` — no PK column, no constraints of any kind.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:** none defined at the DB level.

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

None — no FK constraints exist on this table.

## Indexes

None exist. Given the table has no `WHERE`-clause filtering in the app today (per the docs site's
"no filter at all" finding), an index wouldn't help until that correctness bug is fixed first —
fixing the query to actually filter by user/company/date would be the prerequisite, and an index on
whatever filter columns result would be the natural follow-up.

## Feature

[Receive Payment](../../../Docs/data/accounting.js) — menu id `receive-payment`.
