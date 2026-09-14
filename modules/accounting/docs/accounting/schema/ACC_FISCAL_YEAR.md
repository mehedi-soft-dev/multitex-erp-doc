# Table: ACC_FISCAL_YEAR

```yaml
---
id: tbl:ACC_FISCAL_YEAR
module: accounting
status: inferred
package: PKG_ACC_FISCAL_YEAR
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, CREATED_BY->SC_USER.SC_USER_ID, LAST_UPDATED_BY->SC_USER.SC_USER_ID, ACC_FISCAL_YEAR_ID]
---
```

Defines a company's accounting-year boundary: a name, a fiscal start/end date pair, a separate "calendar" start/end date pair, and an open/closed flag. There is no master Add/Edit/Delete screen in the shipped app — a full CRUD package (`PKG_ACC_FISCAL_YEAR.sql`, dated 2025-06-17) exists in Oracle but is never called from any C# or Angular code; the only reachable fiscal-year functionality is the read-only Period dropdown and Closing Process button on the Fiscal Year Close transaction screen.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_FISCAL_YEAR_ID` | — | PK, auto | feature doc |
| `HR_COMPANY_ID` | — | Which company this fiscal year belongs to; the filter key on every query | feature doc |
| `FY_NAME_EN` | — | Display name, e.g. "2025-2026"; shown in the Period dropdown | feature doc |
| `FY_NAME_BN` | — | Bengali display name; selected but never rendered, and the orphaned insert procedure can't even set it | feature doc |
| `FY_START_DATE` | — | Fiscal year start date; used for voucher-date validation, closing process, dropdown auto-fill | feature doc |
| `FY_END_DATE` | — | Fiscal year end date; same uses as `FY_START_DATE` | feature doc |
| `CY_START_DATE` | — | Separate "calendar year" start date; selected but never consumed by the one screen that exists | feature doc |
| `CY_END_DATE` | — | Separate "calendar year" end date; same as `CY_START_DATE` | feature doc |
| `IS_CLOSED` | — | Whether the year has been closed; used as filter, closing-process gate, and voucher validation | feature doc |
| `REMARKS` | — | Free-text notes; read-displayed in the Period dropdown subtitle, currently un-settable (no live save path) | feature doc |
| `CREATION_DATE` | — | Audit; only read by the orphaned new package, dropped by the live select and C# model | feature doc |
| `CREATED_BY` | — | Audit; same as `CREATION_DATE` | feature doc |
| `LAST_UPDATE_DATE` | — | Audit; same as `CREATION_DATE` | feature doc |
| `LAST_UPDATED_BY` | — | Audit; same as `CREATION_DATE` | feature doc |

No `[Required]`/`[StringLength]` or other validation attributes exist on the C# model — 10 bare auto-properties.

## Keys & Indexes

**Primary key:** `PK_ACC_FISCAL_YEAR` on `ACC_FISCAL_YEAR_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_ACCFY_COMP` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_ACCFY_CRTBY_USR` | `CREATED_BY` | `SC_USER.SC_USER_ID` |
| `FK_ACCFY_UPDBY_USR` | `LAST_UPDATED_BY` | `SC_USER.SC_USER_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_ACC_FISCAL_YEAR` | yes | `ACC_FISCAL_YEAR_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_FISCAL_YEAR` links to `ACC_OPENING_BALANCE` via `ACC_FISCAL_YEAR_ID` — the only real foreign key involving this table, created by the year-end closing process. Vouchers do not carry a fiscal-year FK at all; scoping against a fiscal year is done purely by comparing a voucher's date against `FY_START_DATE`/`FY_END_DATE` at save time, a pattern repeated near-identically across 8+ report procedures. No overlap/gap validation exists between fiscal years for the same company, and an ambiguous multi-row lookup (from overlapping ranges) is silently swallowed, disabling the closed-year check entirely.

## Feature

[features/fiscal-year.md](../features/fiscal-year.md), [features/fiscal-year-close.md](../features/fiscal-year-close.md)
