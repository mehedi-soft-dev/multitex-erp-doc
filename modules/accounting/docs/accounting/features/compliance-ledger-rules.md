# Feature: Compliance Ledger Rules

```yaml
---
id: feat:acc-compliance-ledger-rules
module: accounting
category: master-data
tables: [ACC_COMPL_LEDGER_PCT_RULE]
status: not-implemented
---
```

## Overview

No screen, route, controller, or API exists for this. But the research surfaced the missing
link behind an already-documented mystery: Voucher's known issues note that
`CP_DR_AMT`/`CP_CR_AMT` ("compliance" debit/credit) columns exist on the voucher line tables
and are accepted by stored procedures, but the main Voucher screen never actually populates
them — a compliance-ledger feature that exists in the schema but is unreachable from that
screen.

This menu is almost certainly the rule-configuration screen that was meant to drive that
feature, and it got further built than "Compliance Vouchers" itself did — just not far
enough to reach a UI. A full Oracle table (`ACC_COMPL_LEDGER_PCT_RULE`: one row per GL
account, storing a compliance percentage) plus complete insert/update/select/delete stored
procedures exist — but are called by nothing anywhere, not even other database procedures.
The one function that would have consumed the rule (computing a compliance amount as a
percentage of the real amount) exists only as commented-out, syntactically incomplete code.

Separately, several GL/financial reports (trial balance, income statement, balance sheet,
sub-ledger) already have a live "compliance mode" toggle that switches from the real DR/CR
columns to the CP_DR_AMT/CP_CR_AMT columns — no percentage rule involved, a straight column
swap. Since those columns are never populated by the Voucher screen, any such
compliance-mode report will always show zero, regardless of what the separate "Compliance
Vouchers" transaction menu turns out to be on inspection.

Net picture: a three-tier abandoned feature — unpopulated columns, an unused rules table
meant to compute them, and live report code that already expects them to be populated. All
three tiers exist only at the database layer.
