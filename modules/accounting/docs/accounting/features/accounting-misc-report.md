# Feature: Accounting Misc. Report

```yaml
---
id: feat:acc-accounting-misc-report
module: accounting
category: reports
status: not-implemented
---
```

## Overview

Accounting Misc. Report (Accounting > Reports > Accounting Misc. Report) does not exist as an implemented screen. No such screen, route, or backend endpoint exists anywhere in this repository — not in the Angular routes, controllers, services, or repositories, and not even as plain text anywhere in the codebase.

The trail leads to a misleadingly-named file, not a hidden feature. There is an Oracle package file in the sibling repo named `PKG_ACC_MISC_REPORT.sql` — but its actual contents have nothing to do with a "Misc Report." The file's real package name is `PKG_ACC_MRR_BILL_H`, an entirely different, garment-manufacturing-domain feature for booking supplier bills against goods-receipt documents (yarn, dyes/chemicals, needles, oil, fabric-cutting challans). It appears the file was renamed or misfiled at some point in the sibling repo's history.

None of that package's 11 procedures are called from any C# or Angular code in this repository, or from the sibling repo's own application layer. It isn't partially-built scaffolding for a future Misc Report screen — it's a complete, working feature for a completely different purpose that simply happens to share a filename with what this menu entry implies.
