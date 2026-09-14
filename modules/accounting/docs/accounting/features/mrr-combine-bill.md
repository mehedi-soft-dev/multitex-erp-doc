# Feature: Mrr Combine Bill

```yaml
---
id: feat:acc-mrr-combine-bill
module: accounting
category: transaction
status: not-implemented
---
```

## Overview

No trace of this screen exists anywhere in this application layer (C# or Angular). The
sibling `MultitechERP` repo has an Oracle package, `PKG_ACC_MRR_BILL_H.sql`, for the
underlying concept — MRR (Material Receiving Report, in garment-manufacturing terms)
combining multiple goods-receipt records into one bill for payment — but no C# or Angular
code anywhere calls it.
