# Table: ACC_PAYMENT_MODE

```yaml
---
id: tbl:ACC_PAYMENT_MODE
module: accounting
status: inferred
service: PaymentModeService
package: PKG_ACCOUNTING
procedures: [ac_payment_mode_select, ac_payment_mode_select_by_Id, ac_payment_mode_delete]
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [PAYMENT_MODE_ID]
---
```

Payment Mode master — the ways a payment can be made (Cash, Cheque, Bank Transfer, etc.), set up once and then shown as a dropdown anywhere a voucher records how it was paid.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `PAYMENT_MODE_ID` | Number | PK, auto-generated; not shown on screen, used internally to link a voucher to its payment mode | feature doc |
| `PM_NAME` | string | The payment mode's name, e.g. "Cash", "Cheque" | feature doc |
| `REF_CODE` | string | Auto-generated code like `001`, `002`, read-only on the form | feature doc |
| `SHORT_NAME` | string | Short abbreviation for the name | feature doc |
| `REMARKS` | string | Free-text notes | feature doc |
| `COMP_CODE` | string | Company scope, set automatically from the logged-in user; `ac_payment_mode_select` has no `COMP_CODE` filter, so list/search returns every company's payment modes | feature doc |

All 6 columns confirmed in use (`payment-mode.md` Unused Columns audit, confidence: high). No `[Required]`/`[StringLength]` attributes exist on the C# model — validation is browser-only.

## Keys & Indexes

**Primary key:** `PK_PAYMODE_ID` on `PAYMENT_MODE_ID`

**Foreign keys:** none defined at the DB level.

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `PK_PAYMODE_ID` | yes | `PAYMENT_MODE_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

Payment Mode is a lookup table. `ACC_VOUCHER_MASTER` (Voucher and Draft Voucher, shared model) references it via FK `PAYMENT_MODE_ID` to record how a voucher was paid. `ACC_MAP_PAY_MODE` maps Voucher Type → allowed Payment Modes, filtering the dropdown on the Voucher entry screen. `ac_payment_mode_delete` has a known bug: it deletes from `ACC_MAP_PAY_MODE` using `WHERE MAP_PAY_MODE_ID = pPAYMENT_MODE_ID` instead of `WHERE PAYMENT_MODE_ID = pPAYMENT_MODE_ID`, so deleting a payment mode almost never cleans up its `ACC_MAP_PAY_MODE` rows, leaving orphans.

## Feature

[features/payment-mode.md](../features/payment-mode.md)
