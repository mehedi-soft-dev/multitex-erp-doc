# Feature: Compliance Vouchers

```yaml
---
id: feat:acc-compliance-vouchers
module: accounting
category: transaction
status: not-implemented
---
```

## Overview

The underlying toggle is real in the database, but unreachable from this app. A
`pIS_COMPLIANCE` parameter is genuinely wired throughout the Oracle GL report procedures
(trial balance, income statement, balance sheet, sub-ledger) — when set, those reports read
`CP_DR_AMT`/`CP_CR_AMT` ("compliance" amounts) instead of the normal `DR_AMT`/`CR_AMT`. But
the C# repository methods that call these procedures never supply that parameter, so the
Oracle default always applies and the compliance branch is dead from the app's perspective.

Even if a "Compliance Vouchers" screen were built to flip that toggle, it would show all
zeros today — per the Voucher feature page's known issues, the main Voucher entry screen
never populates `CP_DR_AMT`/`CP_CR_AMT` in the first place. See also Compliance Ledger
Rules for the related dead rules-table story.
