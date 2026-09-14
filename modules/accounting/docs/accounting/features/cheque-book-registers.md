# Feature: Cheque Book Registers

```yaml
---
id: feat:acc-cheque-book-registers
module: accounting
category: master-data
tables: [ACC_CHQ_BOOK_REG, ACC_CHQ_BOOK_REG_LEAF]
status: not-implemented
---
```

## Overview

A Cheque Book Register would normally track physical cheque books/leaves issued against a
bank account — book number, leaf range, used/available/cancelled leaf status — feeding the
Cheque Issue and Cheque Cancellation transaction screens. That concept is correct, but none
of it is built here.

What does exist in this repo (a different, narrower feature): the only cheque-related code
is a print action for an already-posted Bank Payment Voucher — a "print cheque leaf" report
opened from the Voucher screen's action menu. It doesn't track cheque books, leaf ranges, or
issuance status at all.

What exists elsewhere (not in this repo): the sibling `MultitechERP` repository's Oracle
packages contain a fully-designed, recently-authored (dated May 2025) database layer for
exactly this feature: header/leaf tables (`ACC_CHQ_BOOK_REG` / `ACC_CHQ_BOOK_REG_LEAF`,
auto-generating one leaf row per cheque number in the registered range) plus a companion
Cheque Issue package with auto-generated reference codes and a cancellation flow that links
a cancelled leaf to its replacement. But even there, no corresponding .NET controller or
Angular screen was found — it appears to be database-layer-only everywhere it exists, and
hasn't been ported into this application at all.
