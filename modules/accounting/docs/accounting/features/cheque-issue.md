# Feature: Cheque Issue

```yaml
---
id: feat:acc-cheque-issue
module: accounting
category: transaction
service: ReportService.GetChequeReport
status: not-implemented
---
```

## Overview

Cheque Issue is a standalone entry screen for issuing a new cheque, but it does not exist
in this application. The only cheque-related code found anywhere is a print action for an
already-created voucher — `ReportService.GetChequeReport`, which renders `acc_cheque_report`
into the `Cheque.rdlc` report — a print button on the Voucher screen, not a standalone entry
screen.

The sibling `MultitechERP` repo has real, recently-authored (May 2025) Oracle packages for
cheque issuance (`PKG_ACC_CHQ_ISSUE.sql`, with header/detail tables and auto-generated
reference codes), but nothing in this application layer calls them. See also Cheque Book
Registers, the master-data screen this would depend on, which has the same story.
