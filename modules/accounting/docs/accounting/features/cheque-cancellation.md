# Feature: Cheque Cancellation

```yaml
---
id: feat:acc-cheque-cancellation
module: accounting
category: transaction
status: not-implemented
---
```

## Overview

No cancellation-specific code exists in this repo's application layer. The Oracle sibling
repo's cheque packages (`PKG_ACC_CHQ_ISSUE.sql` / `PKG_ACC_CHQ_BOOK_REG.sql`) likely contain
the underlying cancellation procedures — a cancelled leaf links to a replacement leaf, per
the Cheque Book Registers findings — but nothing in this application calls them.
