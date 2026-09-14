# Table: ACC_COMPL_LEDGER_PCT_RULE

```yaml
---
id: tbl:ACC_COMPL_LEDGER_PCT_RULE
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_COMPL_LEDGER_PCT_RULE_ID]
---
```

Compliance-percentage rule table: one row per GL account, storing a compliance percentage used to compute a "compliance" debit/credit amount as a percentage of the real amount. Referenced by the not-yet-implemented Compliance Ledger Rules screen; no column list exists in source docs beyond what's below. Full insert/update/select/delete stored procedures exist for it, but are called by nothing anywhere in either repo — the one function meant to consume the rule exists only as commented-out, syntactically incomplete code.

## Columns

No columns are individually named in the source docs. The feature doc states the row shape only: one row per GL account, storing a compliance percentage — implying at minimum a GL-account FK column and a percentage column, but neither is named explicitly.

## Keys & Indexes

**Primary key:** `PK_ACC_COMPL_LEDGER_PCT_RULE` on `ACC_COMPL_LEDGER_PCT_RULE_ID`

**Foreign keys:** none defined at the DB level.

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_COMPL_LEDGER_PCT_RULE` | yes | `ACC_COMPL_LEDGER_PCT_RULE_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Conceptually tied to `ACC_VOUCHER` line tables' `CP_DR_AMT`/`CP_CR_AMT` columns (the "compliance" debit/credit amounts those columns are meant to hold, computed as a percentage of the real amount) and to a GL account in the Chart of Accounts — but this rule table is never actually read by the Voucher screen or by any report/procedure that populates those columns. Several GL/financial reports (trial balance, income statement, balance sheet, sub-ledger) have a live "compliance mode" toggle that reads `CP_DR_AMT`/`CP_CR_AMT` directly, independent of this rules table.

## Feature

[features/compliance-ledger-rules.md](../features/compliance-ledger-rules.md)
