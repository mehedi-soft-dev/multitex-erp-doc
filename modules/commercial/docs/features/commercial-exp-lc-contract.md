# Feature: Commercial export LC / sales contract entry

```yaml
---
id: feat:commercial-exp-lc-contract
module: commercial
http: GET /api/cmr/ExportLCSalesContact/GetExportLcContactInfo | POST /api/cmr/ExportLCSalesContact/Save | POST /api/cmr/ExportLCSalesContact/Update
mvc: CmrController.ExpLcContractList
api: [GET api/cmr/ExportLCSalesContact/SelectAll/{pageNo}/{pageSize} -> ExportLCSalesContactController.SelectAll, GET api/cmr/ExportLCSalesContact/EXPLCWiseB2BSummary -> ExportLCSalesContactController.EXPLCWiseB2BSummary, GET api/cmr/ExportLCSalesContact/EXPLCWiseCommodityType -> ExportLCSalesContactController.EXPLCWiseCommodityType, POST api/cmr/ExportLCSalesContact/SaveCommodityBBLC -> ExportLCSalesContactController.SaveCommodityBBLC, GET api/cmr/ExportLCSalesContact/CM_EXP_LC_REVISE_REQ_GET_BY_LCID -> ExportLCSalesContactController.CM_EXP_LC_REVISE_REQ_GET_BY_LCID, GET api/cmr/ExportLCSalesContact/GetExportLCOrSCByFilter -> ExportLCSalesContactController.GetExportLCOrSCByFilter, GET api/cmr/ExportLCSalesContact/GetExportLcContactInfo -> ExportLCSalesContactController.GetExportLcContactInfo, GET api/cmr/ExportLCSalesContact/GetLcValueById -> ExportLCSalesContactController.GetLcValueById, GET api/cmr/ExportLCSalesContact/GetExportLcByBuyerID -> ExportLCSalesContactController.GetExportLcByBuyerID, GET api/cmr/ExportLCSalesContact/GetLcApplicantByBuyerID -> ExportLCSalesContactController.GetLcApplicantByBuyerID, GET api/cmr/ExportLCSalesContact/GetLcApplicantByBuyerDD -> ExportLCSalesContactController.GetLcApplicantByBuyerDD, GET api/cmr/ExportLCSalesContact/GetOrderDtlInfo -> ExportLCSalesContactController.SelectExpMcOrderByFilter, GET api/cmr/ExportLCSalesContact/GetOrderDtlComInv -> ExportLCSalesContactController.SelectExpMcOrderDetComInv, GET api/cmr/ExportLCSalesContact/GetPOListByID -> ExportLCSalesContactController.GetPOListByID, POST api/cmr/ExportLCSalesContact/SaveLcApp -> ExportLCSalesContactController.SaveLcApp, POST api/cmr/ExportLCSalesContact/Save -> ExportLCSalesContactController.Save, POST api/cmr/ExportLCSalesContact/Update -> ExportLCSalesContactController.Update, POST api/cmr/ExportLCSalesContact/ExpLCApplyToApproveRevise -> ExportLCSalesContactController.ExpLCApplyToApproveRevise, POST api/cmr/ExportLCSalesContact/CIANotifyDateSync -> ExportLCSalesContactController.CIANotifyDateSync, POST api/cmr/ExportLCSalesContact/DeleteExpLcReviseDocuent -> ExportLCSalesContactController.DeleteExpLcReviseDocuent, GET api/cmr/ExportLC/GetExportPIListByFilter -> ExportLCSalesContactController.GetExportPIListByFilter, GET api/cmr/ExportLCSalesContact/GetPaginatedOrderNoDropdown -> ExportLCSalesContactController.GetPaginatedOrderNoDropdown, GET api/cmr/ExportLCSalesContact/GetOrderDtlForLC -> ExportLCSalesContactController.GetOrderDtlForLC]
service: ICM_EXP_LC_HService / CM_EXP_LC_HService, ICM_EXP_LC_D_POService, ICM_LC_APPLICANTService
procedure: PKG_CM_EXPORT_LC.CM_EXP_LC_H_INSERT | CM_EXP_LC_H_REVISE | CM_EXP_LC_H_SELECT
pOption: 1000 insert/update (Save), 1000 revise (Update, different proc), 3000-3005 select variants
tables: [CM_EXP_LC_H, CM_EXP_LC_D_PO, CM_EXP_LC_D_NTFP, CM_EXP_LC_INCO_TERM_DELV, CM_EXP_LC_SHIPMODE_PORT, CM_EXP_LC_MRG_REP_MAP, CM_EXP_LC_H_STS, CM_EXP_LC_H_HST, CM_EXP_LC_D_PO_HST, CM_EXP_LC_D_NTFP_HST]
models: [CM_EXP_LC_HModel, CM_EXP_LC_D_POModel, CM_LC_APPLICANTModel]
session: [multiScUserId]
upstream: [feat:mrc-buyer, feat:cmr-lc-applicant, feat:commercial-buyer-notify-party]
downstream: [commercial export-lc-pi, commercial lc-ud, commercial exp-invoice, commercial bill-of-exchange, commercial import-lc (via CM_IMP_EXP_LC_MAP)]
status: inferred
---
```

