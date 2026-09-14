# 06 — Module catalog

Each **MVC Area** is a module. BLL and Model folders usually match. Oracle prefixes encode the same module.

## Area ↔ code ↔ Oracle

| Area | API ctrls | MVC ctrls | Angular JS | BLL folder | Model folder | Table prefix | Oracle packages (examples) |
|---|---:|---:|---:|---|---|---|---|
| Admin | 0 | 10 | 17 | `Admin` | `Admin` | `HR_`, `RF_` | `PKG_ADMIN` |
| Commercial | 17 | 2 | 64 | `Commercials` | `Commercial`, `CashIncentive` | `CM_` | `PKG_CM_*` |
| Cutting | 12 | 1 | 71 | `Cutting` | `Cutting` | `GMT_CUT_`, `GMT_MRKR_` | `PKG_CUT_*`, `PKG_GMT_CUT_*` |
| Dyeing | 48 | 4 | 186 | `Dyeing` | `Dyeing` | `DYE_`, `DF_` | `PKG_DYE_*`, `PKG_DF_*` |
| DyeingLab | 5 | 1 | 12 | `DyeingLab` | `DyeingLab` | `DLAB_` | `PKG_DLAB_*` |
| FabricPlanning | 4 | 1 | 16 | `FabricPlanning` | `FabricPlanning` | `FP_`, `TXT_PLAN_` | `PKG_TXTPLN_*` |
| FinishFabric | 3 | 1 | 9 | `FinishFabric` | `FinishFabric` | `KNT_FF_` | `PKG_FIN_FAB_STK_ADJUST` |
| Garments | 19 | 1 | 62 | `Garments` | `Garments` | `GMT_SEW_`, `GMT_FIN_`, `GMT_SHIP_` | `PKG_GMT_*` |
| GenRpt | 0 | 1 | 5 | — | — | reports | `PKG_REPORTS` |
| Hr | 9 | 30 | 111 | `Hr` | `Hr` | `HR_` | `PKG_HR*`, `PKG_SALARY`, `PKG_LEAVE`, `PKG_ATTENDANCE`, `PKG_OT` |
| IE | 10 | 1 | 34 | `IE` | `IE` | `GMT_IE_` | `PKG_GMT_IE*` |
| Inventory | 14 | 3 | 56 | `Inventories` | `Inventory` | `INV_`, `SCM_STR_` | `PKG_INVENTORY`, `PKG_INV_*`, `PKG_SCM_STR*` |
| Knitting | 64 | 2 | 209 | `Knitting` | `Knitting` | `KNT_` | `PKG_KNIT_*`, `PKG_KNT_*` |
| Merchandising | 59 | 2 | 149 | `Merchandising` | `Merchandising` | `MC_` | `PKG_MERCHANDISING`, `PKG_MC_*`, `PKG_MRC_*` |
| Planning | 14 | 1 | 37 | `Planning` | `Planning` | `GMT_PLN_` | `PKG_PLANNING_COMMON`, `PKG_GMT_PLN_*` |
| Purchase | 15 | 2 | 41 | `Purchases` | `Purchase` | `SCM_`, `SCM_PURC_`, `SCM_SUP_` | `PKG_PUR_*`, `PKG_SCM_*` |
| RND | 1 | 1 | 6 | `RND` | `RND` | `RND_` | `PKG_RND_FAB_PROC_SHEET_H` |
| SalesDelivery | 7 | 1 | 17 | `SalesDelivery` | `SalesDelivery` | `SLS_` | `PKG_SLS_*` |
| Security | 11 | 6 | 32 | `Securities` | `Security` | `SC_` | `PKG_SECURITY`, `PKG_MENU`, `PKG_RF_SYS_PARAM` |

Counts are file counts under each Area folder (API `.cs`, MVC `.cs`, Client `.js`).

## Domains without an Area

| Domain | Code | Prefix | Notes |
|---|---|---|---|
| Accounting | almost no BLL; `ERP.Model/Accounting` | `ACC_` | Many `PKG_ACC_*`, `PKG_VOUCHER`; no MVC Area in this tree |
| Logistics | `ERP.BLL/Logistics` | `LOGS_` | Drivers / vehicles |
| Inquiry | `Controllers/InquiryApiController.cs` | `MKT_` | `PKG_INQUIRY` |
| Buyer portal | `Controllers/BuyerPortalApiController.cs` | — | `PKG_BUYER_PORTAL` |
| Common / RF | `ERP.BLL/Commons`, `ERP.Model/Common` | `RF_`, `LK_` | Banks, currency, fabric type, lookups |
| Caching | `ERP.BLL/Caching` | — | HTTP cache |

## Typical API route prefixes

Grep `[RoutePrefix("api/` for the live list. Common ones:

| Prefix | Module |
|---|---|
| `api/mrc` | Merchandising |
| `api/Knit` / knitting variants | Knitting |
| `api/security` | Security |
| `api/salesdelivery` | Sales delivery |
| `api/BuyerPortal` | Buyer portal |

MVC URLs stay `{Area}/{Controller}/{Action}`.

## Cross-module coupling (expect this)

- Purchase uses `SCM_` and `CM_IMP_` (import PO).
- Cutting uses `GMT_` and fabric from `KNT_` / `DF_`.
- Inventory uses `INV_` items and `SCM_STR_` store transactions.
- Merchandising `MC_ORDER_H` is the hub many production modules read.

When you document a feature, list **upstream and downstream modules** in the feature file.

## Where to start exploring (recommended order)

1. Security (login, menu, user)
2. Admin (department, lookup)
3. Merchandising (buyer, style, order) — hub
4. Knitting or HR — largest, but follow one document (yarn issue, or employee)
5. Then Dyeing → Cutting → Garments → Commercial
