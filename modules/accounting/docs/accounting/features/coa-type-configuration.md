# Feature: COA Type Configuration

```yaml
---
id: feat:acc-coa-type-configuration
module: accounting
category: master-data
tables: [ACC_COA_TYPE_CONFIG_H, ACC_COA_TYPE_CONFIG_D]
status: verified
---
```

## Overview

No menu route, controller, API, or Angular screen exists for this anywhere in the app. But
unlike most "not implemented" menus, the database groundwork is fully built: two tables and
five stored procedures (list/save/update/delete) already exist in the Oracle repo, and
financial reports (Balance Sheet / Income Statement style logic) already depend on this
configuration being populated. Only the screen to maintain it is missing.

The idea: map specific GL accounts (at any of the 5 Chart of Accounts tree levels) to a
fixed set of 11 "COA Type" categories — Bank Accounts, Cash Accounts, Purchase Account,
Direct Expenses, Income Tax, Retained Earnings, Profit & Loss Ledger, All Owner's Equity
Ledgers, etc. — so reports can query "give me all Bank Account-type ledgers" instead of
hardcoding specific account IDs.

This is unrelated to the "Vouchar For Type" dropdown already documented on the Chart of
Accounts page (that's a different lookup, for tagging voucher lines with Buyer/Supplier/
Employee/Bank parties).

## Fields

Reconstructed entirely from the Oracle package, since no C# model or UI exists.

#### ACC_COA_TYPE_CONFIG_H (header — one row per rule)

| Column | Meaning |
|---|---|
| `ACC_COA_TYPE_CONFIG_H_ID` | PK |
| `LK_COA_TYPE_CONFIG_ID` | Which of the 11 fixed COA Type categories this rule is for |
| `LK_COA_LAYER_ID` | Which Chart of Accounts tree level the detail rows point into (Parent Class / Account Class / Main Class / Map Class / Sub Class) |
| `IS_ACTIVE`, audit columns | Standard active flag + created/updated audit trail |

#### ACC_COA_TYPE_CONFIG_D (detail — one row per selected GL node)

| Column | Meaning |
|---|---|
| `ACC_COA_TYPE_CONFIG_D_ID` | PK |
| `ACC_COA_TYPE_CONFIG_H_ID` | FK to the header rule |
| `ACC_AC_PARENT_CLASS_ID` / `ACC_AC_CLASS_ID` / `ACC_MAIN_CLASS_ID` / `ACC_MAP_CLASS_ID` / `ACC_SUB_CLASS_ID` | One nullable FK per Chart of Accounts level — whichever one matches the header's layer is populated |

The 11 fixed category values (from a shared lookup-constants file): Income Tax, Bank
Accounts, Cash Accounts, Stock and Store, Purchase Account, Direct Expenses, Retained
Earnings for Profit/Loss, Total Expense After Gross Profit/Loss, All Income Tax Ledgers,
Profit/Loss Ledger, All Owner's Equity Ledgers.

## Relationships

`ACC_COA_TYPE_CONFIG_H` (rule: which COA Type) has a 1:N relationship to
`ACC_COA_TYPE_CONFIG_D` (which GL nodes), which in turn points into the Chart of Accounts
(any of its 5 levels).

Already consumed by (live, DB-layer only):

- Income Tax section of financial statements
- Direct Expenses rollups
- Purchase Account rollups
- Profit/Loss Ledger & Retained Earnings sections

The backend logic that consumes this configuration is live and already dozens of report
queries deep — only the screen to maintain it is missing. Anyone whose reports rely on it
must be populating rows directly against the database today.

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** No menu route, controller, API, or Angular screen exists to maintain this data at all — any user-facing menu item with this name today would 404 or simply not exist in the current route table.
- **Warning:** The save procedure passes GL-node selections as an XML blob parsed with XMLTABLE, and the update variant does a full delete-and-reinsert of every detail row rather than a diff — not a bug per se since nothing calls it, but worth knowing if this is ever wired up: there's no incremental-update path to build on.
- **Minor:** No CREATE TABLE DDL exists for either table in the Oracle repo — like most tables in this system, the schema was applied directly to the database rather than version-controlled, so this documentation is reconstructed entirely from the stored procedures' INSERT/SELECT statements.

## Unused Columns

Not applicable in the usual sense — since no application code references either table at
all, every column is "unused by the app" by definition. The columns above are all
genuinely read/written by the Oracle procedures themselves and by the report queries that
join into them, so nothing here looks like schema cruft — it's a complete feature waiting
for a front door.
