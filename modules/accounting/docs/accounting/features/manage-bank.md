# Feature: Manage Bank

```yaml
---
id: feat:acc-manage-bank
module: accounting
category: master-data
status: not-implemented
---
```

## Overview

A "Manage Bank" screen would normally be the master list of the company's own bank accounts
(bank name, branch, account number, account type) referenced by Cheque Issue, Bank
Reconciliation, and voucher payment-mode screens. No such master table or screen exists
anywhere in either repository — no route, controller, API, BLL/Data/Model class, or Oracle
table/package.

Related but distinct features that DO exist — don't confuse these with this menu:

- Bank Reconciliation Vouchers (Transaction menu)
- Bank Book Report

Neither of those has a bank-account master to look values up from, which suggests bank
details entered on those screens are free-text today rather than picked from a managed
list.
