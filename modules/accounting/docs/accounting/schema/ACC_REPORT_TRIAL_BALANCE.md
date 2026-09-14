# Table: ACC_REPORT_TRIAL_BALANCE

```yaml
---
id: tbl:ACC_REPORT_TRIAL_BALANCE
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID]
---
```

Shared staging table for the trial-balance report, filtered only by user id — populated by a report call and then read back to render the trial balance grid on the Fiscal Year Close screen (and, per `accounting-reports.md`, the standalone Trial Balance report under Accounting Reports). Not a master table; no dedicated column list exists in source docs, only its role and a known copy/paste bug around it.

## Columns

No columns are named in the source docs beyond the implicit user-id scoping column (`fiscal-year-close.md`: "filtered only by user ID — no date-range or company filter of its own"). No date-range, company, or trial-balance-figure columns are named explicitly, though they must exist for the table to serve its purpose.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_ACC_RRT_TRIAL_BAL_01` | `USER_ID`, `ACC_SUB_CLASS_ID` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_RPT_TRIAL_BAL_SUBCLSID` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `UK_ACC_RRT_TRIAL_BAL_01` | yes | `USER_ID`, `ACC_SUB_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Populated by a report-generation call on the Fiscal Year Close screen (Accounting > Transaction > Fiscal Year Close) before the closing trial balance is reviewed; also read by the standalone Trial Balance report under Accounting Reports (`RF_REPORT`-driven report list). Because it's keyed only by user id with no date-range or company filter, concurrent use by the same user across different companies/date-ranges can cross-contaminate the data returned — a known bug, not a schema detail.

## Feature

[features/fiscal-year-close.md](../features/fiscal-year-close.md), [features/accounting-reports.md](../features/accounting-reports.md)
