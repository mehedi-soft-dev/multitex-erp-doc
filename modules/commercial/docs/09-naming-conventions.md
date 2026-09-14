# 09 — Naming conventions

Learning these names is faster than reading every file.

## C#

| Kind | Pattern | Example |
|---|---|---|
| Service interface | `I{Name}Service` | `IMC_BUYERService` |
| Service impl | `{Name}Service` | `MC_BUYERService` |
| DTO | `{TABLE}Model` | `MC_BUYERModel` |
| Filter | `{Name}Filter : BaseSearchFilter` | `MC_BUYERFilter` |
| MVC controller | `{Feature}Controller` | `ScUserController` |
| Web API | `{Feature}ApiController` or `{Feature}Controller` in `Api/` | `BuyerApiController` |
| Area registration | `{Area}AreaRegistration` | `MerchandisingAreaRegistration` |

Namespaces: `ERP.BLL.{Module}`, `ERP.Model`, `ERPSolution.Areas.{Module}.Api`.

## Oracle objects

| Kind | Pattern | Example |
|---|---|---|
| Package | `PKG_{DOMAIN}` | `PKG_MERCHANDISING`, `PKG_KNIT_PLAN` |
| Procedure | `{table}_{insert\|update\|select}` | `mc_buyer_insert` |
| Table | `{PREFIX}_{ENTITY}` | `MC_BUYER`, `KNT_PLAN_H` |
| PK | `{TABLE}_ID` | `MC_BUYER_ID` |
| FK | `{OTHER_TABLE}_ID` | `HR_COUNTRY_ID` on buyer |
| Lookup id | `LK_{NAME}_ID` | `LK_ITEM_STATUS_ID` |
| Reference master | `RF_{ENTITY}` | `RF_CURRENCY`, `RF_BANK` |

## Module prefixes

| Prefix | Module |
|---|---|
| `MC_` | Merchandising |
| `KNT_` | Knitting |
| `DYE_` | Dyeing |
| `DF_` | Dyeing finishing |
| `DLAB_` | Dyeing lab |
| `HR_` | HR / org |
| `CM_` | Commercial |
| `INV_` | Inventory item master |
| `SCM_` | Supply chain / store / supplier / PR |
| `GMT_` | Garments / cutting / IE / planning (context from next token) |
| `RF_` | Reference data |
| `SC_` | Security |
| `SLS_` | Sales delivery |
| `ACC_` | Accounting |
| `FP_` / `TXT_` | Fabric / textile planning |
| `LOGS_` | Logistics |
| `RND_` | R&D |

`GMT_CUT_` is cutting; `GMT_SEW_` sewing; `GMT_PLN_` planning; `GMT_IE_` industrial engineering.

## Header / detail

`MC_ORDER_H` + children. C# often has `List<T> items` on the header model.

## Parameters and options

- Procedure args: `p` + column name (`pBUYER_CODE`).
- `pOption`: 1000 insert, 2000 update, 3000 list, 3001+ variants.
- `pMsg`: output message.
- Session user: `multiScUserId`.
- Cache brand: `MultiTEXCache`.

## Files vs tables

If you see `MC_STYL_BGT_HService.cs`, expect:

- table `MC_STYL_BGT_H`
- package procedure `mc_styl_bgt_h_select` (or similar) in a `PKG_MC_*` / merchandising package
- API somewhere under `Areas/Merchandising/Api`

## Doc / graph ID rules

Principle: **every `id:` segment used in `docs/features/*.md`, `docs/schema/*.md`, or
`.agent/knowledge-graph/*.jsonl` must be a string that already exists above** (an Area name, a table prefix,
an exact table/package/procedure/class name) — never an invented abbreviation. If you can't point
to the exact file, line, or table above a term comes from, it doesn't belong in an ID.

This keeps the docs "organized as code": one canonical name per concept, so mapping a doc/graph
node back to the actual source is a lookup, not a guess.

| ID | Built from | Example |
|---|---|---|
| `mod:{area}` | Area folder name, lowercased | `mod:merchandising` |
| `feat:{prefix}-{entity}` | Route prefix if [06-modules.md](06-modules.md) has one for the module, else the table prefix from this file (lowercased, trailing `_` stripped); never a new abbreviation | `feat:mrc-buyer` (route prefix `mrc`) |
| `tbl:{TABLE}` | Exact uppercase Oracle table name | `tbl:MC_BUYER` |
| `pkg:{PKG_NAME}` | Exact package name | `pkg:PKG_MERCHANDISING` |
| `proc:{pkg}.{proc}` | Exact package + procedure name | `proc:PKG_MERCHANDISING.mc_buyer_insert` |
| `model:{ClassName}` | Exact C# class name | `model:MC_BUYERModel` |
| `svc:{ClassName}` | Exact C# service class name | `svc:MC_BUYERService` |
| `sess:{name}` | Exact session key string | `sess:multiScUserId` |

If two of these seem to disagree (module spelled out as `merchandising`, route prefix abbreviated
to `mrc`), that's expected — different concepts, both real, both already in the code. Don't
collapse them into a new in-between term.

**Two audiences, two vocabularies — don't blend them.** Developer-facing text (doc body, IDs,
code snippets) uses exact identifiers, copy-paste accurate. Manager-facing text (doc titles,
`## Purpose` sections) uses the Area/screen name as shown in the app menu — e.g. "Merchandising",
"Buyer" — because that's the term a manager reading the doc actually recognizes. A feature file's
H1 and `## Purpose` use the manager vocabulary; its front-matter and `## Oracle`/`## C# map`
sections use the developer vocabulary.

Audited the existing feature/schema files against this rule (2026-09-03) — all comply already
(`mrc` is the real `api/mrc` route prefix, not invented; `MC_BUYER`, `HR_DEPARTMENT`,
`PKG_MERCHANDISING`, `PKG_SECURITY`, `PKG_ADMIN` are exact code/DB names). This section formalizes
what's already true so it doesn't drift as more people add docs.
