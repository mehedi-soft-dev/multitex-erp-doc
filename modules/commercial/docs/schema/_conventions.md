# Schema conventions

There is **no DDL in git**. Treat this folder as a living data dictionary.

## How a table file is named

`docs/schema/{TABLE_NAME}.md` — Oracle table name, uppercase.

## How to infer a table from C#

| Signal | Meaning |
|---|---|
| Class `MC_BUYERModel` | Table `MC_BUYER` until proven otherwise |
| Property `MC_BUYER_ID` | PK |
| Property `HR_COUNTRY_ID` | FK to `HR_COUNTRY` |
| `IS_ACTIVE` CHAR-like string | Flag `Y`/`N` typical |
| `CREATION_DATE`, `CREATED_BY`, `LAST_UPDATE_DATE`, `LAST_UPDATED_BY` | Audit |
| `LAST_UPDATE_LOGIN`, `VERSION_NO` | Extra audit / optimistic lock (not on every table) |
| `items`, `text`, `expanded`, `selected`, `TranMode`, `XML` | **UI / payload**, not columns |
| `COUNTRY_NAME_EN` on a buyer model | **Join projection** |

Mark every column `source: model | brow | package | db`.

## Standard column groups

**Identity:** `{TABLE}_ID`  
**Business codes:** `*_CODE`, `*_SNAME`, `*_NAME_EN`, `*_NAME_BN`  
**Flags:** `IS_ACTIVE`, `IS_LEAF`, …  
**Audit:** `CREATION_DATE`, `CREATED_BY`, `LAST_UPDATE_DATE`, `LAST_UPDATED_BY`  
**Header/detail:** `_H` / `_D`

## Header–detail

Document the pair together. Child FK is usually `{HEADER_TABLE}_ID`.

## Lookups

- `RF_*` shared reference (currency, bank, UOM).
- `LK_*_ID` lookup id (status, type groups).
- `SC_*` security.
- `HR_*` org / people even when used from merch/knit.

## Completeness levels

| Status | Meaning |
|---|---|
| `inferred` | From C# model + BLL mapping only |
| `package-checked` | Insert/update params match package spec |
| `db-verified` | `ALL_TAB_COLUMNS` dump |

New files start as `inferred`. Promote when you open the package or query Oracle.

## What not to do

- Do not copy `Web.config` passwords into schema files.
- Do not assume every model property is a column.
- Do not create hundreds of stub files; add a table when a feature needs it.
