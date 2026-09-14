# Feature: Voucher Delete History

```yaml
---
id: feat:acc-voucher-delete-history
module: accounting
category: transaction
tables: [ACC_VOUCHER_MASTER_HIST, ACC_VOUCHER_DETAIL_HIST]
status: not-implemented
---
```

## Overview

The archive tables this screen would presumably show do exist —
`ACC_VOUCHER_MASTER_HIST`/`ACC_VOUCHER_DETAIL_HIST`, already documented on the Voucher
feature page as the tables a voucher gets copied into before a hard delete. But they have
zero read-side references anywhere in the codebase — nothing selects from them, no API
exposes them, no Angular screen displays them. The write side is real; there's simply no
viewer built for it.