## Purpose

The anchor transaction of Commercial's Export side: entering a buyer's Master LC or Sales Contract
(`IS_SC_OR_LC` flag distinguishes the two). Everything downstream — Export LC PI, L/C UD, Commercial
Invoice, Bill Of Exchange, and the Import side's back-to-back LC linkage — hangs off this header row.

## Entry

| Kind | Value |
|---|---|
| API prefix | `[RoutePrefix("api/cmr")]` |
| Controller | `src/ERPSolution/Areas/Commercial/Api/ExportLCSalesContactController.cs` |
| List | `GET ExportLCSalesContact/SelectAll/{pageNo}/{pageSize}` |
| Detail | `GET ExportLCSalesContact/GetExportLcContactInfo?pCM_EXP_LC_H_ID=` |
| Save (insert/update) | `POST ExportLCSalesContact/Save` |
| Revise (amendment) | `POST ExportLCSalesContact/Update` |
| UI | `Areas/Commercial/Client/app/` under the Commercial MVC area shell |

DI: `ICM_EXP_LC_D_POService`, `ICM_EXP_LC_HService`, `ICM_LC_APPLICANTService`.

## Execution (save)

```mermaid
sequenceDiagram
  participant UI as AngularJS
  participant API as ExportLCSalesContactController
  participant Svc as CM_EXP_LC_HService.Save
  participant DB as OraDatabase
  participant PKG as PKG_CM_EXPORT_LC.CM_EXP_LC_H_INSERT

  UI->>API: POST ExportLCSalesContact/Save (CM_EXP_LC_HModel)
  API->>Svc: Save(ob)
  Svc->>DB: ~45 params incl. pXML_PI/pXML_PO/pXML_INCOTERM/pXML_SHIPMODEPORT (CLOB),<br/>pCM_NOTIFY_PARTY_LST, pOption=1000, pCREATED_BY/pLAST_UPDATED_BY = Session["multiScUserId"]
  DB->>PKG: PKG_CM_EXPORT_LC.CM_EXP_LC_H_INSERT
  Note over PKG: branches on NVL(pCM_EXP_LC_H_ID,0) for insert vs update;<br/>parses XML CLOBs into CM_EXP_LC_D_PO / _INCO_TERM_DELV / _SHIPMODE_PORT;<br/>delete+reinsert CM_EXP_LC_D_NTFP from CSV pCM_NOTIFY_PARTY_LST;<br/>side-effect: backfills MC_BUYER.RF_BANK_ID/RF_PAYM_TERM_ID/PAYMENT_DAYS if null
  PKG-->>DB: OUTPARAM (opCM_EXP_LC_H_ID, pMsg)
  Svc-->>API: hand-built JSON from OUTPARAM
```

## Execution (revise/amend)

```mermaid
sequenceDiagram
  participant UI as AngularJS
  participant API as ExportLCSalesContactController
  participant Svc as CM_EXP_LC_HService.Update
  participant DB as OraDatabase
  participant PKG as PKG_CM_EXPORT_LC.CM_EXP_LC_H_REVISE

  UI->>API: POST ExportLCSalesContact/Update (CM_EXP_LC_HModel)
  API->>Svc: Update(ob)
  Svc->>DB: same field shape, pCREATED_BY/pLAST_UPDATED_BY taken from the MODEL (not session)
  DB->>PKG: PKG_CM_EXPORT_LC.CM_EXP_LC_H_REVISE
  Note over PKG: snapshots CM_EXP_LC_H_HST / _D_PO_HST / _D_NTFP_HST before mutating;<br/>REVISION_NO is additive; FN_CAN_REVISE guard is commented out (dead validation)
  PKG-->>DB: OUTPARAM
```

## C# map

| Layer | Type | Path |
|---|---|---|
| API | `ExportLCSalesContactController` | `src/ERPSolution/Areas/Commercial/Api/ExportLCSalesContactController.cs` |
| Service (header) | `CM_EXP_LC_HService` | `src/ERP.BLL/Commercials/CM_EXP_LC_HService.cs` |
| Service (PO/PI detail) | `CM_EXP_LC_D_POService` | `src/ERP.BLL/Commercials/CM_EXP_LC_D_POService.cs` |
| Service (LC applicant) | `CM_LC_APPLICANTService` | `src/ERP.BLL/Commercials/CM_LC_APPLICANTService.cs` |
| Model | `CM_EXP_LC_HModel` | `src/ERP.Model/Commercial/CM_EXP_LC_HModel.cs` |
| Package | `PKG_CM_EXPORT_LC` | `src/ERPSolution/oracle/packages/PKG_CM_EXPORT_LC.sql` (3269 lines) |

