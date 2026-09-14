# Table: ACC_REPORT_RECEIVEPAYMENT

```yaml
---
id: tbl:ACC_REPORT_RECEIVEPAYMENT
module: accounting
status: inferred
---
```

Shared physical staging table backing the Receive Payment report (Accounting > Reports > Receive Payment) — despite the name, a Cash & Bank ledger net-movement summary, not a receipt/payment transaction list. Populated by `ACC_VOUCHER_DETAIL` rows for Cash & Bank class accounts, then read back with no filter at all to produce the printed report. The dataset has 15 columns total per the source doc, but only some are individually described; no full column list with names/types exists in source docs.

## Columns

| Column | Type (C#) | Role/Notes | Source |
|---|---|---|---|
| (unnamed) user-id column | — | Exists only to scope the staging table; scoping is broken — cleanup only clears one hardcoded user id, not the actual caller | receive-payment.md |
| (unnamed) company-code column | — | Fetched every run but never displayed; only the company name is shown, looked up separately | receive-payment.md |
| (unnamed) company address column | — | Fetched every run, never printed anywhere on the report | receive-payment.md |
| (unnamed) account name column | — | The specific Cash/Bank sub-ledger account, shown as "Account name" output | receive-payment.md |
| (unnamed) amount column | — | Net Dr−Cr for the account over the period, bucketed to Received/Payment by sign | receive-payment.md |
| (unnamed) group-heading column | — | Account-class grouping (e.g. "Cash in Hand", "Bank Balance") | receive-payment.md |

Of the 15 total columns in the dataset, only these 6 roles are described in the source doc; the remaining ~9 are not named or described at all. No column is given an explicit Oracle/C# name anywhere in source docs — all are described only by role.

## Keys & Indexes

**Primary key:** none defined at the DB level (no `all_constraints` row with `constraint_type='P'`)

**Foreign keys:** none defined at the DB level.

**Indexes:** none found.

*Verified read-only against the dev Oracle DB (`mtexdev`, host `118.67.213.142`) on 2026-09-14 via `ALL_CONSTRAINTS`/`ALL_CONS_COLUMNS`/`ALL_INDEXES`/`ALL_IND_COLUMNS` under schema `MTEX`. No DDL exists in either repo, so this is the only ground truth for keys/indexes.*

## Relationships

`ACC_VOUCHER_DETAIL` (Cash & Bank class accounts only) writes into this shared staging table, which is read back with no filter (not by user, not by company — a known critical bug) to produce the printed report. Confirmed unrelated to Payment Mode or the Bill-settlement sub-flow despite the similar name.

## Feature

[features/receive-payment.md](../features/receive-payment.md)
