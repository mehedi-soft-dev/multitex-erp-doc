# Feature: Voucher Activity

```yaml
---
id: feat:acc-voucher-activity
module: accounting
category: transaction
status: not-implemented
---
```

## Overview

No dedicated activity-feed or audit table exists for vouchers. The only per-voucher
tracking field found anywhere in the codebase is `ACTN_STS_TRACKER` — a single
workflow-approval-status column, already documented on the Voucher feature page — not an
activity/audit feed showing a history of changes. There is no separate log/audit/tracker
table beyond that one column.
