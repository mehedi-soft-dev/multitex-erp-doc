# Table: RF_REPORT

```yaml
---
id: tbl:RF_REPORT
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [CREATED_BY->SC_USER.SC_USER_ID, RF_REPORT_GRP_ID->RF_REPORT_GRP.RF_REPORT_GRP_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, RF_REPORT_ID]
---
```

Report-definition reference table driving the Accounting Reports screen's (Accounting > Reports > Accounting Reports) radio-button report list — one row per report, roughly a dozen columns per the source doc, though only report name and report code are actually used by the shipped screen; the rest are unused or discarded. No full column list with names/types exists in source docs.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| (unnamed) report name column | — | Used for the radio-button label | accounting-reports.md |
| (unnamed) report code column | — | Drives the entire client/server switch that selects which of ~19 report procedures runs | accounting-reports.md |
| (unnamed) sort-order column | — | Used only inside the database query to order the list; discarded before reaching the client | accounting-reports.md |
| (unnamed) ad-hoc SQL column | — | Name implies each report row was meant to carry its own SQL definition for a data-driven report engine; never read by any code — every report is hardcoded as its own branch instead | accounting-reports.md |
| (unnamed) parameter-definition column | — | Name implies each report row was meant to carry its own parameter definition; never read anywhere, same as the SQL column above | accounting-reports.md |
| (unnamed, several more) | — | "Roughly a dozen columns" total per the doc; several are fetched by the query and silently discarded in mapping code, never reaching the screen — not individually named | accounting-reports.md |

## Keys & Indexes

**Primary key:** `PK_RF_REPORT` on `RF_REPORT_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_RPT_CODE` | `RPT_CODE` |
| `UK_RPT_NAMEBN` | `RPT_NAME_BN` |
| `UK_RPT_NAMEEN` | `RPT_NAME_EN` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_CRTUSER_RPT` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_RPTGRP_RPT` | `RF_REPORT_GRP_ID` | `RF_REPORT_GRP.RF_REPORT_GRP_ID` |
| `FK_UPDUSER_RPT` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_RF_REPORT` | yes | `RF_REPORT_ID` |
| `UK_RPT_CODE` | yes | `RPT_CODE` |
| `UK_RPT_NAMEBN` | yes | `RPT_NAME_BN` |
| `UK_RPT_NAMEEN` | yes | `RPT_NAME_EN` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Joined with a role-mapping table (`SC_ROLE_REPORT`) to build the per-user, permission-filtered radio list on the Accounting Reports screen. A separate "built-in admin" user type bypasses the role join and sees every report in the group. The chosen report code drives one shared render endpoint that switches on it and calls one of ~19 dedicated report procedures reading from Chart of Accounts / Cost Center / Voucher tables — not a data-driven engine despite the unused SQL/parameter-definition columns suggesting one was intended.

## Feature

[features/accounting-reports.md](../features/accounting-reports.md)
