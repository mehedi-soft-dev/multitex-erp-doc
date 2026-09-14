# Table: ACC_COA_TYPE_CONFIG_H

```yaml
---
id: tbl:ACC_COA_TYPE_CONFIG_H
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [LK_COA_LAYER_ID->LOOKUP_DATA.LOOKUP_DATA_ID, LK_COA_TYPE_CONFIG_ID->LOOKUP_DATA.LOOKUP_DATA_ID, ACC_COA_TYPE_CONFIG_H_ID]
---
```

Header table (one row per rule) mapping GL accounts to a fixed set of 11 "COA Type" categories (Bank Accounts, Cash Accounts, Purchase Account, Direct Expenses, Income Tax, Retained Earnings, Profit & Loss Ledger, All Owner's Equity Ledgers, etc.) so financial reports can query "all Bank Account-type ledgers" instead of hardcoding account IDs. No menu route, controller, API, or Angular screen exists to maintain this table — it is reconstructed entirely from the Oracle package's list/save/update/delete procedures, which are live and already consumed by report queries.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `ACC_COA_TYPE_CONFIG_H_ID` | — | PK | feature doc |
| `LK_COA_TYPE_CONFIG_ID` | — | Which of the 11 fixed COA Type categories this rule is for | feature doc |
| `LK_COA_LAYER_ID` | — | Which Chart of Accounts tree level the detail rows point into (Parent Class / Account Class / Main Class / Map Class / Sub Class) | feature doc |
| `IS_ACTIVE` | — | Standard active flag | feature doc |
| audit columns | — | Created/updated audit trail (specific column names not stated in source) | feature doc |

## Keys & Indexes

**Primary key:** `SYS_C0028862` on `ACC_COA_TYPE_CONFIG_H_ID`

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_LK_COA_LAYER_ID` | `LK_COA_LAYER_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |
| `FK_LK_COA_TYPE` | `LK_COA_TYPE_CONFIG_ID` | `LOOKUP_DATA.LOOKUP_DATA_ID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `SYS_C0028862` | yes | `ACC_COA_TYPE_CONFIG_H_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_COA_TYPE_CONFIG_H` has a 1:N relationship to `ACC_COA_TYPE_CONFIG_D` via `ACC_COA_TYPE_CONFIG_H_ID` — each header rule (a COA Type + tree level) fans out to one or more detail rows naming the actual GL nodes. Already consumed (DB-layer only) by the Income Tax, Direct Expenses, Purchase Account, and Profit/Loss Ledger & Retained Earnings sections of financial statements. The save procedure passes GL-node selections as an XML blob parsed with XMLTABLE; the update variant does a full delete-and-reinsert of detail rows rather than a diff.

## Feature

[features/coa-type-configuration.md](../features/coa-type-configuration.md)