## Oracle

| Item | Value |
|---|---|
| Package | `PKG_CM_EXPORT_LC` |
| Insert/Update | `CM_EXP_LC_H_INSERT`, `pOption=1000` — branches on `NVL(pCM_EXP_LC_H_ID,0)` |
| Revise/Amend | `CM_EXP_LC_H_REVISE`, `pOption=1000` — separate procedure from insert, snapshots history tables first |
| Select | `CM_EXP_LC_H_SELECT` — 6 `pOption` branches: 3000 (grid w/ computed BBLC/invoice/UD aggregates + row-level `PERMISSION` flag from `RF_ACTN_STATUS.ASSIGNED_TO_LST`), 3001 (detail, joins `CM_LC_APPLICANT`/`RF_BANK_BRANCH`/`RF_BANK`/`RF_CURRENCY`), 3002 (dropdown by buyer), 3003 (lightweight id/name list), 3004 (shipment-due-in-19-days notify feed — method name says "20 days", SQL says `SYSDATE + 19` exactly, not a range), 3005 (back-to-back LC value/balance via `CM_IMP_EXP_LC_MAP`/`CM_IMP_LC_H`) |
| Main table | `CM_EXP_LC_H` |
| Child tables | `CM_EXP_LC_D_PO` (order/PI lines, XML-merged), `CM_EXP_LC_D_NTFP` (notify parties, delete+reinsert from CSV), `CM_EXP_LC_INCO_TERM_DELV`, `CM_EXP_LC_SHIPMODE_PORT` (both XML-merged, one-to-many per header), `CM_EXP_LC_MRG_REP_MAP` (merge representatives, CSV, insert-only — never updated on revise), `CM_EXP_LC_H_STS` (status history) |
| History tables (revise only) | `CM_EXP_LC_H_HST`, `CM_EXP_LC_D_PO_HST`, `CM_EXP_LC_D_NTFP_HST` |
| Constant | `CN_EXP_LC_COMPLETE := 70` — hardcoded action-status-id meaning "complete/finalized" |

## Request / response

**In (Save/Update):** `CM_EXP_LC_HModel` — buyer/company/currency/bank/payment-term header fields, plus CLOB-encoded XML for PI/PO lines, Inco Term/delivery, ship mode/port, and CSV lists for notify parties and merge reps.
**Out:** `{ success, jsonStr }` built from the procedure's OUTPARAM (`opCM_EXP_LC_H_ID`, `pMsg`).

## Tables / columns touched

Main table: `CM_EXP_LC_H` (no `docs/schema/CM_EXP_LC_H.md` yet — worth adding given how central this table is).

FKs (all corroborated by real JOIN/WHERE evidence in `PKG_CM_EXPORT_LC.sql`, not naming-convention guesses):
- `MC_BUYER_ID → MC_BUYER`, `HR_COMPANY_ID → HR_COMPANY`, `EXP_CNTRY_ID → HR_COUNTRY`, `RF_ACTN_STATUS_ID → RF_ACTN_STATUS`, `RF_PAYM_TERM_ID → RF_PAYM_TERM` (3000-select joins)
- `CM_LC_APPLICANT_ID → CM_LC_APPLICANT`, `RCV_BKBR_ID → RF_BANK_BRANCH → RF_BANK`, `RF_CURRENCY_ID → RF_CURRENCY` (3001-select joins)
- `LIN_BKBR_ID → RF_BANK_BRANCH → RF_BANK` (3002-select join)
- `CM_EXP_LC_INCO_TERM_DELV.RF_INCO_TERM_ID → RF_INCO_TERM`, `.RF_DELV_PLC_ID → RF_DELV_PLC`
- `CM_EXP_LC_SHIPMODE_PORT.RF_SHIP_MODE_ID → RF_SHIP_MODE`, `.LOAD_PORT_ID → RF_TRAN_PORT`
- `CM_EXP_LC_D_PO.MC_ORDER_H_ID → MC_ORDER_H`, `.MC_STYLE_D_ITEM_ID`/`.MC_COLOR_ID`, `.CM_EXP_PI_H_ID`/`.CM_EXP_PI_D_PO_ID → CM_EXP_PI_H`/`CM_EXP_PI_D_PO`
- Cross-module: `CM_IMP_EXP_LC_MAP` links this header to `CM_IMP_LC_H` (back-to-back import LC)

