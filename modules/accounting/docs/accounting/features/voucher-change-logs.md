# Feature: Voucher Change Logs

```yaml
---
id: feat:acc-voucher-change-logs
module: accounting
category: transaction
status: not-implemented
---
```

## Overview

No change-log or audit-trail table exists for voucher edits. The only edit-tracking that
exists anywhere is the generic `LAST_UPDATED_BY`/`LAST_UPDATE_DATE` "last editor" stamp
columns, already documented on the Voucher and Draft Voucher feature pages — simple
overwrite-on-edit stamps, not a history/diff log of what changed.
