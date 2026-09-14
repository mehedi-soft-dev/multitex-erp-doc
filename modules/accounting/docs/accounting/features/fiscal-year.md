# Feature: Fiscal Year

```yaml
---
id: feat:acc-fiscal-year
module: accounting
category: master-data
tables: [ACC_FISCAL_YEAR, ACC_OPENING_BALANCE]
status: verified
---
```

## Overview

A fiscal year record defines a company's accounting-year boundary: a name, a fiscal
start/end date pair, a separate "calendar" start/end date pair, and an open/closed flag.

There is no master Add/Edit/Delete screen for this table anywhere in the app. A complete
database package for full CRUD (`PKG_ACC_FISCAL_YEAR.sql`, dated 2025-06-17) exists in the
Oracle repo, but it is never called from any C# or Angular code — completely orphaned. The
only fiscal-year functionality actually reachable by a user today lives inside the Fiscal
Year Close transaction screen: a read-only "Period" dropdown, and the year-end Closing
Process button. As shipped, fiscal years can only be closed through the app — never
created, edited, or removed. Someone must be inserting rows directly (SQL, a seed script,
or a screen that hasn't been merged yet).

Vouchers don't formally belong to a fiscal year. No voucher table carries a fiscal-year
foreign key — scoping is done purely by comparing a voucher's date against each fiscal
year's date range at save time. The only table with a real fiscal-year foreign key is
`ACC_OPENING_BALANCE`, created when a year is closed.

## Fields

Reconstructed from the orphaned insert procedure plus the C# model, since no Add/Edit UI
exists to observe directly.

| Column | Required? | Meaning | Currently used by the shipped app? |
|---|---|---|---|
| `ACC_FISCAL_YEAR_ID` | PK, auto | Surrogate key | Yes |
| `HR_COMPANY_ID` | Yes | Which company this fiscal year belongs to | Yes — the filter key on every query |
| `FY_NAME_EN` | Yes | Display name, e.g. "2025-2026" | Yes — Period dropdown text |
| `FY_NAME_BN` | — | Bengali display name | **No** — selected but never rendered; the orphaned insert procedure can't even set it |
| `FY_START_DATE` / `FY_END_DATE` | Yes | Fiscal year date range | Yes — voucher-date validation, closing process, dropdown auto-fill |
| `CY_START_DATE` / `CY_END_DATE` | — | A separate "calendar year" date range | **No** — selected but never consumed by the one screen that exists |
| `IS_CLOSED` | Yes | Whether the year has been closed | Yes — filter, closing-process gate, voucher validation |
| `REMARKS` | No | Free-text notes | Read-displayed (Period dropdown subtitle) but currently un-settable — no live save path exists |
| `CREATION_DATE` / `CREATED_BY` / `LAST_UPDATE_DATE` / `LAST_UPDATED_BY` | auto | Audit trail | **No** — only read by the orphaned new package; the currently-used old select and the C# model both drop them entirely |

No `[Required]`/`[StringLength]` or any validation attributes exist on the C# model at all —
10 bare auto-properties.

## Relationships

`ACC_FISCAL_YEAR` links to `ACC_OPENING_BALANCE` via `ACC_FISCAL_YEAR_ID` — the only real
foreign key involving this table, created by the closing process.

Everywhere else, the relationship is a date-range check only, not a real FK — consumed by:

- The voucher save path (blocks posting into a closed year)
- The Fiscal Year Close screen's Period dropdown and trial balance grid
- Financial reports walking "next year" via date-range join (P&L, balance sheet carry-forward)

Because there's no real FK from vouchers to a fiscal year, every report that needs "this
year's transactions" has to re-derive it via date-range join every time — the same join
pattern repeated near-identically 8+ times across different report procedures.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The master-data Add/Edit/Delete screen doesn't exist in the shipped app at all — a fully-built Oracle package for it exists but is never called from anywhere. The only fiscal-year functionality a user can actually reach is the read-only Period dropdown and the Closing Process button on a different (transaction) screen.
- **Critical:** A trial-balance-fetch API action has a copy/paste bug: it computes one value, discards it, and returns a second, unrelated call's result instead — which reads from a shared staging table keyed only by user ID, with no date-range or company filter of its own. If the first call's population step ever fails or is skipped, the endpoint silently returns stale data left over from a previous screen/date-range the same user viewed; two browser tabs for the same user against different companies can cross-contaminate.
- **Critical:** The fiscal-year list endpoint's "closed" filter parameter doesn't actually filter by the value passed in — it only checks whether the parameter is null. Passing "show me closed years" still returns only open years; the orphaned new package fixes this correctly, but that code path is never called.
- **Warning:** Two independent, divergent "close a fiscal year" implementations exist, and the app only wires up the one with fewer safety checks — the unused one guards against existing opening balances and unposted vouchers before proceeding; the live one has no such guard.
- **Warning:** The closing procedure accepts an option parameter that is never actually checked — the closing logic runs unconditionally regardless of what's passed, unlike every other multi-purpose procedure in the same package.
- **Warning:** No explicit COMMIT in the closing procedure — only a ROLLBACK in the exception handler. Whether a "successful" closing is actually persisted depends entirely on connection autocommit settings.
- **Warning:** No overlap/gap validation between fiscal years anywhere — two years for the same company could have overlapping date ranges, which would make the voucher-validation lookup ambiguous. Worse: that ambiguity (a multi-row result where one row was expected) is swallowed by a blanket exception handler that silently disables the closed-year check entirely rather than surfacing an error.
- **Minor:** No server-side validation of any kind on the model — 10 bare auto-properties, nothing to enforce even on the one endpoint that's decorated with a validation attribute.
- **Minor:** A session value is read eagerly in the API controller's constructor for every action, including the plain list read that doesn't even use it — a null/expired session throws before any action method runs, even the harmless one.

## Unused Columns

Of 14 reconstructed columns, 6 are genuinely used end-to-end, 1 is displayed but has no
live write path, and 7 are write-only/effectively unused or entirely unreachable by any
shipped screen:

| Column | Verdict |
|---|---|
| `FY_NAME_BN` | Write-only / effectively unused — no UI field, and the orphaned insert procedure can't even set it. |
| `CY_START_DATE` / `CY_END_DATE` | Write-only / effectively unused in the one screen that exists. |
| `CREATION_DATE` / `CREATED_BY` / `LAST_UPDATE_DATE` / `LAST_UPDATED_BY` | Unused end-to-end — the live code path drops them entirely; the C# model doesn't even declare properties for them. |

This unusually high proportion of dead columns is a direct consequence of the core finding
above: the master CRUD screen that would normally set/use all of these columns simply
doesn't exist yet.