## Permissions / session

`HttpContext.Current.Session["multiScUserId"]` used for `pCREATED_BY`/`pLAST_UPDATED_BY` on **Save** only — **Update (revise) takes these from the client-submitted model instead**, an inconsistency (see Gaps). The 3000-select grid also computes a row-level `PERMISSION` flag from `RF_ACTN_STATUS.ASSIGNED_TO_LST` (a CSV of user ids per status), gating which rows a user may act on directly inside the query.

## Dependencies (other features)

- **Upstream:** `feat:mrc-buyer` (`MC_BUYER`), `feat:cmr-lc-applicant` (`CM_LC_APPLICANT`), `feat:commercial-buyer-notify-party` (`CM_NOTIFY_PARTY`/`CM_EXP_LC_D_NTFP` — the CSV delete+reinsert pattern already documented there is confirmed here at both the insert (lines 612-632) and revise (753-771) call sites).
- **Downstream (real, confirmed by grep of `CM_EXP_LC_H_ID` usage):** Commercial Invoice (`CM_EXP_COM_INV_HService`), Bill Of Exchange (`CM_EXP_BILL_OF_EX_HService`), L/C UD (`CM_UD_HService`, including a `GetUDAutoComplete(pCM_EXP_LC_H_ID, ...)` lookup), Export LC PI (`CM_EXP_PI_HService`, confirmed via the package's own `CM_EXP_PI_H_SELECT`/`CM_EXP_BILL_OF_EX_PI_PO_REF` joins), Import LC (`CM_IMP_LC_HService`, via `CM_IMP_EXP_LC_MAP`).
- Files matched a `CM_EXP_LC_H_ID` grep but were **not** independently verified this pass: `CM_EXP_BNK_BILL_REAL_HService`, `CmrReportModelService`, `CM_IMP_PI_HService`, `CM_IMP_LC_DService`, `StyleOrderViewService`, `MC_STYLE_HService` — don't cite these as confirmed consumers without reading them directly.

## Gaps

- **`Delete()` calls a non-existent procedure** (`SP_CM_EXP_LC_H`, not `PKG_CM_EXPORT_LC.*`) — confirmed absent from the repo's Oracle sources by grep. Unreachable today (no controller route calls it).
- **Two independent hardcoded-ID bugs**, same shape as the already-documented `CM_NOTIFY_PARTYService.Select` bug: `CM_EXP_LC_D_POService.Select(long ID)` and `CM_LC_APPLICANTService.Select(long ID)` both ignore their own `ID` argument and hardcode `0` instead.
- **Audit-column source inconsistency**: `Save` forces `pCREATED_BY`/`pLAST_UPDATED_BY` from the session; `Update` (revise) takes them from the client-submitted model instead.
- **`UpdatePrc` reuses the "select" pOption convention (3000) for a write call** — inconsistent with this codebase's own 1000/2000/3000 (insert/update/select) convention documented in `docs/09-naming-conventions.md`.
- **`FN_CAN_REVISE` validation is dead code at its only enforcement call site** (commented out inside `CM_EXP_LC_H_REVISE`) even though the function itself is still live-queried by the 3000-select grid to *display* a "can revise" flag — the UI's flag can lie about what the backend will actually allow.
- **Inconsistent duplicate-order-check scope**: the insert procedure skips its "order already attached to another LC" check for amendment-type inserts (`pLC_AMD_TYPE <> 'N'`); the revise procedure runs the identical check unconditionally, with no such exception.
- **Finalization flag only advances on one of two insert branches**: `IS_FINALIZED`/`RF_ACTN_STATUS_ID` are only updated when `pIS_UPDATE='N'`; the `pIS_UPDATE='Y'` branch never touches them.
- **Side effect on `MC_BUYER`**: both insert and revise silently backfill `MC_BUYER.RF_BANK_ID`/`RF_PAYM_TERM_ID`/`PAYMENT_DAYS` from the LC's own params whenever those buyer fields are null — an undocumented cross-module write not mentioned in `docs/features/merchandising-buyer.md`.
- **Dropped filter param**: `GetPaginatedOrderNoDropdown`'s `pMC_ORDER_H_IDS` is accepted by the controller/filter but the corresponding bind is commented out in the service — the multi-order-ID filter never reaches Oracle.
- **Merge-representative list is insert-only**: `CM_EXP_LC_H_MRG_REP_MAP` is written on insert but the corresponding param is commented out of `Update()`, and `CM_EXP_LC_H_REVISE`'s body has no DML for that table either — it can never be changed on an amendment.
- Everything above comes from static source analysis only — no live database connection was available, so nothing here is "DB-verified"; FK claims are corroborated by real JOIN/WHERE usage in the package body.
