# Feature: Accounting Reports

```yaml
---
id: feat:acc-accounting-reports
module: accounting
category: reports
mvc: AccountingReportController.AccntReportParams
tables: [RF_REPORT, SC_ROLE_REPORT]
status: verified
---
```

## Overview

Accounting Reports (Accounting > Reports > Accounting Reports) is not a navigation hub — it's a single, self-contained "report runner" screen: a radio-button list of report names on the left (permission-filtered per user), a parameter form on the right whose fields show/hide depending on which report is picked, and one Preview button that renders whichever report was chosen as a PDF or Excel file in a new tab. All ~19 reports are implemented inside one server action that switches on a report code — there's no per-report screen behind this one.

No new master table backs this screen — it reads `RF_REPORT` / `SC_ROLE_REPORT` for the menu list, then hits many report procedures.

The report list itself is genuinely role-driven: an ordinary user only sees reports their role has been granted, via a join through the role-report mapping table. But a separate "built-in admin" user type bypasses that join entirely and sees every report in the group, no role check at all.

This explains a puzzle from the route table: several separately-routed report menu states (Control Ledger, Voucher Summary, Voucher Statement, Balance Sheet, Income Statement, Cash Book, Day Book) point at server actions that are commented out and therefore dead. This screen re-implements every one of those same reports itself, end-to-end — strongly suggesting it's the newer, consolidated replacement, and the individually-routed screens are largely abandoned but never removed.

## Fields

A single dynamic form. Selecting a report toggles which of these show:

| Field | Shown for |
|---|---|
| Company | Almost every report except Chart of Account. |
| Main Class / Map Class / Account Head (typeahead) | Ledger-family and Control Ledger reports. |
| Cash Account / Bank Account (restricted dropdowns) | Cash Book / Bank Book only. |
| Bill Status / Bill No | Bill wise Ledger and Bill Status reports. |
| Voucher Posted? | Voucher Statement reports. |
| From/To Date (or From/To Month for the monthly variant) | Almost every report. |
| Voucher For Type / Voucher For | Rendered for every report regardless of selection — only 3 of the ~19 reports actually use these two fields server-side; harmless dead weight for the rest. |
| Export to Excel? | Always visible — switches the output format. |

The Preview button builds a plain HTML form in JavaScript and submits it directly to the server in a new tab — a classic "download via synthetic form" pattern, with no anti-forgery token.

## Relationships

`RF_REPORT` plus a role-mapping table (which reports this user's role can see) builds the radio list. One shared render endpoint switches on the chosen report code and calls one of ~19 dedicated report procedures, which read from Chart of Accounts / Cost Center / Voucher tables.

Reports covered here include Bill wise Ledger, Day Book, Ledger Summary, Bank Reconcile, Monthly Ledger Summary, Bill Status, Subsidiary Ledger, Trial Balance, Chart of Account, Control Ledger, Cash Book, Bank Book, Day Book Detail/Summary, Voucher Statement (detail/summary), Income Statement (detail/summary), and Balance Sheet — each hardcoded as its own case in the render endpoint, not driven by any stored report-definition/SQL, despite the underlying table having columns that look like they were designed for exactly that (see Unused Columns).

## Known Issues

Bugs/inconsistencies found in the current code — not fixed, just recorded.

- **Critical:** The screen-level permission check is commented out entirely — anyone with any active session can open this screen regardless of whether their role has actually been granted it.
- **Critical:** The render endpoint that actually produces every report has no permission check at all, not even a disabled one. It only reads the session for a user id; it never re-validates that the submitted report code is one the user's role was actually granted. In practice, the role-based report list is enforced only on what's displayed in the radio list — a user (or anyone replaying requests with a valid session) can request any report code directly and receive its data, including reports never shown to them.
- **Critical:** The Company parameter is trusted entirely from the submitted form field, not re-validated against the session's actual company assignments — the dropdown itself is correctly scoped, but nothing stops a tampered request from substituting a company id the user isn't assigned to.
- **Critical:** One report the underlying database procedure already implements (a "Ledger Wise Voucher Summary" variant) has no matching case in the server-side switch at all — if that report is ever activated for a role, selecting it in the UI would fail rather than render anything, because the C# side was never updated to match.
- **Warning:** One report (Bank Reconcile) is fully wired up on the server side but has no corresponding parameter-visibility logic on the client — if ever exposed to a role, selecting it would show no input fields at all, and the resulting request would be missing every parameter the report needs.
- **Warning:** The radio-button markup has a copy-paste bug (every button's underlying value is hardcoded to the first report in the list instead of its own) — the screen only works at all because a separate click handler independently sets the real selection, bypassing the broken native radio-button wiring entirely.
- **Warning:** A currency filter field is fully built (flag, form group, parameter) but is never actually triggered by any report selection — permanently unreachable, dead capability distinct from the currency filter that IS used elsewhere on the same form.
- **Minor:** The report group id this screen requests is hardcoded rather than derived from the menu/route — fine for this one screen, but means it can never show a different report group without a code change.
- **Minor:** No anti-forgery token on the Preview submission, combined with the missing permission check above, means this endpoint is reachable via a simple cross-site form submission while a session is active.
- **Minor:** Two separate, differently-keyed "admin bypass" mechanisms exist for report visibility (one on the general menu-permission check, one baked into the report-list query itself) — disabling one does not disable the other.
- **Note (routing):** This whole screen is plain MVC, not Web API — `AccountingReportController` (`Areas\Accounting\Controllers\AccountingReportController.cs`) has no `[RoutePrefix]`/`[Route]`/`[HttpX]` attribute anywhere in the file, so there is no `api:` route to record. The shell is `AccntReportParams()` (`AccountingReportController.cs:521-525`, confirmed by `Views\AccountingReport\AccntReportParams.cshtml:5` hosting `data-ui-view="AccntReportParams"`, matching the `AccntReportParams` ui-router state's own named view in `Client\app\config.accountingRoute.js:14-34`). The render/export workhorse for the ~19 `RPT-25xx` reports is `PreviewReportRDLC(...)` (`AccountingReportController.cs:531`), reached only via conventional `{controller}/{action}` MVC routing from the synthetic form POST described above — not an attribute-routed endpoint.

## Unused Columns

Of the report-definition row's roughly dozen columns, only two are actually used by this screen: the report name (for the radio label) and the report code (which drives the entire client/server switch). Sort order is used only inside the database query and discarded before reaching the client. Several other columns are fetched by the query and then silently discarded in the mapping code, never reaching the screen at all.

The most interesting dead columns: two fields whose names strongly imply the system was designed to let each report row carry its own ad-hoc SQL and parameter definition — i.e. a genuinely data-driven report engine. In the code actually shipped, nothing anywhere ever reads either column; every report is instead hardcoded as its own branch in the server-side switch, calling a dedicated hand-written method and a hardcoded print-template path. The per-user report *list* is real and dynamic; what each report actually *does* is not dynamic at all — that part of the design was apparently never finished.
