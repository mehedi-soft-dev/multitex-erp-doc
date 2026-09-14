# Feature: Voucher Post/Unpost

```yaml
---
id: feat:acc-voucher-post-unpost
module: accounting
category: transaction
mvc: AccntController.VoucherPost
api: [GET api/accounting/voucher-masters/get-voucher-masters4post -> VoucherMastersController.GetVoucherMasters4post, POST api/accounting/voucher-masters/post-all-voucher-master -> VoucherMastersController.PostAllVoucherMaster]
tables: [ACC_VOUCHER_MASTER, ACC_VOUCHER_STS]
status: verified
---
```

## Overview

Voucher Post/Unpost is a bulk-action console in Accounting > Transaction > Voucher Post/Unpost. It is layered on top of the same `ACC_VOUCHER_MASTER` table documented on the Voucher page (`ACC_VOUCHER_MASTER` — read + `IS_POSTED` toggle only, no lines table involved). It is **not** a voucher entry form — it never creates, edits, or shows individual voucher lines. It exists purely to flip the `IS_POSTED` flag on already-saved vouchers, in bulk, after they have been keyed in via the Voucher entry screen.

Workflow: filter a list of vouchers, tick checkboxes on one or more rows, then click **Posting** (send to `IS_POSTED='Y'`) or **Un-post** (send back to `IS_POSTED='N'`). Both buttons call the exact same API endpoint, differing only in which value they send.

**Correction to an assumption on the Voucher page:** that page notes there is no reverse unpost/revert-to-draft flow — true for the single-voucher Post button on the Voucher entry screen itself (which hardcodes `IS_POSTED='Y'`, one-way). But **this** screen's bulk endpoint genuinely supports both directions. A real, working Unpost action exists in the product — just only reachable from here, not from the main Voucher screen.

## Fields

Cross-reference Voucher's fields (`../002_voucher/02-fields.md` in the source docs) for the full header/line shape of `ACC_VOUCHER_MASTER` — everything below is specific to this screen's list/filter/bulk-action UI.

| Filter / Column | DB Column | Notes |
|---|---|---|
| Voucher No# / Voucher Reference# | `VOUCHER_NO` / `POST_ID` | Free-text partial match. |
| From/To Date | `POST_DATE` | Defaults to last 20 days only when Voucher#, Ref#, and both dates are ALL blank — a Voucher#-only search with no dates bypasses this fallback entirely. |
| Voucher Type / Trx Source / Company | `VOUCHER_TYPE_ID` / `LK_TRX_SRC_ID` / `HR_COMPANY_ID` | Same dropdowns as Voucher. |
| Posting Status | `IS_POSTED` | Posted (Y) / Un-Posted (N). |
| Select checkbox (per row) | `IS_SELECT` | No disabled state at all — see Known Issues. Only the header select-all checkbox skips already-posted rows. |
| Prepared By | `LOGIN_ID` | Always blank — the query only returns aliased PREPARED_BY/UPDATED_BY, never a plain LOGIN_ID column. See Known Issues. |
| Action column | — | Only Print Voucher is live. Edit/Delete buttons exist in the source but are commented out — this screen deliberately has no edit/delete path. |

| Button | Sends |
|---|---|
| Posting | `pIS_POSTED = 'Y'` |
| Un-post | `pIS_POSTED = 'N'` |

Neither button has a confirmation dialog, a summary of how many vouchers are about to change, or a disabled state when zero rows are checked.

## Relationships

This screen introduces no new tables — it is a pure consumer/mutator of `ACC_VOUCHER_MASTER`, sharing the exact list-fetch endpoint the main Voucher list uses, and the exact PL/SQL procedure the Voucher screen's single-Post button uses (a different branch of the same procedure).

The flow: the Voucher entry screen creates/edits the rows this screen lists. This screen bulk-toggles `IS_POSTED` Y ↔ N on `ACC_VOUCHER_MASTER`. If a workflow tracker exists, the same operation also deletes Management/Audit-approve rows and forces status back to Submit in `ACC_VOUCHER_STS` (workflow history).

Also touches: Print Voucher report (same report as the Voucher screen).

Confirmed: this screen never calls the Voucher entry screen's own single-Post endpoint (which hardcodes Y, one-way) — it exclusively uses the bulk endpoint, which genuinely accepts either direction.

## Known Issues

- **Critical:** Un-post silently destroys the approval audit trail, not just the flag: the same procedure branch runs regardless of Post vs. Un-post direction, and it deletes any Management/Audit-approve workflow history rows for the voucher whenever a tracker existed, forcing the status back to Submit. Reverting a fully-approved, posted voucher back to un-posted also erases the record that it was ever approved, with no way to recover the deleted rows.
- **Critical:** No confirmation dialog, no undo, and no per-row guard against re-toggling: the row checkbox has no disabled state at all (only the select-all header checkbox skips already-posted rows). A user can manually tick an already-posted row and click Un-post, or tick an un-posted row and click Posting again — nothing stops repeatedly toggling any voucher's status, compounding the audit-trail-wiping issue above.
- **Critical:** The bulk toggle has no company/ownership scoping in the write path, unlike the read path: the list query does scope by the calling user's companies, but the actual UPDATE statement has no company check at all. Normal UI use is masked because the client only sends IDs it fetched from the scoped list, but a direct API call with an arbitrary voucher ID from any company would post/unpost it — the same class of gap already documented for Voucher's Delete endpoint.
- **Warning:** No exclusion for vouchers created programmatically by other modules (Bills, Payroll, Export/Import Bill, Fund Request, Store Receive, etc.) — they show up in this list exactly like manually-entered vouchers and can be freely posted/unposted from here, even though those modules manage their own posting lifecycle independently.
- **Warning:** Prepared By is always blank on this screen — the underlying query never returns a plain LOGIN_ID column, only aliased PREPARED_BY/UPDATED_BY, and the C# model has no LOGIN_ID property either. (Affects the main Voucher List screen too, not introduced by this screen, but not previously documented.)
- **Warning:** Misleading success message on a no-op submit: clicking Posting/Un-post with zero rows checked still sends an empty payload, the loop iterates zero times, and the API still returns success — the client shows a success toast even though nothing was posted or unposted.
- **Warning:** Unbounded query possible: searching by Voucher# alone (dates left blank) bypasses the 20-day default-range fallback, and the underlying SQL only requires at least one filter be non-null — can return every matching voucher across all history with no date bound. The bulk-action buttons make an unbounded result set more consequential here than on a read-only list.
- **Minor:** The partial view's own controller action has no permission check of its own — only the full-page action checks menu permission; if the partial URL were ever hit directly rather than through the SPA shell, there is no menu-permission gate on that specific action.

## Unused Columns

This screen reuses `ACC_VOUCHER_MASTER` exactly as already audited on the Voucher page (`../002_voucher/05-unused-columns.md` in the source docs) — that audit stands unchanged. Two screen-specific findings, not previously documented:

| Column returned by the query | Verdict |
|---|---|
| `PERMISSION` | Computed via a function call on every row, never consumed by this screen's grid or logic — a wasted per-row calculation on every page of results. |
| `CAN_ALLOW_WORKFLOW_BTN` | Same pattern — computed via a subquery on every row, never read by this screen's Angular code. |
| `UPDATED_BY` | Returned, never displayed — no Updated By column exists on this screen's grid. |
| `TOTAL_AMT_CP` | Returned, never displayed — consistent with the Voucher page's finding that the compliance DR/CR columns are unreachable from the UI; this screen's grid has no compliance-amount column at all. |
