# Table: SC_ROLE_REPORT

```yaml
---
id: tbl:SC_ROLE_REPORT
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [CREATED_BY->SC_USER.SC_USER_ID, LAST_UPDATE_LOGIN->SC_USER.SC_USER_ID, RF_REPORT_ID->RF_REPORT.RF_REPORT_ID, SC_ROLE_ID->SC_ROLE.SC_ROLE_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, SC_ROLE_REPORT_ID]
---
```

Role-to-report mapping table (security module, `SC_*` naming per convention) — determines which reports in `RF_REPORT` a given user's role can see on the Accounting Reports screen. No column list exists in source docs beyond its role as a mapping table; source docs describe behavior, not columns.

## Columns

No columns are named in the source docs. The feature doc describes it only as "a role-mapping table (which reports this user's role can see)" joined against `RF_REPORT` to build the radio list — implying at minimum a role FK and a report FK, but neither is named explicitly.

## Keys & Indexes

**Primary key:** `PK_SC_ROLE_REPORT` on `SC_ROLE_REPORT_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_ROLE_ROLEREPORT1` | `SC_ROLE_ID`, `RF_REPORT_ID` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_CRTUSER_ROLEREPORT` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_LOGUSER_ROLEREPORT` | `LAST_UPDATE_LOGIN` | `SC_USER.SC_USER_ID` |
| `FK_REPORT_ROLEREPORT` | `RF_REPORT_ID` | `RF_REPORT.RF_REPORT_ID` |
| `FK_ROLE_ROLEREPORT` | `SC_ROLE_ID` | `SC_ROLE.SC_ROLE_ID` |
| `FK_UPDUSER_ROLEREPORT` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_SC_ROLE_REPORT` | yes | `SC_ROLE_REPORT_ID` |
| `UK_ROLE_ROLEREPORT1` | yes | `SC_ROLE_ID`, `RF_REPORT_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Joined with `RF_REPORT` to filter the Accounting Reports screen's radio list to only the reports the current user's role has been granted. This join is enforced only on the displayed list, not on the render endpoint itself — a known critical bug: the endpoint that actually returns report data never re-validates the submitted report code against this mapping, so any authenticated session can request any report code directly. A separate "built-in admin" user type bypasses this table's join entirely and sees every report in the group.

## Feature

[features/accounting-reports.md](../features/accounting-reports.md)
