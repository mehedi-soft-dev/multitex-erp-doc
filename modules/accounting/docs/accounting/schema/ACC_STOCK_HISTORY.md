# Table: ACC_STOCK_HISTORY

```yaml
---
id: tbl:ACC_STOCK_HISTORY
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [HR_COMPANY_ID->HR_COMPANY.HR_COMPANY_ID, ACC_SUB_CLASS_ID->ACC_SUB_CLASS.ACC_SUB_CLASS_ID, STOCK_HISTORY_ID]
---
```

Real, heavily-used table backing month-end stock closing entry (Accounting > Transaction > Stock Closing) — one row per company/year/month/stock-GL-account, holding the closing stock value. Confirmed as the actual persisted table by four separate financial reports (Balance Sheet, Trial Balance, opening-balance procedure, Profit & Loss), despite the screen's C# model class being misleadingly named `ACC_STOCK_CLOSING` (with a matching `ACC_STOCK_CLOSING_SEQ` sequence) — there is no `ACC_STOCK_CLOSING` table; `ACC_STOCK_HISTORY` is the real one.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| (unnamed) Code/Particular columns | — | 3-part Chart-of-Accounts code and account name, read-only display | stock-closing.md |
| (unnamed) Closing value column | — | The only genuinely editable field — month-end stock value the accountant enters | stock-closing.md |
| `HR_COMPANY_ID` | — | Write-only from the posting path's perspective — neither posting procedure filters/reads it; only the entry screen's own read query uses it. Also: the read query has no company-code scoping, relying on a different company identifier instead — an inconsistent-key issue | stock-closing.md |
| `IS_FINALIZE` | — | Set by the app/procedures but never read back into any UI element — invisible to the end user | stock-closing.md |
| Opening / Dr / Cr / Balance / Net Amt (view-model fields) | — | Round-trip on the model but always zero and never shown — leftovers from a richer stock-ledger view that was never finished; not confirmed as real table columns | stock-closing.md |

## Keys & Indexes

**Primary key:** `PK_ACC_STK_HISTRY` on `STOCK_HISTORY_ID`

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_STK_HISTRY01` | `HR_COMPANY_ID`, `YEAR_CODE`, `MONTH_CODE`, `ACC_SUB_CLASS_ID` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_HRCOMP_STK_HISTRY` | `HR_COMPANY_ID` | `HR_COMPANY.HR_COMPANY_ID` |
| `FK_SUBCLS_STK_HISTRY` | `ACC_SUB_CLASS_ID` | `ACC_SUB_CLASS.ACC_SUB_CLASS_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `IDX_STOCK_HISTORY_01` | no | `YEAR_CODE`, `MONTH_CODE` |
| `IDX_STOCK_HISTORY_02` | no | `HR_COMPANY_ID`, `YEAR_CODE`, `MONTH_CODE` |
| `PK_ACC_STK_HISTRY` | yes | `STOCK_HISTORY_ID` |
| `UK_STK_HISTRY01` | yes | `HR_COMPANY_ID`, `YEAR_CODE`, `MONTH_CODE`, `ACC_SUB_CLASS_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Populated by the Stock Closing entry screen's grid (one row per Chart-of-Accounts GL account flagged "stock" via a system parameter, scoped by company/year/month). Its (currently UI-unreachable) posting action generates a closing voucher and companion opening voucher in `ACC_VOUCHER_MASTER` / `ACC_VOUCHER_DETAIL` (voucher numbers prefixed `STC-`/`STO-`, voucher type 5, cost center forced to the "N/A" sentinel). Read by the Balance Sheet report, Trial Balance report, opening-balance procedure, and Profit & Loss calculation.

## Feature

[features/stock-closing.md](../features/stock-closing.md)
