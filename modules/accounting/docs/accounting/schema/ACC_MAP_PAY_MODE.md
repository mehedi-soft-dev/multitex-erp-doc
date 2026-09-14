# Table: ACC_MAP_PAY_MODE

```yaml
---
id: tbl:ACC_MAP_PAY_MODE
module: accounting
status: inferred
# columns: full FK/PK graph data for this table, DB-verified 2026-09-14 (see ## Keys & Indexes below for the raw constraint names).
columns: [PAYMENT_MODE_ID->ACC_PAYMENT_MODE.PAYMENT_MODE_ID, VOUCHERT_TYPE_ID->ACC_VOUCHER_TYPE.VOUCHERTYPEID]
---
```

Mapping table of Voucher Type → allowed Payment Modes; filters the Payment Mode dropdown on the Voucher entry screen, since some payment modes only make sense for certain voucher types.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| `MAP_PAY_MODE_ID` | — | Own surrogate PK, a different ID space from `PAYMENT_MODE_ID` — a known bug in `ac_payment_mode_delete` confuses the two | feature doc |
| `PAYMENT_MODE_ID` | — | FK → `ACC_PAYMENT_MODE` | feature doc |
| `VOUCHERT_TYPE_ID` | Int64 | FK → voucher type (`acc_voucher_type`); column name carries a typo ("VOUCHERT") baked into the schema | `ERP.Data\VoucherMasterRepository.cs:641` (`GetPaymentModes`) |

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Unique constraints:**

| Constraint | Columns |
|---|---|
| `UK_VCRTYPE_PAYMODE_PAYMP` | `VOUCHERT_TYPE_ID`, `PAYMENT_MODE_ID` |

**Foreign keys:**

| Constraint | Column | References |
|---|---|---|
| `FK_PAYMODE_PAYMP` | `PAYMENT_MODE_ID` | `ACC_PAYMENT_MODE.PAYMENT_MODE_ID` |
| `FK_VCHR_TYP_PAYMP` | `VOUCHERT_TYPE_ID` | `ACC_VOUCHER_TYPE.VOUCHERTYPEID` |

**Indexes:**

| Index | Unique? | Columns |
|---|---|---|
| `UK_VCRTYPE_PAYMODE_PAYMP` | yes | `VOUCHERT_TYPE_ID`, `PAYMENT_MODE_ID` |

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_MAP_PAY_MODE` sits between `ACC_PAYMENT_MODE` and the voucher-type lookup (`acc_voucher_type`), filtering which payment modes are offered for a given voucher type on the Voucher entry screen (`VoucherMasterRepository.GetPaymentModes`, joined via `ac_payment_mode_select`/`ac_payment_mode_select_by_Id`'s correlated subqueries). `ac_payment_mode_delete` is supposed to clean up rows here when a payment mode is deleted but targets the wrong key (`MAP_PAY_MODE_ID` instead of `PAYMENT_MODE_ID`), so deletes routinely leave orphaned mapping rows.

## Feature

[features/payment-mode.md](../features/payment-mode.md)
